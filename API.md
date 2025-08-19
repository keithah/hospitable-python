# Hospitable API Documentation

## Overview

The Hospitable Public API v2 allows you to manage vacation rental properties, reservations, calendars, guest messaging, and reviews programmatically. The API follows REST architectural standards and uses OAuth 2.0 for authentication.

**Base URL:** `https://public.api.hospitable.com/v2`

## Authentication

The API uses Bearer token authentication. You need to generate a Personal Access Token (PAT) from your Hospitable account.

### Generating a Personal Access Token

1. Log in to [my.hospitable.com](https://my.hospitable.com)
2. Click **Apps** in the sidebar
3. Choose **API access**
4. In the **Access tokens** tab, click **+ Add new**
5. Name your access token and select permissions:
   - **Read**: View property, reservation, and calendar information
   - **Write**: Modify calendar pricing and availability

### Using the Token

Include the token in the `Authorization` header of all requests:

```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

## Core Resources

### Properties

Properties represent your vacation rental listings.

#### Endpoints

- `GET /properties` - List all properties
- `GET /properties/{uuid}` - Get a specific property
- `GET /properties/search` - Search properties with availability
- `GET /properties/{uuid}/calendar` - Get property calendar
- `PUT /properties/{uuid}/calendar` - Update calendar pricing/availability

#### Key Fields

- `id` - Unique property identifier
- `name` - Internal property name
- `public_name` - Public-facing property name
- `address` - Full address details with coordinates
- `capacity` - Guest capacity and room details
- `listings` - Connected platform listings (Airbnb, Vrbo, etc.)
- `calendar_restricted` - Whether calendar can be updated via API

### Reservations

Reservations represent bookings across all connected platforms.

#### Endpoints

- `GET /reservations` - List reservations
- `GET /reservations/{uuid}` - Get a specific reservation

#### Key Fields

- `id` - Unique reservation identifier
- `platform` - Booking source (airbnb, homeaway, booking, direct, manual)
- `platform_id` - Reservation code on the platform
- `arrival_date` / `departure_date` - Stay dates
- `check_in` / `check_out` - Exact check-in/out times
- `guests` - Guest counts by type
- `reservation_status` - Current status and history

#### Reservation Status Categories

- `request` - Pending approval
- `accepted` - Confirmed booking
- `cancelled` - Cancelled reservation
- `not accepted` - Declined request
- `checkpoint` - Status checkpoint
- `unknown` - Unknown status

### Messages

Messages allow communication with guests about their reservations.

#### Endpoints

- `GET /reservations/{uuid}/messages` - Get reservation messages
- `POST /reservations/{uuid}/messages` - Send a message

#### Sending Messages

```json
{
  "body": "Hello! Your check-in details...",
  "images": ["https://example.com/image.jpg"]
}
```

**Rate Limits:**
- 2 messages per minute per reservation
- 50 messages per 5 minutes total

#### Message Sources

- `public_api` - Sent via API
- `platform` - Native platform messaging
- `hospitable` - Sent from Hospitable app
- `automated` - Scheduled/event-based
- `AI` - Auto-reply messages

### Calendar

Calendar endpoints manage property availability and pricing.

#### Calendar Day Structure

```json
{
  "date": "2024-03-15",
  "day": "FRIDAY",
  "min_stay": 2,
  "status": {
    "reason": "AVAILABLE",
    "available": true
  },
  "price": {
    "amount": 15000,
    "currency": "USD",
    "formatted": "$150.00"
  },
  "closed_for_checkin": false,
  "closed_for_checkout": false
}
```

#### Updating Calendar

```json
{
  "dates": [
    {
      "date": "2024-03-15",
      "price": {"amount": 15000},
      "available": true,
      "min_stay": 2
    }
  ]
}
```

**Limits:**
- Update up to 3 years in the future
- Maximum 60 dates per request
- 1000 requests per minute

### Reviews

Reviews from guests across platforms.

#### Endpoints

- `GET /properties/{uuid}/reviews` - Get property reviews
- `POST /reviews/{uuid}/respond` - Respond to a review

#### Review Structure

- `public` - Public rating and review text
- `private` - Private feedback
- `detailed_ratings` - Category-specific ratings
- `guest` - Guest information

### User

Get authenticated user and billing information.

#### Endpoint

- `GET /user` - Get user details

## Pagination

List endpoints support pagination:

- `page` - Page number (default: 1)
- `per_page` - Results per page (default: 10, max: 100)

Response includes `meta` object with pagination details.

## Including Related Data

Use the `include` parameter to fetch related data:

```
GET /properties?include=listings,user
```

Available includes vary by endpoint - check specific endpoint documentation.

## Error Handling

Error responses follow this format:

```json
{
  "status_code": 400,
  "reason_phrase": "Invalid pagination parameter supplied.",
  "message": "The given data was invalid."
}
```

Common status codes:
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `429` - Rate Limited
- `500` - Server Error

## Rate Limits

- Calendar updates: 1000 requests/minute
- Message sending: 2 per minute per reservation, 50 per 5 minutes total
- General API: Contact support for limits

## Webhooks

Webhooks provide real-time updates for:

- `reservation.created` - New reservation
- `reservation.updated` - Reservation changed
- `property.updated` - Property modified
- `message.created` - New message
- `review.created` - New review

Webhook payloads include:
- `id` - Unique payload ID
- `action` - Event type
- `data` - Full resource data
- `created` - Timestamp
- `version` - Webhook version

## Required Scopes

Different endpoints require specific token scopes:

- `property:read` - View properties
- `calendar:read` - View calendar
- `calendar:write` - Update calendar
- `reservation:read` - View reservations
- `message:read` - View messages
- `message:write` - Send messages (requires approval)
- `financials:read` - View financial data
- `listing:read` - View platform listings
- `reviews:read` - View reviews
- `reviews:write` - Respond to reviews

## Important Notes

- V1 API End of Life: February 3rd, 2025
- Properties with `calendar_restricted: true` cannot be updated via API
- HTML is not supported in messages
- Search endpoint requires self-hosted Direct site
- Contact team-platform@hospitable.com for `message:write` scope