from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

class Participant(Base):
    __tablename__ = "participants"
    
    participant_id = Column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    usn = Column(String(20), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    skills = Column(JSON, nullable=False)  # Store skills as JSON array
    team_id = Column(UUID(as_uuid=False), ForeignKey("teams.team_id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    team = relationship("Team", back_populates="members", foreign_keys=[team_id])
    
    def __repr__(self):
        return f"<Participant(name='{self.name}', email='{self.email}', usn='{self.usn}')>"
