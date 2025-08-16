from pydantic import BaseModel, EmailStr
from app.schemas.participant import ParticipantResponse

class LoginRequest(BaseModel):
    email: EmailStr

class LoginResponse(BaseModel):
    participant: ParticipantResponse
    message: str

class TeamCreationRequest(BaseModel):
    team_name: str
    leader_email: EmailStr
