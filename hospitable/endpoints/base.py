"""
Base endpoint class for common functionality
"""

from typing import TYPE_CHECKING, Dict, Any, Optional, List, Type, TypeVar
from datetime import datetime
import json

if TYPE_CHECKING:
    from ..client import HospitableClient

T = TypeVar('T')


class BaseEndpoint:
    """Base class for API endpoints"""
    
    def __init__(self, client: "HospitableClient"):
        self.client = client
    
    def _parse_datetime(self, dt_str: Optional[str]) -> Optional[datetime]:
        """Parse datetime string from API response"""
        if not dt_str:
            return None
        
        # Handle different datetime formats from API
        formats = [
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%dT%H:%M:%S.%f%z",
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(dt_str, fmt)
            except ValueError:
                continue
        
        # If none of the formats work, raise an error
        raise ValueError(f"Unable to parse datetime: {dt_str}")
    
    def _parse_dict_to_model(self, data: Dict[str, Any], model_class: Type[T]) -> T:
        """Convert dictionary to data model, handling nested objects"""
        # This is a simplified parser - in a production system you'd want
        # to use a library like pydantic or implement more robust parsing
        
        # For now, we'll return the dictionary as-is
        # TODO: Implement proper model parsing
        return data
    
    def _build_query_params(self, **kwargs) -> Dict[str, str]:
        """Build query parameters, filtering out None values"""
        params = {}
        
        for key, value in kwargs.items():
            if value is not None:
                if isinstance(value, list):
                    # Handle array parameters
                    if key.endswith('[]'):
                        # Already formatted for arrays
                        params[key] = value
                    else:
                        # Convert to comma-separated string
                        params[key] = ','.join(str(v) for v in value)
                elif isinstance(value, bool):
                    params[key] = 'true' if value else 'false'
                elif isinstance(value, dict):
                    # Handle nested objects (like location)
                    for nested_key, nested_value in value.items():
                        params[f"{key}[{nested_key}]"] = str(nested_value)
                else:
                    params[key] = str(value)
        
        return params