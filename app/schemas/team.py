from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from .participant import ParticipantResponse

class TeamBase(BaseModel):
    team_name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    max_members: Optional[str] = "4"
    tags: Optional[str] = None

class TeamCreate(TeamBase):
    leader_id: str

class TeamUpdate(BaseModel):
    team_name: Optional[str] = Field(None, min_length=1, max_length=100)
    leader_id: Optional[str] = None
    description: Optional[str] = None
    max_members: Optional[str] = None
    tags: Optional[str] = None
    is_open_to_requests: Optional[bool] = None

class TeamResponse(TeamBase):
    team_id: str
    leader_id: str
    is_locked: bool = False
    is_open_to_requests: bool = True
    created_at: datetime
    members: List[ParticipantResponse] = []
    member_count: int = 0
    
    class Config:
        from_attributes = True

class TeamJoin(BaseModel):
    team_id: str
    participant_id: str

class TeamLock(BaseModel):
    is_locked: bool
