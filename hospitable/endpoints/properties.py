"""
Properties endpoint implementation
"""

from typing import List, Optional, Dict, Any, Union
from .base import BaseEndpoint
from ..models import (
    Property, 
    PropertySearchResult, 
    PropertyCalendar, 
    CalendarUpdateResponse,
    PaginatedResponse,
)


class PropertiesEndpoint(BaseEndpoint):
    """Properties API endpoint handler"""
    
    def list(
        self,
        include: Optional[str] = None,
        page: int = 1,
        per_page: int = 10,
    ) -> PaginatedResponse:
        """
        Get a list of properties.
        
        Args:
            include: Relationships to include (user, listings, details, bookings)
            page: Page number (default: 1)
            per_page: Results per page (max: 100, default: 10)
            
        Returns:
            Paginated response with properties
            
        Available includes:
        - user: User information
        - listings: Platform listings (requires listing:read scope)
        - details: Additional property details
        - bookings: Booking information
        """
        params = self._build_query_params(
            include=include,
            page=page,
            per_page=per_page
        )
        
        response = self.client.get("/properties", params=params)
        data = response.json()
        
        # Parse response
        properties = [self._parse_property(prop) for prop in data["data"]]
        
        return PaginatedResponse(
            data=properties,
            meta=data["meta"]
        )
    
    def get(
        self,
        uuid: str,
        include: Optional[str] = None,
    ) -> Property:
        """
        Get a specific property by UUID.
        
        Args:
            uuid: Property UUID
            include: Relationships to include
            
        Returns:
            Property object
        """
        params = self._build_query_params(include=include)
        
        response = self.client.get(f"/properties/{uuid}", params=params)
        data = response.json()
        
        return self._parse_property(data["data"])
    
    def search(
        self,
        start_date: str,
        end_date: str,
        adults: int,
        children: Optional[int] = None,
        infants: Optional[int] = None,
        pets: Optional[int] = None,
        location: Optional[Dict[str, float]] = None,
        include: Optional[str] = None,
    ) -> List[PropertySearchResult]:
        """
        Search for properties with availability and pricing.
        
        Args:
            start_date: Check-in date (YYYY-MM-DD)
            end_date: Check-out date (YYYY-MM-DD) 
            adults: Number of adults (required)
            children: Number of children
            infants: Number of infants
            pets: Number of pets
            location: Location dict with latitude/longitude
            include: Relationships to include (listings, details)
            
        Returns:
            List of property search results
            
        Notes:
        - Search up to 3 years in the future
        - Maximum 90-day period
        - Requires self-hosted Direct site
        """
        params = self._build_query_params(
            start_date=start_date,
            end_date=end_date,
            adults=adults,
            children=children,
            infants=infants,
            pets=pets,
            location=location,
            include=include
        )
        
        response = self.client.get("/properties/search", params=params)
        data = response.json()
        
        return [self._parse_search_result(result) for result in data["data"]]
    
    def get_calendar(
        self,
        uuid: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> PropertyCalendar:
        """
        Get property calendar data.
        
        Args:
            uuid: Property UUID
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Property calendar object
            
        Required scopes:
        - property:read
        - calendar:read
        """
        params = self._build_query_params(
            start_date=start_date,
            end_date=end_date
        )
        
        response = self.client.get(f"/properties/{uuid}/calendar", params=params)
        data = response.json()
        
        return self._parse_calendar(data["data"])
    
    def update_calendar(
        self,
        uuid: str,
        dates: List[Dict[str, Any]],
    ) -> CalendarUpdateResponse:
        """
        Update property calendar pricing and availability.
        
        Args:
            uuid: Property UUID
            dates: List of date updates (max 60 dates)
            
        Returns:
            Calendar update response
            
        Date format:
        {
            "date": "YYYY-MM-DD",
            "price": {"amount": 15000},  # Optional, in base units
            "available": True,            # Optional
            "min_stay": 2,               # Optional
            "closed_for_checkin": False, # Optional
            "closed_for_checkout": False # Optional
        }
        
        Limits:
        - Update up to 3 years in the future
        - Maximum 60 dates per request
        - Rate limit: 1000 requests/minute
        
        Required scopes:
        - property:read
        - calendar:write
        """
        if len(dates) > 60:
            raise ValueError("Maximum 60 dates allowed per request")
        
        payload = {"dates": dates}
        
        response = self.client.put(f"/properties/{uuid}/calendar", json_data=payload)
        data = response.json()
        
        return CalendarUpdateResponse(status=data["status"])
    
    def _parse_property(self, data: Dict[str, Any]) -> Property:
        """Parse property data from API response"""
        # For now, return raw data
        # TODO: Implement proper model parsing
        return data
    
    def _parse_search_result(self, data: Dict[str, Any]) -> PropertySearchResult:
        """Parse property search result from API response"""
        # For now, return raw data
        # TODO: Implement proper model parsing
        return data
    
    def _parse_calendar(self, data: Dict[str, Any]) -> PropertyCalendar:
        """Parse calendar data from API response"""
        # For now, return raw data
        # TODO: Implement proper model parsing
        return data