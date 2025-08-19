# Hospitable API Changelog

This document tracks changes to the Hospitable Public API that may affect the SDK.

## August 1st, 2025

### Track messages sent via the API

Previously, when sending a message via the Messaging API, no response data was returned. This was due to the synchronous nature of some booking platforms, which prevented us from immediately confirming the message details.

As a result, it wasn't possible to match a sent message with the corresponding message.created webhook.

**New feature**: `sent_reference_id`
- Returned in the API response when a message is sent
- Included in the `message.created` webhook payload
- Enables reliable correlation between sent messages and webhook events
- Makes end-to-end message tracking possible

**SDK Impact**: ✅ Already supported via `MessageSendResponse.sent_reference_id`

## July 30th, 2025

### New `stay_type` property added to reservation resource

New property to help identify owner stays:
- Included in reservation-specific webhooks and API responses
- Values: `guest_stay`, `owner_stay`

**SDK Impact**: ✅ Already supported in `Reservation.stay_type`

## July 29th, 2025

### New Message attributes to identify message source

Added new attributes to the Message resource:

**`source`** - Specifies the origin of the message:
- `public_api` – Sent via the API, using a Personal Access Token or by an integration partner
- `platform` – Sent through the booking channel's native messaging platform
- `hospitable` – Sent directly from within the Hospitable app
- `automated` – Sent as a scheduled or event-triggered automation
- `AI` – Sent by Hospitable's AI-powered auto-reply feature

**`integration`** - The name of the integration that sent the message (Personal Access Token only)

**SDK Impact**: ✅ Already supported in `Message.source` and `Message.integration`

## July 25th, 2025

### Guest issue alerts trigger webhooks

When a guest issue is detected:
- Triggers the reservation webhook
- `Reservation.issue_alert` field populated with issue description

**SDK Impact**: ✅ Already supported in `Reservation.issue_alert`

## July 24th, 2025

### iCal imports enhancements

Added resync option and timestamps:
- `resync: true` in PUT payload for unchanged URLs
- `last_sync_at` - nullable ISO-8601 timestamp of last sync
- `disconnected_at` - nullable ISO-8601 timestamp when disconnected

**SDK Impact**: ✅ Already supported in `iCalImport` model

## June 26th, 2025

### External iCal import management endpoints

New endpoints for managing iCal imports:
- Vendors can only manage imports they added
- Personal Access Tokens have no restrictions
- Shows in Property resource under `ical_imports` (requires `listings` include)

**SDK Impact**: ✅ Already supported in Property model

## March 19th, 2025

### Message and Review webhooks

Two new webhook types:
- **Message webhook**: Triggers when new message created (excludes messages >12 hours old)
- **Review webhook**: Triggers when new review received (Airbnb and direct bookings)

**SDK Impact**: ✅ Already documented in webhook guides

## February 20th, 2025

### Source information for calendar blocks

Enhanced calendar blocking information:

**`source_type`** values:
- `USER` - Manually blocked by user
- `PLATFORM` - Blocked on platform (e.g., Airbnb)
- `VENDOR` - Blocked by integration partner
- `AVAILABILITY_WINDOW` - Blocked by availability window
- `TURNOVER_DAY` - Blocked by turnover day configuration
- `ADVANCED_NOTICE` - Blocked by advance notice period
- `UPSELL` - Blocked by upsell configuration
- `RESERVATION` - Blocked by reservation

**`source`** - Specific information based on source_type

**SDK Impact**: ✅ Already supported in `AvailabilityStatus` model

## January 28th, 2025

### Property webhooks

New property webhook events:
- `property.created`
- `property.changed` 
- `property.deleted`
- `property.merged`

**SDK Impact**: ✅ Already documented in webhook guides

## January 15th, 2025

### Financial changes trigger webhooks

Reservation financial updates (adjustments) now trigger reservation webhooks.

**SDK Impact**: ✅ No changes needed

## January 8th, 2025

### Parent/Child relationship details

Added `parent_child` property to Property resource:
- `type`: "parent" or "child"
- `parent`: Parent property ID (for children)
- `children`: Array of child property IDs (for parents)
- `siblings`: Array of sibling property IDs (for children)

**SDK Impact**: ✅ Already supported in `Property.parent_child`

## January 2nd, 2025

### `nights` attribute for Reservations

Added `nights` property to avoid calculating from check-in/check-out dates.

**SDK Impact**: ✅ Already supported in `Reservation.nights`

## December 4th, 2024

### Review endpoints

New endpoints:
- Get property reviews
- Respond to review
- Review include parameter for Reservation API

**SDK Impact**: ✅ Already implemented in `ReviewsEndpoint`

## November 21st, 2024

### Property checkout time

Added `checkout` attribute to Property resource (previously only had `check_in`).

**SDK Impact**: ✅ Already supported in `Property.check_out`

## November 8th, 2024

### Calendar check-in/check-out restrictions

Added support for updating check-in/check-out restrictions:
- `closed_for_checkin` and `closed_for_checkout` in calendar updates

**SDK Impact**: ✅ Already supported in calendar update methods

### New property booking include

New `bookings` include for property endpoints:
- Provides booking information (fees, policies, markups, security deposits)
- Requires `property:read` scope

**SDK Impact**: ✅ Already supported via include parameter

## November 7th, 2024

### Integration disconnected webhook

New `integration.disconnected` webhook when user disconnects integration.

**SDK Impact**: ✅ Documented in webhook guides

## October 9th, 2024

### Send images with messages

Support for sending up to 3 images with messages via `images` array.

**SDK Impact**: ✅ Already supported in `MessagesEndpoint.send()`

## September 20th, 2024

### Property details include

New `details` include for properties with descriptive information and WiFi details.
Added `property_type` and `room_type` to base property.

**SDK Impact**: ✅ Already supported

### Inquiry endpoints

New endpoints for pre-reservation inquiries:
- Get all inquiries
- Get single inquiry  
- Send message to inquiry

**SDK Impact**: 🔄 Could be added in future SDK version

## September 19th, 2024

### Reservation financials deprecation

Old `financials` object deprecated in favor of `financialsV2`.

**SDK Impact**: ✅ SDK uses current API structure

## July 18th, 2024

### New reservation financials

Reworked financials structure:
- Shows negative amounts for discounts/adjustments
- Raw financial data instead of totals
- Per-night accommodation breakdown
- Single currency field

**SDK Impact**: ✅ SDK uses current structure

## July 14th, 2024

### User attribute in reservation webhook

Added `user` object to reservation webhook payload for multi-user identification.

**SDK Impact**: ✅ No changes needed

## June 12th, 2024

### Deprecated status and status_history

Replaced with unified `reservation_status` object.

**SDK Impact**: ✅ SDK supports both old and new structures

## April 4th, 2024

### Status changes trigger webhooks

Reservation status changes now trigger `reservation.changed` webhook.

**SDK Impact**: ✅ No changes needed

---

## SDK Compatibility

The Hospitable Python SDK is designed to be forward-compatible with API changes:

✅ **Fully Compatible** - All documented features supported
🔄 **Partial/Future** - May be added in future versions
❌ **Not Applicable** - Not relevant to SDK functionality

The SDK automatically handles most API evolution through flexible data models and optional parameters.