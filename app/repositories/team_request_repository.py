from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.team_request import TeamRequest
from datetime import datetime

class TeamRequestRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, from_participant_id: str, to_participant_id: str, team_id: Optional[str] = None, message: Optional[str] = None) -> TeamRequest:
        """Create a new team request"""
        request = TeamRequest(
            from_participant_id=from_participant_id,
            to_participant_id=to_participant_id,
            team_id=team_id,
            message=message
        )
        self.db.add(request)
        self.db.commit()
        self.db.refresh(request)
        return request
    
    def get_by_id(self, request_id: str) -> Optional[TeamRequest]:
        """Get team request by ID"""
        return self.db.query(TeamRequest).filter(TeamRequest.request_id == request_id).first()
    
    def get_existing_request(self, from_participant_id: str, to_participant_id: str) -> Optional[TeamRequest]:
        """Check if a request already exists between two participants"""
        return self.db.query(TeamRequest).filter(
            TeamRequest.from_participant_id == from_participant_id,
            TeamRequest.to_participant_id == to_participant_id,
            TeamRequest.status == "pending"
        ).first()
    
    def get_incoming_requests(self, participant_id: str) -> List[TeamRequest]:
        """Get all incoming requests for a participant"""
        return self.db.query(TeamRequest).filter(
            TeamRequest.to_participant_id == participant_id
        ).order_by(TeamRequest.created_at.desc()).all()
    
    def get_outgoing_requests(self, participant_id: str) -> List[TeamRequest]:
        """Get all outgoing requests from a participant"""
        return self.db.query(TeamRequest).filter(
            TeamRequest.from_participant_id == participant_id
        ).order_by(TeamRequest.created_at.desc()).all()
    
    def update_status(self, request_id: str, status: str, responded_at: datetime) -> bool:
        """Update request status and response time"""
        request = self.get_by_id(request_id)
        if request:
            request.status = status
            request.responded_at = responded_at
            self.db.commit()
            return True
        return False
    
    def delete(self, request_id: str) -> bool:
        """Delete a team request"""
        request = self.get_by_id(request_id)
        if request:
            self.db.delete(request)
            self.db.commit()
            return True
        return False
    
    def get_pending_requests_for_team(self, team_id: str) -> List[TeamRequest]:
        """Get all pending requests for a specific team"""
        return self.db.query(TeamRequest).filter(
            TeamRequest.team_id == team_id,
            TeamRequest.status == "pending"
        ).all()
    
    def cleanup_expired_requests(self, days: int = 7) -> int:
        """Clean up requests older than specified days"""
        from datetime import timedelta
        cutoff_date = datetime.now() - timedelta(days=days)
        
        expired_requests = self.db.query(TeamRequest).filter(
            TeamRequest.created_at < cutoff_date,
            TeamRequest.status == "pending"
        ).all()
        
        count = len(expired_requests)
        for request in expired_requests:
            request.status = "expired"
        
        self.db.commit()
        return count
