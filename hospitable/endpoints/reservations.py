"""
Reservations endpoint implementation
"""

from typing import List, Optional, Dict, Any
from .base import BaseEndpoint
from ..models import Reservation, PaginatedResponse


class ReservationsEndpoint(BaseEndpoint):
    """Reservations API endpoint handler"""
    
    def list(
        self,
        properties: List[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        include: Optional[str] = None,
        date_query: str = "checkin",
        platform_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        last_message_at: Optional[str] = None,
        page: int = 1,
        per_page: int = 10,
    ) -> PaginatedResponse:
        """
        Get a list of reservations.
        
        Args:
            properties: List of property UUIDs (required)
            start_date: Find reservations after this date (YYYY-MM-DD)
            end_date: Find reservations before this date (YYYY-MM-DD)
            include: Relationships to include
            date_query: Use dates for 'checkin' or 'checkout' search
            platform_id: Find by exact reservation code match
            conversation_id: Find by exact conversation UUID match
            last_message_at: Find reservations with last message after datetime
            page: Page number (default: 1)
            per_page: Results per page (max: 100, default: 10)
            
        Returns:
            Paginated response with reservations
            
        Available includes:
        - guest: Guest information
        - user: User information
        - financials: Financial data (requires financials:read scope)
        - listings: Platform listings (requires listing:read scope)
        - properties: Property data (requires property:read scope)
        - review: Review data (requires reviews:read scope)
        
        Notes:
        - Defaults to reservations with check-in dates in next 2 weeks
          if no date parameters provided
        """
        # Convert properties list to array parameter format
        params = self._build_query_params(
            start_date=start_date,
            end_date=end_date,
            include=include,
            date_query=date_query,
            platform_id=platform_id,
            conversation_id=conversation_id,
            last_message_at=last_message_at,
            page=page,
            per_page=per_page
        )
        
        # Add properties as array parameters
        for prop_uuid in properties:
            params[f"properties[]"] = prop_uuid
        
        response = self.client.get("/reservations", params=params)
        data = response.json()
        
        # Parse response
        reservations = [self._parse_reservation(res) for res in data["data"]]
        
        return PaginatedResponse(
            data=reservations,
            meta=data["meta"]
        )
    
    def get(
        self,
        uuid: str,
        include: Optional[str] = None,
    ) -> Reservation:
        """
        Get a specific reservation by UUID.
        
        Args:
            uuid: Reservation UUID
            include: Relationships to include
            
        Returns:
            Reservation object
            
        Available includes:
        - guest: Guest information
        - user: User information
        - financials: Financial data (requires financials:read scope)
        - financialsV2: V2 financial data (requires financials:read scope)
        - listings: Platform listings (requires listing:read scope)
        - properties: Property data (requires property:read scope)
        """
        params = self._build_query_params(include=include)
        
        response = self.client.get(f"/reservations/{uuid}", params=params)
        data = response.json()
        
        return self._parse_reservation(data["data"])
    
    def _parse_reservation(self, data: Dict[str, Any]) -> Reservation:
        """Parse reservation data from API response"""
        # For now, return raw data
        # TODO: Implement proper model parsing with datetime conversion
        return data