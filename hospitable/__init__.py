"""
Hospitable Python SDK

A Python library for interacting with the Hospitable Public API v2.
Manage properties, reservations, calendars, messaging, and reviews.
"""

from .client import HospitableClient
from .exceptions import (
    HospitableError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    NotFoundError,
    ForbiddenError,
)
from .jwt_utils import JWTInfo, parse_jwt

__version__ = "0.1.0"
__author__ = "Keith"
__email__ = "keith@example.com"
__description__ = "Python SDK for Hospitable API"

__all__ = [
    "HospitableClient",
    "HospitableError",
    "AuthenticationError", 
    "RateLimitError",
    "ValidationError",
    "NotFoundError",
    "ForbiddenError",
    "JWTInfo",
    "parse_jwt",
]