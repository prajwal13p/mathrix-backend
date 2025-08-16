from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.core.database import get_db
from app.services.participant_service import ParticipantService
from app.services.suggestion_service import SuggestionService
from app.schemas.participant import ParticipantCreate, ParticipantResponse, ParticipantUpdate
from app.schemas.suggestion import SuggestionResponse

router = APIRouter()

@router.post("/register", response_model=ParticipantResponse)
async def register_participant(
    participant_data: ParticipantCreate,
    db: Session = Depends(get_db)
):
    """Register a new participant"""
    service = ParticipantService(db)
    return service.register_participant(participant_data)

@router.get("/check-email/{email}")
async def check_email_exists(
    email: str,
    db: Session = Depends(get_db)
):
    """Check if an email already exists in the database"""
    try:
        service = ParticipantService(db)
        exists = service.check_email_exists(email)
        return {"exists": exists}
    except Exception as e:
        print(f"Error in check_email_exists: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/check-usn/{usn}")
async def check_usn_exists(
    usn: str,
    db: Session = Depends(get_db)
):
    """Check if a USN already exists in the database"""
    try:
        service = ParticipantService(db)
        exists = service.check_usn_exists(usn)
        return {"exists": exists}
    except Exception as e:
        print(f"Error in check_usn_exists: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/{participant_id}", response_model=ParticipantResponse)
async def get_participant(
    participant_id: UUID,
    db: Session = Depends(get_db)
):
    """Get participant by ID"""
    service = ParticipantService(db)
    return service.get_participant(participant_id)

@router.get("/", response_model=List[ParticipantResponse])
async def get_all_participants(
    db: Session = Depends(get_db)
):
    """Get all participants"""
    service = ParticipantService(db)
    return service.get_all_participants()

@router.put("/{participant_id}", response_model=ParticipantResponse)
async def update_participant(
    participant_id: UUID,
    participant_data: ParticipantUpdate,
    db: Session = Depends(get_db)
):
    """Update participant information"""
    service = ParticipantService(db)
    return service.update_participant(participant_id, participant_data)

@router.delete("/{participant_id}")
async def delete_participant(
    participant_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a participant"""
    service = ParticipantService(db)
    return service.delete_participant(participant_id)

@router.get("/unassigned/", response_model=List[ParticipantResponse])
async def get_unassigned_participants(
    db: Session = Depends(get_db)
):
    """Get participants not assigned to any team"""
    service = ParticipantService(db)
    return service.get_unassigned_participants()

@router.get("/skill/{skill}", response_model=List[ParticipantResponse])
async def get_participants_by_skill(
    skill: str,
    db: Session = Depends(get_db)
):
    """Get participants by skill"""
    service = ParticipantService(db)
    return service.get_participants_by_skill(skill)

@router.get("/skills/distribution")
async def get_skill_distribution(
    db: Session = Depends(get_db)
):
    """Get distribution of participants across skills"""
    service = ParticipantService(db)
    return service.get_skill_distribution()

@router.get("/{participant_id}/suggestions", response_model=SuggestionResponse)
async def get_teammate_suggestions(
    participant_id: UUID,
    max_suggestions: int = 5,
    db: Session = Depends(get_db)
):
    """Get teammate suggestions for a participant"""
    service = SuggestionService(db)
    return service.get_teammate_suggestions(participant_id, max_suggestions)
