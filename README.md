# Hospitable Python SDK

[![PyPI version](https://badge.fury.io/py/hospitable-python.svg)](https://badge.fury.io/py/hospitable-python)
[![Python Support](https://img.shields.io/pypi/pyversions/hospitable-python.svg)](https://pypi.org/project/hospitable-python/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive Python SDK for the [Hospitable Public API v2](https://developer.hospitable.com/docs/public-api-docs/). Manage vacation rental properties, reservations, calendars, guest messaging, and reviews programmatically.

## Features

- **🏠 Property Management**: List, search, and manage vacation rental properties
- **📅 Calendar Management**: Update pricing and availability with rate limiting
- **📋 Reservations**: Access booking data across all connected platforms  
- **💬 Guest Messaging**: Send and receive messages with automatic rate limiting
- **⭐ Reviews**: Access and respond to guest reviews
- **🔄 Webhooks**: Real-time event notifications
- **🔐 Authentication**: Support for both Personal Access Tokens and OAuth 2.0
- **⚡ Auto-retry**: Automatic retry with exponential backoff for failed requests
- **🛡️ Error Handling**: Comprehensive error handling with custom exceptions

## Installation

```bash
pip install hospitable-python
```

## Quick Start

### Authentication

#### Personal Access Token (Recommended for testing)

1. Log in to [my.hospitable.com](https://my.hospitable.com)
2. Go to **Apps** → **API access** → **Access tokens** 
3. Click **+ Add new** and select permissions
4. Copy your token

```python
from hospitable import HospitableClient

# Option 1: Pass token directly
client = HospitableClient(token="your_pat_token_here")

# Option 2: Use environment variable
# Set HOSPITABLE_PAT=your_token_here in your environment or .env file
client = HospitableClient()
```

**Environment Variables:**
- `HOSPITABLE_PAT`: Personal Access Token (preferred)
- `HOSPITABLE_TOKEN`: Access token (fallback for backward compatibility)

#### OAuth 2.0 (For production integrations)

```python
client = HospitableClient(
    token="access_token",
    refresh_token="refresh_token",
    client_id="your_vendor_id",
    client_secret="your_vendor_secret"
)
```

### Basic Usage

```python
# Get all properties
properties = client.properties.list()
print(f"Found {len(properties.data)} properties")

# Get upcoming reservations
property_uuids = [p.id for p in properties.data]
reservations = client.reservations.list(
    properties=property_uuids,
    start_date="2024-01-01",
    end_date="2024-12-31",
    include="guest,properties"
)

# Update calendar pricing
client.properties.update_calendar("property-uuid", [
    {
        "date": "2024-03-15",
        "price": {"amount": 15000},  # $150.00 in cents
        "available": True,
        "min_stay": 2
    }
])

# Send a message to a guest
client.messages.send(
    reservation_uuid="reservation-uuid",
    body="Hi! Looking forward to hosting you next week!"
)

# Respond to a review
client.reviews.respond(
    review_uuid="review-uuid", 
    response="Thank you for the wonderful review!"
)
```

### JWT Token Management

If you're using a Personal Access Token (JWT), the SDK automatically parses token information:

```python
from hospitable import HospitableClient, parse_jwt

# Initialize client with JWT token
client = HospitableClient()

# Get JWT information
jwt_info = client.get_token_info()
if jwt_info:
    print(f"Token expires: {jwt_info.expires_at}")
    print(f"Time until expiry: {jwt_info.time_until_expiry}")
    print(f"Has read access: {jwt_info.has_read_access()}")
    print(f"Has write access: {jwt_info.has_write_access()}")
    print(f"Scopes: {', '.join(jwt_info.scopes)}")

# Parse JWT directly
jwt_info = parse_jwt("your_jwt_token_here")
print(f"User ID: {jwt_info.user_id}")
print(f"Is expired: {jwt_info.is_expired}")
```

## API Reference

### Properties

```python
# List properties with pagination
properties = client.properties.list(
    include="listings,details",
    page=1,
    per_page=50
)

# Get specific property
property = client.properties.get("property-uuid", include="listings")

# Search available properties
results = client.properties.search(
    start_date="2024-06-01",
    end_date="2024-06-07", 
    adults=2,
    children=1,
    location={"latitude": 40.7128, "longitude": -74.0060}
)

# Get calendar
calendar = client.properties.get_calendar(
    "property-uuid",
    start_date="2024-03-01",
    end_date="2024-03-31"
)

# Update calendar (rate limited: 1000 req/min)
client.properties.update_calendar("property-uuid", [
    {"date": "2024-03-15", "price": {"amount": 15000}, "available": True}
])
```

### Reservations

```python
# List reservations
reservations = client.reservations.list(
    properties=["prop-uuid-1", "prop-uuid-2"],
    start_date="2024-01-01",
    end_date="2024-12-31",
    include="guest,properties,financials"
)

# Get specific reservation  
reservation = client.reservations.get("reservation-uuid", include="guest")
```

### Messages

```python
# Get messages for a reservation
messages = client.messages.list("reservation-uuid")

# Send message (rate limited: 2/min per reservation, 50/5min global)
response = client.messages.send(
    "reservation-uuid",
    "Your check-in instructions...",
    images=["https://example.com/instructions.jpg"]  # Optional
)
```

### Reviews

```python
# Get property reviews
reviews = client.reviews.list("property-uuid", include="guest")

# Respond to review
review = client.reviews.respond(
    "review-uuid",
    "Thank you for staying with us!"
)
```

### User

```python
# Get authenticated user info
user = client.user.get()
print(f"User: {user.name} ({user.email})")
```

## Error Handling

```python
from hospitable.exceptions import (
    AuthenticationError,
    RateLimitError,
    ValidationError,
    NotFoundError,
    ForbiddenError
)

try:
    properties = client.properties.list()
except AuthenticationError:
    print("Invalid token or expired")
except RateLimitError as e:
    print(f"Rate limited - retry after {e.retry_after} seconds")
except ValidationError as e:
    print(f"Invalid request: {e.message}")
except NotFoundError:
    print("Resource not found")
except ForbiddenError:
    print("Insufficient permissions")
```

## Rate Limiting

The SDK automatically handles rate limits with exponential backoff:

- **Calendar updates**: 1000 requests/minute
- **Message sending**: 2/minute per reservation, 50/5 minutes globally  
- **Other endpoints**: Contact Hospitable support for limits

```python
# Rate limits are handled automatically
for property_uuid in property_uuids:
    client.properties.update_calendar(property_uuid, calendar_data)
    # SDK automatically pauses if rate limited
```

## Webhooks

Set up webhooks for real-time notifications:

```python
import hmac
import hashlib

def verify_webhook(payload, signature, secret):
    expected = hmac.new(
        secret.encode(),
        payload.encode(), 
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)

# Handle webhook events
webhook_data = {
    "id": "01GTKD6ZYFVQMR0RWP4HBBHNZC",
    "action": "reservation.created", 
    "data": {...},  # Full reservation object
    "created": "2023-10-01T09:35:24Z",
    "version": "1.0"
}
```

Available webhook events:
- `reservation.created` / `reservation.updated`
- `property.updated` / `property.merged` 
- `message.created`
- `review.created`

## Configuration

### Environment Variables

```bash
export HOSPITABLE_TOKEN="your_token_here"
```

```python
# Client automatically uses HOSPITABLE_TOKEN
client = HospitableClient()
```

### Custom Configuration

```python
client = HospitableClient(
    token="your_token",
    base_url="https://staging.api.hospitable.com/v2",  # Custom API URL
    timeout=30,        # Request timeout
    max_retries=3,     # Max retry attempts
    auto_refresh=True  # Auto-refresh OAuth tokens
)
```

## Development

### Setup

```bash
git clone https://github.com/your-username/hospitable-python.git
cd hospitable-python
pip install -e ".[dev]"
```

### Testing

```bash
pytest tests/
pytest --cov=hospitable tests/  # With coverage
```

### Code Formatting

```bash
black hospitable/
flake8 hospitable/
mypy hospitable/
```

## API Version Support

- **Current**: v2 (recommended)
- **Deprecated**: v1 (sunset: February 3rd, 2025)

The SDK uses API v2 endpoints exclusively.

## Requirements

- Python 3.8+
- `requests` library

## Documentation

- [📚 Full Documentation](docs/README.md)
- [🚀 Quick Start Guide](docs/quickstart.md)
- [🔐 Authentication Guide](docs/authentication.md)
- [📡 Webhooks Guide](docs/webhooks.md)
- [⚡ Rate Limits Guide](docs/rate-limits.md)
- [🌐 Official API Docs](https://developer.hospitable.com/docs/public-api-docs/)

## Support

- **Email**: team-platform@hospitable.com
- **Issues**: [GitHub Issues](https://github.com/your-username/hospitable-python/issues)
- **API Status**: [Hospitable Status Page](https://status.hospitable.com)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### v0.1.0 (2024-01-01)
- Initial release
- Support for all Hospitable API v2 endpoints
- OAuth 2.0 and Personal Access Token authentication
- Automatic rate limiting and retry logic
- Comprehensive error handling
- Full webhook support