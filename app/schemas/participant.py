from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class ParticipantBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    usn: str = Field(..., min_length=5, max_length=20)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    skills: List[str] = Field(..., min_items=1, max_items=20)

class ParticipantCreate(ParticipantBase):
    pass

class ParticipantUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    usn: Optional[str] = Field(None, min_length=5, max_length=20)
    password: Optional[str] = Field(None, min_length=6, max_length=100)
    skills: Optional[List[str]] = Field(None, min_items=1, max_items=20)

class ParticipantResponse(BaseModel):
    participant_id: UUID
    name: str
    usn: str
    email: str
    skills: List[str]
    team_id: Optional[UUID] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class ParticipantLogin(BaseModel):
    email: EmailStr
    password: str
