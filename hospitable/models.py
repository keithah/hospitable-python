"""
Data models for Hospitable API responses
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum


# Enums
class Platform(str, Enum):
    """Booking platforms"""
    AIRBNB = "airbnb"
    HOMEAWAY = "homeaway"
    BOOKING = "booking"
    DIRECT = "direct"
    MANUAL = "manual"


class MessageSource(str, Enum):
    """Message sources"""
    PUBLIC_API = "public_api"
    PLATFORM = "platform"
    AI = "AI"
    AUTOMATED = "automated"
    HOSPITABLE = "hospitable"


class ReservationCategory(str, Enum):
    """Reservation status categories"""
    REQUEST = "request"
    ACCEPTED = "accepted"
    CANCELLED = "cancelled"
    NOT_ACCEPTED = "not accepted"
    UNKNOWN = "unknown"
    CHECKPOINT = "checkpoint"


class AvailabilityReason(str, Enum):
    """Calendar availability reasons"""
    RESERVED = "RESERVED"
    AVAILABLE = "AVAILABLE"
    BLOCKED = "BLOCKED"


class ReviewPlatform(str, Enum):
    """Review platforms"""
    AIRBNB = "airbnb"
    DIRECT = "direct"


# Base data models
@dataclass
class Address:
    """Property address"""
    number: str
    street: str
    city: str
    state: str
    country: str
    postcode: str
    coordinates: Dict[str, float]  # {"latitude": float, "longitude": float}
    display: str


@dataclass
class Capacity:
    """Property capacity details"""
    max: Optional[int] = None
    bedrooms: Optional[int] = None
    beds: Optional[float] = None
    bathrooms: Optional[float] = None


@dataclass
class RoomDetail:
    """Room configuration"""
    type: str
    quantity: int


@dataclass
class HouseRules:
    """Property house rules"""
    pets_allowed: bool
    smoking_allowed: bool
    events_allowed: Optional[bool] = None


@dataclass
class Listing:
    """Platform listing information"""
    platform: str
    platform_id: str
    platform_name: Optional[str] = None
    platform_email: Optional[str] = None


@dataclass
class iCalImport:
    """iCal import feed"""
    uuid: str
    url: str
    name: Optional[str]
    host: Dict[str, Optional[str]]  # {"first_name": str, "last_name": str}
    last_sync_at: Optional[datetime]
    disconnected_at: Optional[datetime]


@dataclass
class ParentChild:
    """Parent/child property relationship"""
    type: str  # "parent" or "child"
    parent: Optional[str] = None
    children: Optional[List[str]] = None
    siblings: Optional[List[str]] = None


@dataclass
class Property:
    """Property data model"""
    id: str
    name: str
    public_name: str
    picture: str
    address: Address
    timezone: str
    listed: bool
    amenities: List[str]
    description: str
    summary: str
    check_in: str  # Default check-in time
    check_out: str  # Default check-out time
    currency: str
    capacity: Capacity
    room_details: List[RoomDetail]
    house_rules: HouseRules
    listings: List[Listing]
    tags: List[str]
    property_type: str
    room_type: str
    calendar_restricted: bool
    parent_child: Optional[ParentChild] = None
    ical_imports: Optional[List[iCalImport]] = None


@dataclass
class ReservationStatus:
    """Reservation status details"""
    category: str
    sub_category: str


@dataclass
class ReservationStatusHistory:
    """Reservation status with history"""
    current: ReservationStatus
    history: List[Dict[str, Any]]  # Status changes with timestamps


@dataclass
class GuestCount:
    """Guest count breakdown"""
    total: int
    adult_count: int
    child_count: int
    infant_count: int
    pet_count: int


@dataclass
class Reservation:
    """Reservation data model"""
    id: str
    conversation_id: str
    platform: str
    platform_id: str
    booking_date: datetime
    arrival_date: datetime
    departure_date: datetime
    nights: int
    check_in: datetime
    check_out: datetime
    last_message_at: datetime
    reservation_status: ReservationStatusHistory
    guests: GuestCount
    issue_alert: Optional[str] = None
    stay_type: Optional[str] = None
    # Deprecated field
    status: Optional[str] = None
    status_history: Optional[List[Dict[str, Any]]] = None


@dataclass
class Attachment:
    """Message attachment"""
    type: str  # "image"
    url: str


@dataclass
class Sender:
    """Message sender details"""
    first_name: str
    full_name: str
    locale: str
    picture_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    location: Optional[str] = None


@dataclass
class User:
    """User information"""
    id: str
    email: str
    name: str
    business: bool
    company: Optional[str] = None
    vat: Optional[str] = None
    tax_id: Optional[str] = None
    street_line1: Optional[str] = None
    street_line2: Optional[str] = None
    postal_code: Optional[int] = None
    city: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None


@dataclass
class Message:
    """Message data model"""
    platform: str
    platform_id: int
    conversation_id: str
    content_type: str
    body: str
    sender_type: str
    sender_role: str
    sender: Sender
    created_at: datetime
    source: str
    reservation_id: Optional[str] = None
    attachments: Optional[List[Attachment]] = None
    user: Optional[User] = None
    integration: Optional[str] = None
    sent_reference_id: Optional[str] = None


@dataclass
class Financial:
    """Financial data"""
    amount: int
    formatted: str


@dataclass
class Price:
    """Price information"""
    amount: int
    currency: str
    formatted: str


@dataclass
class AvailabilityStatus:
    """Calendar day availability status"""
    reason: str
    source_type: Optional[str] = None
    source: Optional[str] = None
    available: bool = False


@dataclass
class CalendarDay:
    """Calendar day information"""
    date: str
    day: str
    min_stay: int
    status: AvailabilityStatus
    price: Price
    closed_for_checkin: bool
    closed_for_checkout: bool


@dataclass
class PropertyCalendar:
    """Property calendar data"""
    start_date: str
    end_date: str
    days: List[CalendarDay]


@dataclass
class Guest:
    """Guest information"""
    first_name: str
    last_name: str
    language: Optional[str] = None


@dataclass
class DetailedRating:
    """Detailed review rating"""
    type: str
    rating: int
    comment: str


@dataclass
class PublicReview:
    """Public review information"""
    rating: int
    review: str
    response: str


@dataclass
class PrivateReview:
    """Private review feedback"""
    feedback: str
    detailed_ratings: Optional[List[DetailedRating]] = None


@dataclass
class Review:
    """Review data model"""
    id: str
    platform: str
    public: PublicReview
    private: PrivateReview
    guest: Guest
    responded_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None
    can_respond: bool = False


@dataclass
class PropertySearchPricing:
    """Property search pricing"""
    daily: List[Dict[str, Any]]
    total_without_taxes: Financial
    total: Financial


@dataclass
class PropertySearchAvailability:
    """Property search availability"""
    available: bool
    details: List[Dict[str, Any]]


@dataclass
class PropertySearchResult:
    """Property search result"""
    property: Property
    pricing: PropertySearchPricing
    availability: PropertySearchAvailability
    distance_in_km: int


@dataclass
class PaginationMeta:
    """Pagination metadata"""
    current_page: int
    from_: int  # 'from' is a Python keyword
    last_page: int
    per_page: int
    to: int
    total: int
    links: List[Dict[str, Any]]


@dataclass
class PaginatedResponse:
    """Paginated API response"""
    data: List[Any]
    meta: PaginationMeta


@dataclass
class CalendarUpdateResponse:
    """Calendar update response"""
    status: str


@dataclass
class MessageSendResponse:
    """Message send response"""
    sent_reference_id: str