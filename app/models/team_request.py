from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

class TeamRequest(Base):
    __tablename__ = "team_requests"
    
    request_id = Column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    from_participant_id = Column(UUID(as_uuid=False), ForeignKey("participants.participant_id"), nullable=False)
    to_participant_id = Column(UUID(as_uuid=False), ForeignKey("participants.participant_id"), nullable=False)
    team_id = Column(UUID(as_uuid=False), ForeignKey("teams.team_id"), nullable=True)  # If joining existing team
    message = Column(Text, nullable=True)  # Custom message from requester
    status = Column(String(20), default="pending")  # pending, accepted, declined, expired
    created_at = Column(DateTime, server_default=func.now())
    responded_at = Column(DateTime, nullable=True)
    
    # Relationships
    from_participant = relationship("Participant", foreign_keys=[from_participant_id])
    to_participant = relationship("Participant", foreign_keys=[to_participant_id])
    team = relationship("Team", foreign_keys=[team_id])
    
    def __repr__(self):
        return f"<TeamRequest(from='{self.from_participant_id}', to='{self.to_participant_id}', status='{self.status}')>"
