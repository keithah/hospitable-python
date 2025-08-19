"""
Hospitable API exceptions
"""


class HospitableError(Exception):
    """Base exception for all Hospitable API errors."""
    
    def __init__(self, message, status_code=None, response=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response = response


class AuthenticationError(HospitableError):
    """Raised when API authentication fails (401)."""
    pass


class ForbiddenError(HospitableError):
    """Raised when API request is forbidden (403)."""
    pass


class NotFoundError(HospitableError):
    """Raised when requested resource is not found (404)."""
    pass


class ValidationError(HospitableError):
    """Raised when request validation fails (400)."""
    pass


class RateLimitError(HospitableError):
    """Raised when API rate limit is exceeded (429)."""
    
    def __init__(self, message, retry_after=None, **kwargs):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


class ServerError(HospitableError):
    """Raised when server returns 5xx error."""
    pass