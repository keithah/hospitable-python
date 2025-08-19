# Webhooks

Webhooks provide real-time notifications when events occur in your Hospitable account. All webhooks are sent as POST requests expecting a 200 response.

## Webhook Events

### Available Events

- `reservation.created` - New reservation created
- `reservation.updated` - Reservation status or details changed
- `property.updated` - Property information modified
- `property.merged` - Properties merged
- `message.created` - New message sent or received
- `review.created` - New review received

### Payload Structure

All webhooks contain these fields:

```json
{
  "id": "01GTKD6ZYFVQMR0RWP4HBBHNZC",
  "action": "reservation.created",
  "data": { /* Resource data */ },
  "created": "2023-10-01T09:35:24Z",
  "version": "1.0"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `id` | ULID string | Unique ordered ID for the payload |
| `action` | string | Event type that triggered webhook |
| `data` | object/array | Resource data (same format as GET endpoints) |
| `created` | ISO8601 string | When payload was created |
| `version` | string | Webhook version |

## Configuration

### For Vendors

Configure webhook URLs in your Partner Portal at [partners.hospitable.com](https://partners.hospitable.com):

1. Navigate to Settings
2. Add webhook URLs and select triggers
3. All customer events will be sent to your configured URLs

### For Personal Use

Webhook URLs are configured differently for personal access:
- Contact team-platform@hospitable.com for webhook configuration
- Your webhook secret is your primary email address encoded in base64

## Security

### IP Whitelisting

Webhooks are sent from IP range: `38.80.170.0/24`

Whitelist only this range for enhanced security.

### Signature Verification

Every webhook includes a `Signature` header for verification:

```python
import hmac
import hashlib
import base64

def verify_webhook(payload, signature, secret):
    """Verify webhook signature"""
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected, signature)

# Usage
payload = request.body  # Raw request body
signature = request.headers.get('Signature')

# For vendors: use secret from Partner Portal
# For personal: base64.b64encode(email.encode()).decode()
secret = "your_webhook_secret"

if verify_webhook(payload, signature, secret):
    # Process webhook
    pass
else:
    # Invalid signature
    return 401
```

### Example Implementation

```python
from flask import Flask, request, jsonify
import json

app = Flask(__name__)

@app.route('/webhooks/hospitable', methods=['POST'])
def handle_webhook():
    # Verify signature
    payload = request.get_data(as_text=True)
    signature = request.headers.get('Signature')
    
    if not verify_webhook(payload, signature, WEBHOOK_SECRET):
        return jsonify({'error': 'Invalid signature'}), 401
    
    # Parse webhook data
    webhook_data = json.loads(payload)
    
    # Handle different event types
    action = webhook_data['action']
    data = webhook_data['data']
    
    if action == 'reservation.created':
        handle_new_reservation(data)
    elif action == 'reservation.updated':
        handle_reservation_update(data)
    elif action == 'message.created':
        handle_new_message(data)
    # ... handle other events
    
    return jsonify({'status': 'success'}), 200

def handle_new_reservation(reservation):
    """Process new reservation"""
    print(f"New reservation: {reservation['platform_id']}")
    # Add your business logic here

def handle_reservation_update(reservation):
    """Process reservation update"""
    current_status = reservation['reservation_status']['current']
    print(f"Reservation {reservation['platform_id']} status: {current_status}")

def handle_new_message(message):
    """Process new message"""
    if message['sender_type'] == 'guest':
        print(f"New guest message: {message['body']}")
        # Trigger auto-response logic
```

## Retry Logic

### Automatic Retries

If your endpoint doesn't respond with 200 OK, Hospitable retries:

- **Retry attempts**: Up to 5 times
- **Backoff schedule**: 1s, 5s, 10s, 1hr, 6hr
- **Success condition**: 200 response or exhausted retries

### Handling Retries

Use the webhook `id` to detect and handle duplicate deliveries:

```python
processed_webhooks = set()  # In production, use Redis/database

@app.route('/webhooks/hospitable', methods=['POST'])
def handle_webhook():
    webhook_data = json.loads(request.get_data(as_text=True))
    webhook_id = webhook_data['id']
    
    # Check if already processed
    if webhook_id in processed_webhooks:
        return jsonify({'status': 'already_processed'}), 200
    
    try:
        # Process webhook
        process_webhook(webhook_data)
        
        # Mark as processed
        processed_webhooks.add(webhook_id)
        
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        # Log error but don't mark as processed
        # Hospitable will retry
        logger.error(f"Webhook processing failed: {e}")
        return jsonify({'error': 'Processing failed'}), 500
```

## Testing Webhooks

### Development Environment

Use tools like ngrok for local testing:

```bash
# Expose local server
ngrok http 5000

# Use the HTTPS URL in webhook configuration
# https://abc123.ngrok.io/webhooks/hospitable
```

### Webhook Debugging

For vendors, the Partner Portal provides:
- Webhook delivery logs
- Response codes and errors
- Payload sharing links
- Retry information

## Best Practices

### Endpoint Design

```python
@app.route('/webhooks/hospitable', methods=['POST'])
def handle_webhook():
    # Always return 200 for valid webhooks, even if processing fails
    try:
        webhook_data = json.loads(request.get_data(as_text=True))
        
        # Queue for async processing (recommended)
        queue_webhook_processing.delay(webhook_data)
        
        return jsonify({'status': 'queued'}), 200
    
    except json.JSONDecodeError:
        return jsonify({'error': 'Invalid JSON'}), 400
    except Exception:
        # Log error but return 200 to prevent retries
        logger.exception("Webhook processing error")
        return jsonify({'status': 'error_logged'}), 200
```

### Async Processing

Process webhooks asynchronously to avoid timeouts:

```python
import celery

@celery.task
def process_webhook(webhook_data):
    """Async webhook processing"""
    action = webhook_data['action']
    
    if action == 'reservation.created':
        # Send welcome email
        send_welcome_email(webhook_data['data'])
        
        # Update internal systems
        sync_reservation_to_crm(webhook_data['data'])
        
    elif action == 'message.created':
        # Check for auto-response triggers
        check_auto_response(webhook_data['data'])
```

### Error Handling

```python
def process_webhook_safely(webhook_data):
    """Wrapper for safe webhook processing"""
    try:
        action = webhook_data['action']
        
        handlers = {
            'reservation.created': handle_new_reservation,
            'reservation.updated': handle_reservation_update,
            'message.created': handle_new_message,
            'review.created': handle_new_review,
        }
        
        handler = handlers.get(action)
        if handler:
            handler(webhook_data['data'])
        else:
            logger.warning(f"Unknown webhook action: {action}")
            
    except Exception as e:
        logger.error(f"Webhook processing failed: {e}", extra={
            'webhook_id': webhook_data.get('id'),
            'action': webhook_data.get('action')
        })
```

## Historical Webhooks

Vendors can request historical webhook re-delivery:
- Contact team-platform@hospitable.com
- Specify date range and optional property filter
- Useful for recovering from outages or missed events