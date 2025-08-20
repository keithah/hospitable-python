"""
JWT utilities for token parsing and validation
"""

import json
import base64
from typing import Dict, Any, Optional
from datetime import datetime, timedelta


class JWTInfo:
    """Container for JWT token information"""
    
    def __init__(self, payload: Dict[str, Any]):
        self.payload = payload
        self.aud = payload.get('aud')
        self.jti = payload.get('jti')
        self.iat = payload.get('iat')
        self.nbf = payload.get('nbf')
        self.exp = payload.get('exp')
        self.sub = payload.get('sub')
        self.scopes = payload.get('scopes', [])
    
    @property
    def issued_at(self) -> Optional[datetime]:
        """Get token issued at time"""
        return datetime.fromtimestamp(self.iat) if self.iat else None
    
    @property
    def expires_at(self) -> Optional[datetime]:
        """Get token expiration time"""
        return datetime.fromtimestamp(self.exp) if self.exp else None
    
    @property
    def not_before(self) -> Optional[datetime]:
        """Get token not before time"""
        return datetime.fromtimestamp(self.nbf) if self.nbf else None
    
    @property
    def is_expired(self) -> bool:
        """Check if token is expired"""
        if not self.exp:
            return False
        return datetime.now() >= datetime.fromtimestamp(self.exp)
    
    @property
    def time_until_expiry(self) -> Optional[timedelta]:
        """Get time until token expires"""
        if not self.exp:
            return None
        exp_time = datetime.fromtimestamp(self.exp)
        if exp_time <= datetime.now():
            return timedelta(0)
        return exp_time - datetime.now()
    
    @property
    def user_id(self) -> Optional[str]:
        """Get user ID from subject"""
        return self.sub
    
    def has_scope(self, scope: str) -> bool:
        """Check if token has specific scope"""
        return scope in self.scopes
    
    def has_read_access(self) -> bool:
        """Check if token has read access"""
        return self.has_scope('pat:read') or 'read' in ' '.join(self.scopes)
    
    def has_write_access(self) -> bool:
        """Check if token has write access"""
        return self.has_scope('pat:write') or 'write' in ' '.join(self.scopes)
    
    def __repr__(self):
        return f"JWTInfo(sub={self.sub}, scopes={self.scopes}, expires={self.expires_at})"


def decode_jwt_payload(token: str) -> Dict[str, Any]:
    """
    Decode JWT payload without verification.
    
    Note: This only decodes the payload, it does NOT verify the signature.
    For production use, you should verify the signature with the proper key.
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded payload dictionary
        
    Raises:
        ValueError: If token format is invalid
    """
    try:
        # Split the token into its parts
        parts = token.split('.')
        if len(parts) != 3:
            raise ValueError("Invalid JWT format: expected 3 parts separated by '.'")
        
        # Decode the payload (second part)
        payload = parts[1]
        
        # Add padding if needed for base64 decoding
        padding = len(payload) % 4
        if padding:
            payload += '=' * (4 - padding)
        
        # Decode from base64
        decoded_bytes = base64.urlsafe_b64decode(payload)
        decoded_payload = json.loads(decoded_bytes)
        
        return decoded_payload
    except (json.JSONDecodeError, ValueError) as e:
        raise ValueError(f"Failed to decode JWT payload: {e}")
    except Exception as e:
        raise ValueError(f"Unexpected error decoding JWT: {e}")


def parse_jwt(token: str) -> JWTInfo:
    """
    Parse JWT token and return structured information.
    
    Args:
        token: JWT token string
        
    Returns:
        JWTInfo object with parsed token data
    """
    payload = decode_jwt_payload(token)
    return JWTInfo(payload)