"""
Hospitable API Client

Main client class for interacting with the Hospitable Public API v2.
"""

import os
import time
from typing import Optional, Dict, Any, Union
from urllib.parse import urljoin
import requests
from datetime import datetime, timedelta

from .exceptions import (
    HospitableError,
    AuthenticationError,
    ForbiddenError,
    NotFoundError,
    ValidationError,
    RateLimitError,
    ServerError,
)
from .endpoints import (
    PropertiesEndpoint,
    ReservationsEndpoint,
    MessagesEndpoint,
    ReviewsEndpoint,
    UserEndpoint,
)
from .jwt_utils import parse_jwt, JWTInfo


class HospitableClient:
    """
    Main client for the Hospitable Public API v2.
    
    Supports both Personal Access Tokens (PATs) and OAuth 2.0 authentication.
    """
    
    DEFAULT_BASE_URL = "https://public.api.hospitable.com/v2"
    DEFAULT_AUTH_URL = "https://auth.hospitable.com/oauth/token"
    
    def __init__(
        self,
        token: Optional[str] = None,
        refresh_token: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        base_url: Optional[str] = None,
        auth_url: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        auto_refresh: bool = True,
    ):
        """
        Initialize the Hospitable API client.
        
        Args:
            token: Access token (Personal Access Token or OAuth access token)
            refresh_token: OAuth refresh token (required for auto-refresh)
            client_id: OAuth client ID (required for token refresh)
            client_secret: OAuth client secret (required for token refresh)
            base_url: API base URL (defaults to production)
            auth_url: OAuth token URL (defaults to production)
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts for failed requests
            auto_refresh: Automatically refresh expired OAuth tokens
        
        Environment Variables:
            HOSPITABLE_PAT: Personal Access Token (preferred)
            HOSPITABLE_TOKEN: Access token (fallback)
        """
        # Use environment variable if no token provided
        self.token = token or os.getenv("HOSPITABLE_PAT") or os.getenv("HOSPITABLE_TOKEN")
        if not self.token:
            raise ValueError("Token is required. Provide token parameter or set HOSPITABLE_PAT/HOSPITABLE_TOKEN environment variable.")
        
        # OAuth credentials for token refresh
        self.refresh_token = refresh_token
        self.client_id = client_id
        self.client_secret = client_secret
        
        # API configuration
        self.base_url = base_url or self.DEFAULT_BASE_URL
        self.auth_url = auth_url or self.DEFAULT_AUTH_URL
        self.timeout = timeout
        self.max_retries = max_retries
        self.auto_refresh = auto_refresh
        
        # Token expiry tracking
        self._token_expires_at: Optional[datetime] = None
        
        # Parse JWT token info if it's a JWT
        self._jwt_info: Optional[JWTInfo] = None
        try:
            self._jwt_info = parse_jwt(self.token)
            # Use JWT expiry if available
            if self._jwt_info.expires_at:
                self._token_expires_at = self._jwt_info.expires_at
        except ValueError:
            # Not a JWT token, continue normally
            pass
        
        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "hospitable-python/0.1.0",
        })
        
        # Initialize endpoint handlers
        self.properties = PropertiesEndpoint(self)
        self.reservations = ReservationsEndpoint(self)
        self.messages = MessagesEndpoint(self)
        self.reviews = ReviewsEndpoint(self)
        self.user = UserEndpoint(self)
    
    def _update_auth_header(self):
        """Update the Authorization header with current token."""
        self.session.headers["Authorization"] = f"Bearer {self.token}"
    
    def get_token_info(self) -> Optional[JWTInfo]:
        """
        Get JWT token information if token is a valid JWT.
        
        Returns:
            JWTInfo object with token details, or None if not a JWT
        """
        return self._jwt_info
    
    def _is_token_expired(self) -> bool:
        """Check if the current token is expired."""
        if not self._token_expires_at:
            return False
        return datetime.now() >= self._token_expires_at - timedelta(minutes=5)  # 5 min buffer
    
    def _should_refresh_token(self) -> bool:
        """Determine if token should be refreshed."""
        return (
            self.auto_refresh and 
            self.refresh_token and 
            self.client_id and 
            self.client_secret and
            self._is_token_expired()
        )
    
    def refresh_access_token(self) -> Dict[str, Any]:
        """
        Refresh the OAuth access token using the refresh token.
        
        Returns:
            Dictionary containing new token information
            
        Raises:
            AuthenticationError: If refresh fails
        """
        if not all([self.refresh_token, self.client_id, self.client_secret]):
            raise AuthenticationError("OAuth credentials required for token refresh")
        
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
        }
        
        try:
            response = requests.post(
                self.auth_url,
                json=data,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            token_data = response.json()
            
            # Update client with new tokens
            self.token = token_data["access_token"]
            self.refresh_token = token_data.get("refresh_token", self.refresh_token)
            
            # Set expiry time
            expires_in = token_data.get("expires_in", 43200)  # Default 12 hours
            self._token_expires_at = datetime.now() + timedelta(seconds=expires_in)
            
            # Update session header
            self._update_auth_header()
            
            return token_data
            
        except requests.exceptions.RequestException as e:
            raise AuthenticationError(f"Token refresh failed: {e}")
        except KeyError as e:
            raise AuthenticationError(f"Invalid token response: missing {e}")
    
    def _handle_response_errors(self, response: requests.Response):
        """
        Handle HTTP error responses and raise appropriate exceptions.
        
        Args:
            response: HTTP response object
            
        Raises:
            Appropriate HospitableError subclass
        """
        if response.status_code < 400:
            return
        
        try:
            error_data = response.json()
            message = error_data.get("message", response.reason)
            reason_phrase = error_data.get("reason_phrase", "")
        except (ValueError, KeyError):
            message = response.reason
            reason_phrase = ""
        
        full_message = f"{message}. {reason_phrase}".strip(". ")
        
        if response.status_code == 401:
            raise AuthenticationError(full_message, response.status_code, response)
        elif response.status_code == 403:
            raise ForbiddenError(full_message, response.status_code, response)
        elif response.status_code == 404:
            raise NotFoundError(full_message, response.status_code, response)
        elif response.status_code == 400:
            raise ValidationError(full_message, response.status_code, response)
        elif response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            if retry_after:
                retry_after = int(retry_after)
            raise RateLimitError(full_message, retry_after, response.status_code, response)
        elif response.status_code >= 500:
            raise ServerError(full_message, response.status_code, response)
        else:
            raise HospitableError(full_message, response.status_code, response)
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        retries: int = 0,
    ) -> requests.Response:
        """
        Make an HTTP request to the API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (without base URL)
            params: Query parameters
            json_data: JSON body data
            retries: Current retry count
            
        Returns:
            HTTP response object
            
        Raises:
            Various HospitableError subclasses for different error conditions
        """
        # Check if token needs refresh
        if self._should_refresh_token():
            try:
                self.refresh_access_token()
            except AuthenticationError:
                # Continue with current token, let the request fail if needed
                pass
        
        # Ensure auth header is set
        self._update_auth_header()
        
        # Build full URL
        url = urljoin(self.base_url.rstrip("/") + "/", endpoint.lstrip("/"))
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                timeout=self.timeout,
            )
            
            # Handle rate limiting with retry
            if response.status_code == 429 and retries < self.max_retries:
                retry_after = int(response.headers.get("Retry-After", 60))
                time.sleep(retry_after)
                return self._make_request(method, endpoint, params, json_data, retries + 1)
            
            # Handle auth errors with token refresh
            if (
                response.status_code == 401 and 
                retries == 0 and 
                self.auto_refresh and 
                self.refresh_token
            ):
                try:
                    self.refresh_access_token()
                    return self._make_request(method, endpoint, params, json_data, retries + 1)
                except AuthenticationError:
                    # Refresh failed, let original error bubble up
                    pass
            
            # Check for errors
            self._handle_response_errors(response)
            
            return response
            
        except requests.exceptions.Timeout:
            if retries < self.max_retries:
                time.sleep(2 ** retries)  # Exponential backoff
                return self._make_request(method, endpoint, params, json_data, retries + 1)
            raise HospitableError(f"Request timeout after {retries + 1} attempts")
        
        except requests.exceptions.RequestException as e:
            if retries < self.max_retries:
                time.sleep(2 ** retries)
                return self._make_request(method, endpoint, params, json_data, retries + 1)
            raise HospitableError(f"Request failed: {e}")
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        """Make a GET request."""
        return self._make_request("GET", endpoint, params=params)
    
    def post(self, endpoint: str, json_data: Optional[Dict[str, Any]] = None) -> requests.Response:
        """Make a POST request."""
        return self._make_request("POST", endpoint, json_data=json_data)
    
    def put(self, endpoint: str, json_data: Optional[Dict[str, Any]] = None) -> requests.Response:
        """Make a PUT request."""
        return self._make_request("PUT", endpoint, json_data=json_data)
    
    def delete(self, endpoint: str) -> requests.Response:
        """Make a DELETE request."""
        return self._make_request("DELETE", endpoint)
    
    def patch(self, endpoint: str, json_data: Optional[Dict[str, Any]] = None) -> requests.Response:
        """Make a PATCH request."""
        return self._make_request("PATCH", endpoint, json_data=json_data)
    
    def close(self):
        """Close the HTTP session."""
        self.session.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def __repr__(self):
        """String representation of the client."""
        return f"HospitableClient(base_url='{self.base_url}')"