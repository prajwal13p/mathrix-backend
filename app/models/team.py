from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

class Team(Base):
    __tablename__ = "teams"
    
    team_id = Column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    team_name = Column(String(100), nullable=False, unique=True)
    leader_id = Column(UUID(as_uuid=False), ForeignKey("participants.participant_id"), nullable=False)
    description = Column(Text, nullable=True)  # Team bio/description
    is_locked = Column(Boolean, default=False)  # Team lock status
    is_open_to_requests = Column(Boolean, default=True)  # Accepting new members
    max_members = Column(String(10), default="4")  # Flexible team size
    tags = Column(String(200), nullable=True)  # Team tags (comma-separated)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    leader = relationship("Participant", foreign_keys=[leader_id])
    members = relationship("Participant", back_populates="team", foreign_keys="Participant.team_id")
    
    def __repr__(self):
        return f"<Team(name='{self.team_name}', leader_id='{self.leader_id}', locked={self.is_locked})>"
