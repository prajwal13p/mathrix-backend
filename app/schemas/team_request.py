from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from .participant import ParticipantResponse
from .team import TeamResponse

class TeamRequestCreate(BaseModel):
    to_participant_id: str
    team_id: Optional[str] = None  # If joining existing team
    message: Optional[str] = None

class TeamRequestResponse(BaseModel):
    request_id: str
    from_participant: ParticipantResponse
    to_participant: ParticipantResponse
    team_id: Optional[str] = None
    message: Optional[str] = None
    status: str
    created_at: datetime
    responded_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class TeamRequestUpdate(BaseModel):
    status: str  # accept, decline

class TeamRequestList(BaseModel):
    incoming_requests: List[TeamRequestResponse]
    outgoing_requests: List[TeamRequestResponse]

class TeamRequestResponseResult(BaseModel):
    success: bool
    message: str
    team: Optional[TeamResponse] = None
    request_id: str
    status: str
