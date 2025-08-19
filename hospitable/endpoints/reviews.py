"""
Reviews endpoint implementation
"""

from typing import Optional, Dict, Any
from .base import BaseEndpoint
from ..models import Review, PaginatedResponse


class ReviewsEndpoint(BaseEndpoint):
    """Reviews API endpoint handler"""
    
    def list(
        self,
        property_uuid: str,
        include: Optional[str] = None,
        page: int = 1,
        per_page: int = 10,
    ) -> PaginatedResponse:
        """
        Get reviews for a specific property.
        
        Args:
            property_uuid: Property UUID
            include: Relationships to include
            page: Page number (default: 1)
            per_page: Results per page (max: 50, default: 10)
            
        Returns:
            Paginated response with reviews
            
        Available includes:
        - guest: Guest information
        - reservations: Reservation data
        
        Required scopes:
        - reviews:read
        
        Notes:
        - Sources review data from Airbnb and direct bookings
        """
        params = self._build_query_params(
            include=include,
            page=page,
            per_page=per_page
        )
        
        response = self.client.get(f"/properties/{property_uuid}/reviews", params=params)
        data = response.json()
        
        # Parse response
        reviews = [self._parse_review(review) for review in data["data"]]
        
        return PaginatedResponse(
            data=reviews,
            meta=data["meta"]
        )
    
    def respond(
        self,
        review_uuid: str,
        response: str,
    ) -> Review:
        """
        Respond to a review.
        
        Args:
            review_uuid: Review UUID
            response: Response text
            
        Returns:
            Updated review object with response
            
        Required scopes:
        - reviews:write
        
        Limitations:
        - Can only respond once per review
        - Must respond within platform's response window
        - Returns 403 if review cannot be responded to
        """
        payload = {"response": response}
        
        response_obj = self.client.post(
            f"/reviews/{review_uuid}/respond",
            json_data=payload
        )
        data = response_obj.json()
        
        return self._parse_review(data["data"])
    
    def _parse_review(self, data: Dict[str, Any]) -> Review:
        """Parse review data from API response"""
        # For now, return raw data
        # TODO: Implement proper model parsing with datetime conversion
        return data