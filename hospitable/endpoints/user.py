"""
User endpoint implementation
"""

from typing import Dict, Any
from .base import BaseEndpoint
from ..models import User


class UserEndpoint(BaseEndpoint):
    """User API endpoint handler"""
    
    def get(self) -> User:
        """
        Get authenticated user and billing information.
        
        Returns:
            User object with account and billing details
        """
        response = self.client.get("/user")
        data = response.json()
        
        return self._parse_user(data["data"])
    
    def _parse_user(self, data: Dict[str, Any]) -> User:
        """Parse user data from API response"""
        # For now, return raw data
        # TODO: Implement proper model parsing
        return data