from sqlalchemy.orm import Session
from typing import List, Optional
from app.repositories.team_request_repository import TeamRequestRepository
from app.repositories.participant_repository import ParticipantRepository
from app.schemas.team_request import TeamRequestResponse

class NotificationService:
    def __init__(self, db: Session):
        self.db = db
        self.request_repository = TeamRequestRepository(db)
        self.participant_repository = ParticipantRepository(db)
    
    def get_unread_request_count(self, participant_id: str) -> int:
        """Get count of unread team requests for a participant"""
        incoming_requests = self.request_repository.get_incoming_requests(participant_id)
        unread_count = sum(1 for req in incoming_requests if req.status == "pending")
        return unread_count
    
    def mark_request_as_read(self, request_id: str, participant_id: str) -> bool:
        """Mark a request as read (optional feature for future)"""
        # For now, just return success
        # In future, could add a 'read' field to track read status
        return True
    
    def get_recent_requests(self, participant_id: str, limit: int = 5) -> List[TeamRequestResponse]:
        """Get recent team requests for a participant"""
        incoming_requests = self.request_repository.get_incoming_requests(participant_id)
        # Sort by creation date and limit
        recent_requests = sorted(incoming_requests, key=lambda x: x.created_at, reverse=True)[:limit]
        return [TeamRequestResponse.from_orm(req) for req in recent_requests]
    
    def get_request_summary(self, participant_id: str) -> dict:
        """Get a summary of all requests for a participant"""
        incoming_requests = self.request_repository.get_incoming_requests(participant_id)
        outgoing_requests = self.request_repository.get_outgoing_requests(participant_id)
        
        # Count by status
        incoming_by_status = {}
        outgoing_by_status = {}
        
        for req in incoming_requests:
            status = req.status
            incoming_by_status[status] = incoming_by_status.get(status, 0) + 1
        
        for req in outgoing_requests:
            status = req.status
            outgoing_by_status[status] = outgoing_by_status.get(status, 0) + 1
        
        return {
            "incoming": {
                "total": len(incoming_requests),
                "pending": incoming_by_status.get("pending", 0),
                "accepted": incoming_by_status.get("accepted", 0),
                "declined": incoming_by_status.get("declined", 0)
            },
            "outgoing": {
                "total": len(outgoing_requests),
                "pending": outgoing_by_status.get("pending", 0),
                "accepted": outgoing_by_status.get("accepted", 0),
                "declined": outgoing_by_status.get("declined", 0)
            },
            "notifications": self.get_recent_requests(participant_id, limit=10)
        }
