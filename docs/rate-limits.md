# Rate Limits

The Hospitable API implements rate limiting to ensure fair usage and system stability. Different endpoints have different limits.

## Endpoint-Specific Limits

### Calendar Updates
- **Limit**: 1000 requests per minute
- **Endpoint**: `PUT /properties/{uuid}/calendar`
- **Scope**: Per access token

### Message Sending
- **Per Reservation**: 2 messages per minute
- **Global**: 50 messages per 5 minutes
- **Endpoint**: `POST /reservations/{uuid}/messages`

### General API
- **Default**: Contact support for specific limits
- **Varies by**: Endpoint and access pattern

## Rate Limit Headers

API responses include rate limit information:

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
Retry-After: 60
```

| Header | Description |
|--------|-------------|
| `X-RateLimit-Limit` | Total requests allowed in window |
| `X-RateLimit-Remaining` | Requests remaining in current window |
| `X-RateLimit-Reset` | Unix timestamp when window resets |
| `Retry-After` | Seconds to wait before retrying (429 only) |

## Handling Rate Limits

### Automatic Handling

The SDK automatically handles rate limits:

```python
from hospitable import HospitableClient

client = HospitableClient(token="your_token")

# SDK automatically retries with exponential backoff
properties = client.properties.list()
```

### Manual Handling

```python
from hospitable.exceptions import RateLimitError
import time

def safe_api_call(func, *args, **kwargs):
    """Wrapper for API calls with rate limit handling"""
    max_retries = 3
    base_delay = 1
    
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except RateLimitError as e:
            if attempt == max_retries - 1:
                raise  # Re-raise after final attempt
            
            # Use Retry-After header if available
            delay = e.retry_after or (base_delay * (2 ** attempt))
            print(f"Rate limited. Waiting {delay} seconds...")
            time.sleep(delay)
        except Exception:
            raise  # Don't retry other errors

# Usage
try:
    properties = safe_api_call(client.properties.list)
except RateLimitError:
    print("Still rate limited after retries")
```

### Checking Rate Limits

```python
import requests

def check_rate_limits(client):
    """Check current rate limit status"""
    try:
        response = client._make_request("GET", "/user")
        
        limit = response.headers.get('X-RateLimit-Limit')
        remaining = response.headers.get('X-RateLimit-Remaining')
        reset_time = response.headers.get('X-RateLimit-Reset')
        
        if limit and remaining:
            print(f"Rate limit: {remaining}/{limit} remaining")
            
            if int(remaining) < 10:
                print("Warning: Approaching rate limit")
                
    except Exception as e:
        print(f"Could not check rate limits: {e}")

# Check before making many requests
check_rate_limits(client)
```

## Best Practices

### 1. Implement Exponential Backoff

```python
import time
import random

def exponential_backoff_retry(func, max_retries=3):
    """Retry with exponential backoff and jitter"""
    for attempt in range(max_retries):
        try:
            return func()
        except RateLimitError as e:
            if attempt == max_retries - 1:
                raise
            
            # Exponential backoff with jitter
            base_delay = 2 ** attempt
            jitter = random.uniform(0, 1)
            delay = base_delay + jitter
            
            # Respect Retry-After if provided
            if e.retry_after:
                delay = max(delay, e.retry_after)
            
            time.sleep(delay)
```

### 2. Batch Operations

```python
def batch_calendar_updates(client, property_uuid, all_dates):
    """Update calendar in batches to respect rate limits"""
    batch_size = 60  # Max dates per request
    
    for i in range(0, len(all_dates), batch_size):
        batch = all_dates[i:i + batch_size]
        
        try:
            result = client.properties.update_calendar(
                uuid=property_uuid,
                dates=batch
            )
            print(f"Updated batch {i//batch_size + 1}: {result.status}")
            
            # Small delay between batches
            time.sleep(0.1)
            
        except RateLimitError:
            print(f"Rate limited on batch {i//batch_size + 1}")
            time.sleep(60)  # Wait 1 minute
            
            # Retry this batch
            client.properties.update_calendar(
                uuid=property_uuid,
                dates=batch
            )
```

### 3. Respect Message Rate Limits

```python
from datetime import datetime, timedelta
import time

class MessageRateLimiter:
    def __init__(self):
        self.reservation_messages = {}  # Track per-reservation timing
        self.global_messages = []       # Track global timing
    
    def can_send_message(self, reservation_uuid):
        """Check if message can be sent to reservation"""
        now = datetime.now()
        
        # Check per-reservation limit (2/minute)
        if reservation_uuid in self.reservation_messages:
            last_messages = self.reservation_messages[reservation_uuid]
            recent = [t for t in last_messages if now - t < timedelta(minutes=1)]
            
            if len(recent) >= 2:
                return False, "Per-reservation rate limit (2/minute)"
        
        # Check global limit (50/5 minutes)
        recent_global = [t for t in self.global_messages if now - t < timedelta(minutes=5)]
        if len(recent_global) >= 50:
            return False, "Global rate limit (50/5 minutes)"
        
        return True, None
    
    def record_message(self, reservation_uuid):
        """Record message sending"""
        now = datetime.now()
        
        # Record per-reservation
        if reservation_uuid not in self.reservation_messages:
            self.reservation_messages[reservation_uuid] = []
        self.reservation_messages[reservation_uuid].append(now)
        
        # Record global
        self.global_messages.append(now)
        
        # Cleanup old entries
        cutoff_1min = now - timedelta(minutes=1)
        cutoff_5min = now - timedelta(minutes=5)
        
        self.reservation_messages[reservation_uuid] = [
            t for t in self.reservation_messages[reservation_uuid] 
            if t > cutoff_1min
        ]
        
        self.global_messages = [
            t for t in self.global_messages 
            if t > cutoff_5min
        ]

def send_message_with_rate_limiting(client, reservation_uuid, body):
    """Send message respecting rate limits"""
    limiter = MessageRateLimiter()
    
    can_send, reason = limiter.can_send_message(reservation_uuid)
    
    if not can_send:
        print(f"Cannot send message: {reason}")
        return None
    
    try:
        response = client.messages.send(reservation_uuid, body)
        limiter.record_message(reservation_uuid)
        return response
    except RateLimitError as e:
        print(f"Rate limited: {e.message}")
        return None
```

### 4. Monitor Rate Limit Usage

```python
from collections import defaultdict
from datetime import datetime, timedelta

class RateLimitMonitor:
    def __init__(self):
        self.request_counts = defaultdict(list)
        self.rate_limit_hits = []
    
    def record_request(self, endpoint):
        """Record API request"""
        now = datetime.now()
        self.request_counts[endpoint].append(now)
        
        # Clean old entries (keep 1 hour)
        cutoff = now - timedelta(hours=1)
        self.request_counts[endpoint] = [
            t for t in self.request_counts[endpoint] 
            if t > cutoff
        ]
    
    def record_rate_limit_hit(self, endpoint):
        """Record rate limit hit"""
        self.rate_limit_hits.append({
            'endpoint': endpoint,
            'timestamp': datetime.now()
        })
    
    def get_usage_stats(self):
        """Get usage statistics"""
        now = datetime.now()
        
        stats = {}
        for endpoint, timestamps in self.request_counts.items():
            # Requests in last hour
            hour_ago = now - timedelta(hours=1)
            recent = [t for t in timestamps if t > hour_ago]
            
            stats[endpoint] = {
                'requests_last_hour': len(recent),
                'requests_per_minute': len(recent) / 60
            }
        
        # Rate limit hits in last hour
        hour_ago = now - timedelta(hours=1)
        recent_hits = [
            hit for hit in self.rate_limit_hits 
            if hit['timestamp'] > hour_ago
        ]
        
        stats['rate_limit_hits_last_hour'] = len(recent_hits)
        
        return stats

# Usage
monitor = RateLimitMonitor()

def monitored_api_call(client, func_name, *args, **kwargs):
    """Wrapper to monitor API calls"""
    monitor.record_request(func_name)
    
    try:
        func = getattr(client, func_name.split('.')[0])
        method = getattr(func, func_name.split('.')[1])
        return method(*args, **kwargs)
    except RateLimitError:
        monitor.record_rate_limit_hit(func_name)
        raise

# Example usage
try:
    properties = monitored_api_call(client, 'properties.list')
except RateLimitError:
    stats = monitor.get_usage_stats()
    print(f"Usage stats: {stats}")
```

### 5. Calendar Update Optimization

```python
def optimize_calendar_updates(client, property_uuid, updates):
    """Optimize calendar updates for rate limits"""
    
    # Group updates by date proximity
    def group_dates(dates, max_gap_days=7):
        """Group dates that are close together"""
        sorted_dates = sorted(dates, key=lambda x: x['date'])
        groups = []
        current_group = []
        
        for date_update in sorted_dates:
            if not current_group:
                current_group.append(date_update)
            else:
                last_date = datetime.strptime(current_group[-1]['date'], '%Y-%m-%d')
                current_date = datetime.strptime(date_update['date'], '%Y-%m-%d')
                
                if (current_date - last_date).days <= max_gap_days:
                    current_group.append(date_update)
                else:
                    groups.append(current_group)
                    current_group = [date_update]
        
        if current_group:
            groups.append(current_group)
        
        return groups
    
    # Group and batch updates
    date_groups = group_dates(updates)
    
    for group_idx, group in enumerate(date_groups):
        # Further split into batches of 60
        for batch_idx in range(0, len(group), 60):
            batch = group[batch_idx:batch_idx + 60]
            
            try:
                result = client.properties.update_calendar(
                    uuid=property_uuid,
                    dates=batch
                )
                print(f"Group {group_idx + 1}, Batch {batch_idx//60 + 1}: {result.status}")
                
                # Respect rate limits - max 1000/minute = ~16/second
                time.sleep(0.1)  # Small delay between requests
                
            except RateLimitError:
                print(f"Rate limited, waiting 60 seconds...")
                time.sleep(60)
                
                # Retry batch
                result = client.properties.update_calendar(
                    uuid=property_uuid,
                    dates=batch
                )
                print(f"Retry successful: {result.status}")
```

## Error Recovery

### Graceful Degradation

```python
def robust_property_sync(client, property_data):
    """Sync property data with graceful degradation"""
    
    # Critical operations (try multiple times)
    critical_ops = [
        ('calendar_update', lambda: update_property_calendar(client, property_data)),
        ('reservation_sync', lambda: sync_reservations(client, property_data))
    ]
    
    # Non-critical operations (try once)
    optional_ops = [
        ('review_responses', lambda: respond_to_reviews(client, property_data)),
        ('message_guests', lambda: send_guest_messages(client, property_data))
    ]
    
    results = {'critical': {}, 'optional': {}}
    
    # Critical operations with retry
    for op_name, op_func in critical_ops:
        for attempt in range(3):
            try:
                result = op_func()
                results['critical'][op_name] = {'success': True, 'result': result}
                break
            except RateLimitError as e:
                if attempt < 2:
                    time.sleep(e.retry_after or 60)
                else:
                    results['critical'][op_name] = {'success': False, 'error': str(e)}
            except Exception as e:
                results['critical'][op_name] = {'success': False, 'error': str(e)}
                break
    
    # Optional operations (single attempt)
    for op_name, op_func in optional_ops:
        try:
            result = op_func()
            results['optional'][op_name] = {'success': True, 'result': result}
        except RateLimitError as e:
            results['optional'][op_name] = {'success': False, 'error': 'Rate limited', 'retry_after': e.retry_after}
        except Exception as e:
            results['optional'][op_name] = {'success': False, 'error': str(e)}
    
    return results
```

## Monitoring and Alerting

```python
import logging

class RateLimitLogger:
    def __init__(self):
        self.logger = logging.getLogger('hospitable.rate_limits')
        self.logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def log_rate_limit(self, endpoint, retry_after=None):
        """Log rate limit hits"""
        message = f"Rate limit hit on {endpoint}"
        if retry_after:
            message += f" (retry after {retry_after}s)"
        
        self.logger.warning(message)
    
    def log_high_usage(self, endpoint, usage_percent):
        """Log high API usage"""
        if usage_percent > 80:
            self.logger.warning(
                f"High API usage on {endpoint}: {usage_percent}%"
            )

# Integration with client
rate_limit_logger = RateLimitLogger()

def logged_api_call(client, method_name, *args, **kwargs):
    """API call wrapper with rate limit logging"""
    try:
        return getattr(client, method_name)(*args, **kwargs)
    except RateLimitError as e:
        rate_limit_logger.log_rate_limit(method_name, e.retry_after)
        raise
```