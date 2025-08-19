# Hospitable Python SDK Documentation

## Overview

The Hospitable Python SDK provides a comprehensive interface to the Hospitable Public API v2, allowing you to manage vacation rental properties, reservations, calendars, guest messaging, and reviews programmatically.

## Table of Contents

- [Quick Start](quickstart.md)
- [Authentication](authentication.md)
- [API Reference](api-reference.md)
- [Webhooks](webhooks.md)
- [Rate Limits](rate-limits.md)
- [Error Handling](error-handling.md)
- [Examples](examples.md)

## Key Features

- **Properties Management**: List, search, and manage vacation rental properties
- **Reservations**: Access booking data across all connected platforms
- **Calendar Management**: Update pricing and availability
- **Guest Messaging**: Send and receive messages with rate limiting
- **Reviews**: Access and respond to guest reviews
- **Webhooks**: Real-time event notifications
- **OAuth2 & PAT Support**: Both vendor OAuth and personal access tokens

## Installation

```bash
pip install hospitable-python
```

## Quick Example

```python
from hospitable import HospitableClient

# Initialize with Personal Access Token
client = HospitableClient(token="your_pat_token")

# Get all properties
properties = client.properties.list()

# Get reservations for a property
reservations = client.reservations.list(
    properties=["property-uuid"],
    start_date="2024-01-01",
    end_date="2024-12-31"
)

# Update calendar pricing
client.properties.update_calendar("property-uuid", [
    {
        "date": "2024-03-15",
        "price": {"amount": 15000},  # $150.00
        "available": True,
        "min_stay": 2
    }
])
```

## API Versions

- **Current**: v2 (recommended)
- **Deprecated**: v1 (sunset: February 3rd, 2025)

The SDK automatically uses API v2 endpoints and handles versioning transparently.

## Support

- **Documentation**: [developer.hospitable.com](https://developer.hospitable.com)
- **Platform Team**: team-platform@hospitable.com
- **GitHub Issues**: [Report bugs and feature requests](https://github.com/your-username/hospitable-python/issues)