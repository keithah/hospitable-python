"""
Messages endpoint implementation
"""

from typing import List, Optional, Dict, Any
from .base import BaseEndpoint
from ..models import Message, MessageSendResponse


class MessagesEndpoint(BaseEndpoint):
    """Messages API endpoint handler"""
    
    def list(self, reservation_uuid: str) -> List[Message]:
        """
        Get messages for a specific reservation.
        
        Args:
            reservation_uuid: Reservation UUID
            
        Returns:
            List of messages
            
        Required scopes:
        - message:read
        """
        response = self.client.get(f"/reservations/{reservation_uuid}/messages")
        data = response.json()
        
        return [self._parse_message(msg) for msg in data["data"]]
    
    def send(
        self,
        reservation_uuid: str,
        body: str,
        images: Optional[List[str]] = None,
    ) -> MessageSendResponse:
        """
        Send a message to the guest for a specific reservation.
        
        Args:
            reservation_uuid: Reservation UUID
            body: Message text content
            images: List of image URLs (max 3, 5MB each)
            
        Returns:
            Message send response with reference ID
            
        Notes:
        - HTML is not supported
        - \\n is parsed for line breaks
        - Maximum 3 images per message
        - Maximum 5MB per image
        
        Rate Limits:
        - 2 messages per minute per reservation
        - 50 messages per 5 minutes total
        
        Required scopes:
        - message:write (requires approval from team-platform@hospitable.com)
        """
        if images and len(images) > 3:
            raise ValueError("Maximum 3 images allowed per message")
        
        payload = {"body": body}
        if images:
            payload["images"] = images
        
        response = self.client.post(
            f"/reservations/{reservation_uuid}/messages",
            json_data=payload
        )
        data = response.json()
        
        return MessageSendResponse(
            sent_reference_id=data["data"]["sent_reference_id"]
        )
    
    def _parse_message(self, data: Dict[str, Any]) -> Message:
        """Parse message data from API response"""
        # For now, return raw data
        # TODO: Implement proper model parsing with datetime conversion
        return data