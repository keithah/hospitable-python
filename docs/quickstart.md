# Quick Start Guide

Get started with the Hospitable Python SDK in minutes.

## Installation

```bash
pip install hospitable-python
```

## Authentication Setup

### Option 1: Personal Access Token (Recommended for testing)

1. Log in to [my.hospitable.com](https://my.hospitable.com)
2. Go to **Apps** → **API access** → **Access tokens**
3. Click **+ Add new** and select permissions
4. Copy your token

```python
from hospitable import HospitableClient

client = HospitableClient(token="your_pat_token_here")
```

### Option 2: OAuth (For production integrations)

```python
client = HospitableClient(
    token="access_token",
    refresh_token="refresh_token",
    client_id="your_vendor_id", 
    client_secret="your_vendor_secret"
)
```

## Basic Usage Examples

### 1. List Your Properties

```python
# Get all properties
properties = client.properties.list()

print(f"Found {len(properties.data)} properties:")
for property in properties.data:
    print(f"- {property.public_name} in {property.address.city}")
    print(f"  Capacity: {property.capacity.max} guests")
    print(f"  Listed: {'Yes' if property.listed else 'No'}")
```

### 2. Get Upcoming Reservations

```python
from datetime import datetime, timedelta

# Get reservations for next 30 days
start_date = datetime.now().strftime("%Y-%m-%d")
end_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

# First, get property UUIDs
properties = client.properties.list()
property_uuids = [p.id for p in properties.data]

# Get reservations
reservations = client.reservations.list(
    properties=property_uuids,
    start_date=start_date,
    end_date=end_date,
    include="guest,properties"
)

print(f"\nUpcoming reservations ({len(reservations.data)}):")
for reservation in reservations.data:
    print(f"- {reservation.platform_id}: {reservation.arrival_date} to {reservation.departure_date}")
    print(f"  Guests: {reservation.guests.total}")
    print(f"  Status: {reservation.reservation_status.current.category}")
```

### 3. Update Property Pricing

```python
from datetime import datetime, timedelta

# Update pricing for a property
property_uuid = properties.data[0].id  # Use first property

# Set pricing for next week
dates_to_update = []
for i in range(7):
    date = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
    dates_to_update.append({
        "date": date,
        "price": {"amount": 15000},  # $150.00 (amount in cents)
        "available": True,
        "min_stay": 2
    })

# Update calendar
result = client.properties.update_calendar(
    uuid=property_uuid,
    dates=dates_to_update
)

print(f"\nCalendar update: {result.status}")
```

### 4. Check Property Calendar

```python
# Get calendar for next month
start_date = datetime.now().strftime("%Y-%m-%d") 
end_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

calendar = client.properties.get_calendar(
    uuid=property_uuid,
    start_date=start_date,
    end_date=end_date
)

print(f"\nCalendar for {property_uuid}:")
for day in calendar.days[:7]:  # Show first 7 days
    status = "Available" if day.status.available else "Blocked"
    print(f"- {day.date} ({day.day}): {day.price.formatted} - {status}")
```

### 5. Send a Message to Guest

```python
# Get a reservation to message
if reservations.data:
    reservation = reservations.data[0]
    
    try:
        response = client.messages.send(
            reservation_uuid=reservation.id,
            body="Hi! Just wanted to confirm your upcoming stay. Looking forward to hosting you!"
        )
        print(f"\nMessage sent! Reference ID: {response.sent_reference_id}")
    except Exception as e:
        print(f"Message sending failed: {e}")
        print("Note: Sending messages requires 'message:write' scope approval")
```

### 6. Handle Property Reviews

```python
# Get reviews for a property
reviews = client.reviews.list(
    property_uuid=property_uuid,
    include="guest",
    per_page=5
)

print(f"\nRecent reviews for property:")
for review in reviews.data:
    print(f"- Rating: {review.public.rating}/5")
    print(f"  Review: {review.public.review[:100]}...")
    print(f"  Guest: {review.guest.first_name} {review.guest.last_name}")
    
    # Respond to review if not already responded
    if review.can_respond and not review.public.response:
        try:
            response_text = f"Thank you {review.guest.first_name}! We're so glad you enjoyed your stay."
            client.reviews.respond(
                review_uuid=review.id,
                response=response_text
            )
            print(f"  ✓ Response posted")
        except Exception as e:
            print(f"  ✗ Response failed: {e}")
```

## Error Handling

```python
from hospitable.exceptions import (
    AuthenticationError,
    RateLimitError, 
    ValidationError,
    NotFoundError
)

try:
    properties = client.properties.list()
except AuthenticationError:
    print("Authentication failed - check your token")
except RateLimitError as e:
    print(f"Rate limited - retry after {e.retry_after} seconds")
except ValidationError as e:
    print(f"Invalid request: {e.message}")
except NotFoundError:
    print("Resource not found")
```

## Advanced Features

### Automatic Token Refresh (OAuth only)

```python
# Client automatically refreshes expired tokens
client = HospitableClient(
    token="access_token",
    refresh_token="refresh_token",
    client_id="vendor_id",
    client_secret="vendor_secret" 
)

# This will auto-refresh if token is expired
properties = client.properties.list()
```

### Pagination Helper

```python
# Get all reservations across all pages
all_reservations = []
page = 1

while True:
    response = client.reservations.list(
        properties=property_uuids,
        page=page,
        per_page=100  # Max per page
    )
    
    all_reservations.extend(response.data)
    
    if page >= response.meta.last_page:
        break
    
    page += 1

print(f"Total reservations: {len(all_reservations)}")
```

### Search Available Properties

```python
# Search for available properties in a location
search_results = client.properties.search(
    start_date="2024-06-01",
    end_date="2024-06-07",
    adults=2,
    children=1,
    location={
        "latitude": 40.7128,   # New York City
        "longitude": -74.0060
    }
)

print(f"Found {len(search_results)} available properties:")
for result in search_results:
    property = result.property
    pricing = result.pricing
    print(f"- {property.public_name}: {pricing.total.formatted}")
    print(f"  Distance: {result.distance_in_km}km")
```

## Configuration

### Environment Variables

```bash
# Set default token in environment
export HOSPITABLE_TOKEN="your_token_here"
```

```python
import os
from hospitable import HospitableClient

# Client will automatically use HOSPITABLE_TOKEN env var
client = HospitableClient()

# Or override with explicit token
client = HospitableClient(token=os.getenv("PROD_HOSPITABLE_TOKEN"))
```

### Custom Base URL (for testing)

```python
client = HospitableClient(
    token="your_token",
    base_url="https://staging.api.hospitable.com/v2"  # Custom URL
)
```

## Next Steps

- Read the [Authentication Guide](authentication.md) for OAuth setup
- Check the [API Reference](api-reference.md) for all available methods
- Set up [Webhooks](webhooks.md) for real-time notifications
- Review [Error Handling](error-handling.md) best practices

## Getting Help

- **Documentation**: [developer.hospitable.com](https://developer.hospitable.com)
- **Platform Team**: team-platform@hospitable.com
- **GitHub Issues**: Report bugs and feature requests

## Example: Complete Property Management Script

```python
#!/usr/bin/env python3
"""
Complete example: Property management automation
"""

from hospitable import HospitableClient
from datetime import datetime, timedelta
import time

def main():
    # Initialize client
    client = HospitableClient(token="your_token_here")
    
    # Get properties
    properties = client.properties.list(include="listings")
    print(f"Managing {len(properties.data)} properties")
    
    for property in properties.data:
        print(f"\n--- {property.public_name} ---")
        
        # Update pricing for next 30 days
        update_pricing(client, property.id)
        
        # Check upcoming reservations
        check_reservations(client, property.id)
        
        # Handle reviews
        handle_reviews(client, property.id)
        
        # Rate limiting - pause between properties
        time.sleep(1)

def update_pricing(client, property_uuid):
    """Update property pricing for next 30 days"""
    dates = []
    base_price = 12000  # $120.00
    
    for i in range(30):
        date = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
        
        # Weekend pricing (Friday-Sunday)
        day_of_week = (datetime.now() + timedelta(days=i)).weekday()
        is_weekend = day_of_week >= 4  # Friday = 4, Saturday = 5, Sunday = 6
        
        price = int(base_price * 1.3) if is_weekend else base_price
        
        dates.append({
            "date": date,
            "price": {"amount": price},
            "available": True,
            "min_stay": 3 if is_weekend else 2
        })
    
    try:
        result = client.properties.update_calendar(property_uuid, dates)
        print(f"  ✓ Calendar updated: {result.status}")
    except Exception as e:
        print(f"  ✗ Calendar update failed: {e}")

def check_reservations(client, property_uuid):
    """Check upcoming reservations"""
    start_date = datetime.now().strftime("%Y-%m-%d")
    end_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    
    reservations = client.reservations.list(
        properties=[property_uuid],
        start_date=start_date,
        end_date=end_date
    )
    
    print(f"  Upcoming reservations: {len(reservations.data)}")
    
    for reservation in reservations.data:
        status = reservation.reservation_status.current.category
        print(f"    {reservation.platform_id}: {status}")

def handle_reviews(client, property_uuid):
    """Check and respond to reviews"""
    reviews = client.reviews.list(property_uuid, per_page=5)
    
    unanswered = [r for r in reviews.data if r.can_respond and not r.public.response]
    
    if unanswered:
        print(f"  {len(unanswered)} reviews need responses")
        
        for review in unanswered:
            try:
                response = f"Thank you {review.guest.first_name}! We appreciate your feedback."
                client.reviews.respond(review.id, response)
                print(f"    ✓ Responded to {review.guest.first_name}'s review")
            except Exception as e:
                print(f"    ✗ Response failed: {e}")

if __name__ == "__main__":
    main()
```