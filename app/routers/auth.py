from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.participant_service import ParticipantService
from app.schemas.auth import LoginRequest, LoginResponse
from app.schemas.participant import ParticipantResponse, ParticipantLogin

router = APIRouter()

@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: ParticipantLogin,
    db: Session = Depends(get_db)
):
    """Login for registered participants using email and password"""
    service = ParticipantService(db)
    
    # Authenticate participant with email and password
    participant = service.authenticate_participant(login_data.email, login_data.password)
    if not participant:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    
    return LoginResponse(
        participant=participant,
        message="Login successful"
    )

@router.get("/profile/{email}", response_model=ParticipantResponse)
async def get_profile_by_email(
    email: str,
    db: Session = Depends(get_db)
):
    """Get participant profile by email"""
    service = ParticipantService(db)
    participant = service.repository.get_by_email(email)
    
    if not participant:
        raise HTTPException(
            status_code=404,
            detail="Participant not found"
        )
    
    return ParticipantResponse.from_orm(participant)
