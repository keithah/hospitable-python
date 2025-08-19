# API Reference

Complete reference for all Hospitable API endpoints and data structures.

## Client Initialization

```python
from hospitable import HospitableClient

# Personal Access Token
client = HospitableClient(token="your_pat_token")

# OAuth (auto-refresh enabled)
client = HospitableClient(
    token="access_token",
    refresh_token="refresh_token", 
    client_id="vendor_id",
    client_secret="vendor_secret"
)
```

## Properties

### List Properties

```python
properties = client.properties.list(
    include="listings,details",  # Optional relationships
    page=1,                      # Page number
    per_page=10                  # Results per page (max 100)
)

# Returns: PaginatedResponse[Property]
for property in properties.data:
    print(f"{property.name} - {property.address.city}")
```

### Get Property

```python
property = client.properties.get(
    uuid="property-uuid",
    include="listings,user"
)

# Returns: Property
print(f"Property: {property.public_name}")
print(f"Capacity: {property.capacity.max} guests")
```

### Search Properties

Search for available properties with pricing.

```python
results = client.properties.search(
    start_date="2024-08-16",
    end_date="2024-08-20", 
    adults=2,
    children=0,
    infants=0,
    pets=0,
    location={
        "latitude": 40.7128,
        "longitude": -74.0060
    },
    include="details"
)

# Returns: List[PropertySearchResult]
for result in results:
    property = result.property
    pricing = result.pricing
    print(f"{property.name}: ${pricing.total.formatted}")
```

**Requirements:**
- Search up to 3 years in the future
- Maximum 90-day period
- Requires self-hosted Direct site

### Get Property Calendar

```python
calendar = client.properties.get_calendar(
    uuid="property-uuid",
    start_date="2024-03-01",  # Optional
    end_date="2024-03-31"     # Optional
)

# Returns: PropertyCalendar
for day in calendar.days:
    print(f"{day.date}: {day.price.formatted} - {'Available' if day.status.available else 'Blocked'}")
```

### Update Property Calendar

```python
# Update pricing and availability
result = client.properties.update_calendar(
    uuid="property-uuid",
    dates=[
        {
            "date": "2024-03-15",
            "price": {"amount": 15000},  # $150.00 in cents
            "available": True,
            "min_stay": 2,
            "closed_for_checkin": False,
            "closed_for_checkout": False
        },
        {
            "date": "2024-03-16", 
            "available": False  # Block this date
        }
    ]
)

# Returns: CalendarUpdateResponse
print(result.status)  # "accepted"
```

**Limits:**
- Update up to 3 years in the future
- Maximum 60 dates per request
- Rate limit: 1000 requests/minute

## Reservations

### List Reservations

```python
reservations = client.reservations.list(
    properties=["prop-uuid-1", "prop-uuid-2"],  # Required
    start_date="2024-01-01",     # Check-in/out after this date
    end_date="2024-12-31",       # Check-in/out before this date
    include="guest,properties,listings",
    date_query="checkin",        # "checkin" or "checkout"
    platform_id="ABC123",        # Exact reservation code match
    conversation_id="conv-uuid", # Exact conversation match
    page=1,
    per_page=25
)

# Returns: PaginatedResponse[Reservation]
for reservation in reservations.data:
    status = reservation.reservation_status.current
    print(f"{reservation.platform_id}: {status.category}")
```

**Default behavior**: Returns reservations with check-in dates in next 2 weeks if no date parameters provided.

### Get Reservation

```python
reservation = client.reservations.get(
    uuid="reservation-uuid",
    include="guest,properties,financials"
)

# Returns: Reservation
print(f"Reservation: {reservation.platform_id}")
print(f"Guest: {reservation.guests.total} guests")
print(f"Platform: {reservation.platform}")
```

## Messaging

### Get Messages

```python
messages = client.messages.list(
    reservation_uuid="reservation-uuid"
)

# Returns: List[Message]
for message in messages:
    print(f"{message.sender_type}: {message.body}")
    print(f"Source: {message.source}")
```

### Send Message

```python
response = client.messages.send(
    reservation_uuid="reservation-uuid",
    body="Thank you for your booking! Check-in details...",
    images=[
        "https://example.com/check-in-instructions.jpg",
        "https://example.com/welcome-guide.jpg"
    ]  # Optional, max 3 images, 5MB each
)

# Returns: MessageSendResponse
print(f"Message queued with ID: {response.sent_reference_id}")
```

**Rate Limits:**
- 2 messages per minute per reservation
- 50 messages per 5 minutes total

**Requirements:**
- `message:write` scope (requires approval from team-platform@hospitable.com)
- HTML not supported
- `\n` parsed for line breaks

## Reviews

### Get Property Reviews

```python
reviews = client.reviews.list(
    property_uuid="property-uuid",
    include="guest,reservations",
    page=1,
    per_page=20
)

# Returns: PaginatedResponse[Review]
for review in reviews.data:
    print(f"Rating: {review.public.rating}/5")
    print(f"Review: {review.public.review}")
    if review.public.response:
        print(f"Response: {review.public.response}")
```

### Respond to Review

```python
review = client.reviews.respond(
    review_uuid="review-uuid",
    response="Thank you for your kind words! We're so glad you enjoyed your stay."
)

# Returns: Review (updated with response)
print(f"Response posted at: {review.responded_at}")
```

**Limitations:**
- Can only respond once per review
- Must respond within platform's response window
- Requires `reviews:write` scope

## User Information

### Get User Details

```python
user = client.user.get()

# Returns: User
print(f"User: {user.name} ({user.email})")
print(f"Business: {user.business}")
print(f"Company: {user.company}")
```

## Data Models

### Property

```python
@dataclass
class Property:
    id: str                    # UUID
    name: str                  # Internal name
    public_name: str           # Public-facing name
    picture: str               # Image URL
    address: Address           # Full address with coordinates
    timezone: str              # Timezone offset
    listed: bool               # Is property listed
    amenities: List[str]       # Available amenities
    description: str           # Property description
    summary: str               # Short summary
    check_in: str              # Default check-in time
    check_out: str             # Default check-out time
    currency: str              # Currency code
    capacity: Capacity         # Guest capacity details
    room_details: List[Room]   # Room configuration
    house_rules: HouseRules    # Property rules
    listings: List[Listing]    # Platform listings (requires scope)
    tags: List[str]            # Property tags
    property_type: str         # Property type
    room_type: str             # Room type
    calendar_restricted: bool  # Can calendar be updated via API
    parent_child: Optional[ParentChild]  # Parent/child relationship
```

### Reservation

```python
@dataclass
class Reservation:
    id: str                           # UUID
    conversation_id: str              # Conversation UUID
    platform: Platform               # airbnb, homeaway, booking, direct, manual
    platform_id: str                 # Reservation code
    booking_date: datetime            # When booked
    arrival_date: datetime            # Check-in date
    departure_date: datetime          # Check-out date
    nights: int                       # Number of nights
    check_in: datetime                # Exact check-in time
    check_out: datetime               # Exact check-out time
    last_message_at: datetime         # Last message timestamp
    reservation_status: ReservationStatus  # Current status and history
    guests: GuestCount                # Guest breakdown
    issue_alert: Optional[str]        # Any detected issues
    stay_type: StayType               # guest_stay or owner_stay
```

### Message

```python
@dataclass  
class Message:
    platform: str                    # Platform name
    platform_id: int                 # Platform message ID
    conversation_id: str              # Conversation UUID
    reservation_id: Optional[str]     # Reservation UUID if applicable
    content_type: str                 # MIME type
    body: str                         # Message text
    attachments: List[Attachment]     # Image attachments
    sender_type: str                  # host or guest
    sender_role: str                  # host, co-host, teammate
    sender: Sender                    # Sender details
    user: Optional[User]              # User details
    created_at: datetime              # Message timestamp
    source: MessageSource             # Origin of message
    integration: Optional[str]        # Integration name if applicable
    sent_reference_id: Optional[str]  # Send reference ID
```

### Reservation Status

```python
@dataclass
class ReservationStatus:
    current: StatusDetail             # Current status
    history: List[StatusHistory]      # Status change history

@dataclass
class StatusDetail:
    category: str     # request, accepted, cancelled, not accepted, unknown, checkpoint
    sub_category: str # More specific status within category
```

**Status Categories:**
- `request` - Pending approval
- `accepted` - Confirmed booking  
- `cancelled` - Cancelled reservation
- `not accepted` - Declined request
- `checkpoint` - Verification required
- `unknown` - Unknown/broken state

### Calendar Day

```python
@dataclass
class CalendarDay:
    date: str                    # YYYY-MM-DD
    day: str                     # Day of week
    min_stay: int                # Minimum nights
    status: AvailabilityStatus   # Availability details
    price: Price                 # Pricing information
    closed_for_checkin: bool     # Check-in allowed
    closed_for_checkout: bool    # Check-out allowed

@dataclass
class AvailabilityStatus:
    reason: str                  # RESERVED, AVAILABLE, BLOCKED
    source_type: Optional[str]   # Source of availability
    source: Optional[str]        # Platform name
    available: bool              # Is date available
```

## Error Handling

### Exception Types

```python
from hospitable.exceptions import (
    HospitableError,        # Base exception
    AuthenticationError,    # 401 - Invalid token
    ForbiddenError,         # 403 - Insufficient permissions  
    NotFoundError,          # 404 - Resource not found
    ValidationError,        # 400 - Invalid request
    RateLimitError,         # 429 - Rate limit exceeded
    ServerError            # 5xx - Server errors
)

try:
    properties = client.properties.list()
except AuthenticationError:
    # Refresh token or re-authenticate
    client.refresh_token()
except RateLimitError as e:
    # Wait before retrying
    time.sleep(e.retry_after or 60)
except ValidationError as e:
    # Fix request parameters
    print(f"Invalid request: {e.message}")
```

### Rate Limit Handling

```python
from hospitable.exceptions import RateLimitError
import time

def safe_api_call(func, *args, **kwargs):
    """Wrapper for API calls with rate limit handling"""
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except RateLimitError as e:
            if attempt == max_retries - 1:
                raise
            wait_time = e.retry_after or (2 ** attempt)
            time.sleep(wait_time)
    
# Usage
properties = safe_api_call(client.properties.list, page=1)
```

## Pagination

All list endpoints return paginated results:

```python
# Manual pagination
page = 1
all_reservations = []

while True:
    response = client.reservations.list(
        properties=["prop-uuid"],
        page=page,
        per_page=100
    )
    
    all_reservations.extend(response.data)
    
    if page >= response.meta.last_page:
        break
    
    page += 1

# Using built-in pagination helper
all_reservations = list(client.reservations.list_all(
    properties=["prop-uuid"],
    per_page=100
))
```

## Including Related Data

Use `include` parameter to fetch related resources:

```python
# Single include
properties = client.properties.list(include="listings")

# Multiple includes
reservations = client.reservations.list(
    properties=["prop-uuid"],
    include="guest,properties,financials,listings"
)

# Available includes by endpoint:
# Properties: user, listings, details, bookings
# Reservations: guest, user, financials, listings, properties, review
# Reviews: guest, reservations
```