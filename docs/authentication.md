# Authentication

The Hospitable API supports two authentication methods: Personal Access Tokens (PATs) for personal use and OAuth 2.0 for vendor integrations.

## Personal Access Tokens (PATs)

Best for personal API access and testing integrations.

### Getting a PAT

1. Log in to [my.hospitable.com](https://my.hospitable.com)
2. Navigate to **Apps** → **API access**
3. Click **+ Add new** in the Access tokens tab
4. Name your token and select permissions:
   - **Read**: View properties, reservations, calendars
   - **Write**: Modify calendar pricing and availability

### Using PATs

```python
from hospitable import HospitableClient

client = HospitableClient(token="your_pat_token")
```

### PAT Scopes

Different endpoints require specific scopes:

- `property:read` - View properties
- `calendar:read` - View calendar data
- `calendar:write` - Update calendar pricing/availability
- `reservation:read` - View reservations
- `message:read` - View messages
- `message:write` - Send messages (requires approval)
- `financials:read` - View financial data
- `listing:read` - View platform listings
- `reviews:read` - View reviews
- `reviews:write` - Respond to reviews

## OAuth 2.0 for Vendors

Required for building integrations used by other Hospitable users.

### Becoming an Approved Vendor

Submit an application with:
- Technical contact information
- App name and description
- Requested scopes
- App logo URL (square format, .png/.jpg)
- Customer-facing description
- Redirect URL
- Webhooks URL

### OAuth Flow Implementation

#### 1. Authorization URL

Direct users to:
```
https://auth.hospitable.com/oauth/authorize?client_id=<vendor_id>&response_type=code&state=<optional_state>
```

#### 2. Handle Redirect

After authorization, users are redirected to your configured URL with a `code` parameter:
```
https://your-app.com/redirect?code=def2020087...&state=<your_state>
```

**Note**: Authorization codes expire in 10 minutes.

#### 3. Exchange Code for Tokens

```python
import requests

response = requests.post("https://auth.hospitable.com/oauth/token", json={
    "client_id": "your_vendor_id",
    "client_secret": "your_vendor_secret", 
    "grant_type": "authorization_code",
    "code": "def2020087..."
})

tokens = response.json()
# {
#   "token_type": "Bearer",
#   "expires_in": 43200,  # 12 hours
#   "access_token": "eyJ0eXA...",
#   "refresh_token": "def502005..."
# }
```

#### 4. Using OAuth Tokens

```python
from hospitable import HospitableClient

client = HospitableClient(
    token=tokens["access_token"],
    refresh_token=tokens["refresh_token"],
    client_id="your_vendor_id",
    client_secret="your_vendor_secret"
)
```

### Token Refresh

Access tokens expire after 12 hours. Refresh automatically:

```python
# The client will automatically refresh when needed
properties = client.properties.list()  # Auto-refreshes if expired

# Or manually refresh
new_tokens = client.refresh_token()
```

Manual refresh request:
```python
import requests

response = requests.post("https://auth.hospitable.com/oauth/token", json={
    "client_id": "your_vendor_id",
    "client_secret": "your_vendor_secret",
    "grant_type": "refresh_token", 
    "refresh_token": "your_refresh_token"
})
```

### Token Storage Considerations

- **Access tokens**: ~1,200 characters
- **Refresh tokens**: ~1,000 characters
- **Refresh token expiry**: 90 days if unused
- **Recommendation**: Refresh tokens regularly to prevent expiry

## One-Click OAuth

Hospitable provides a streamlined OAuth flow initiated from their Apps marketplace:

1. User clicks "Get Started" in Hospitable
2. User is redirected directly to your app with authorization code
3. No need for separate authorization page visit

## State Parameter Security

Use the `state` parameter for security and request tracking:

```python
import uuid
import urllib.parse

state = str(uuid.uuid4())
# Store state in session/database

auth_url = f"https://auth.hospitable.com/oauth/authorize?client_id={client_id}&response_type=code&state={state}"

# Later, verify state matches when handling redirect
if received_state != stored_state:
    raise SecurityError("Invalid state parameter")
```

## Error Handling

Common authentication errors:

- `401 Unauthorized` - Invalid or expired token
- `403 Forbidden` - Insufficient permissions
- `invalid_grant` - Invalid authorization code or refresh token

```python
from hospitable.exceptions import AuthenticationError, ForbiddenError

try:
    properties = client.properties.list()
except AuthenticationError:
    # Token invalid or expired
    client.refresh_token()
    properties = client.properties.list()
except ForbiddenError:
    # Insufficient permissions
    print("This operation requires additional scopes")
```