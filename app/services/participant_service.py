from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.repositories.participant_repository import ParticipantRepository
from app.schemas.participant import ParticipantCreate, ParticipantUpdate, ParticipantResponse
from fastapi import HTTPException
from passlib.context import CryptContext

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class ParticipantService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = ParticipantRepository(db)
    
    def register_participant(self, participant_data: ParticipantCreate) -> ParticipantResponse:
        """Register a new participant"""
        # Check if email already exists
        existing_participant = self.repository.get_by_email(participant_data.email)
        if existing_participant:
            raise HTTPException(
                status_code=400,
                detail="A participant with this email already exists"
            )
        
        # Check if USN already exists
        existing_usn = self.repository.get_by_usn(participant_data.usn)
        if existing_usn:
            raise HTTPException(
                status_code=400,
                detail="A participant with this USN already exists"
            )
        
        # Validate skills
        if not participant_data.skills or len(participant_data.skills) == 0:
            raise HTTPException(
                status_code=400,
                detail="At least one skill must be selected"
            )
        
        if len(participant_data.skills) > 20:
            raise HTTPException(
                status_code=400,
                detail="Maximum 20 skills allowed"
            )
        
        # Hash password
        hashed_password = pwd_context.hash(participant_data.password)
        
        # Create participant with hashed password
        participant_data_dict = participant_data.dict()
        participant_data_dict['password_hash'] = hashed_password
        del participant_data_dict['password']  # Remove plain password
        
        participant = self.repository.create(participant_data_dict)
        return ParticipantResponse.from_orm(participant)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def authenticate_participant(self, email: str, password: str) -> Optional[ParticipantResponse]:
        """Authenticate a participant with email and password"""
        participant = self.repository.get_by_email(email)
        if not participant:
            return None
        
        if not self.verify_password(password, participant.password_hash):
            return None
        
        return ParticipantResponse.from_orm(participant)
    
    def get_participant(self, participant_id: UUID) -> ParticipantResponse:
        """Get participant by ID"""
        participant = self.repository.get_by_id(participant_id)
        if not participant:
            raise HTTPException(
                status_code=404,
                detail="Participant not found"
            )
        return ParticipantResponse.from_orm(participant)
    
    def get_all_participants(self) -> List[ParticipantResponse]:
        """Get all participants"""
        participants = self.repository.get_all()
        return [ParticipantResponse.from_orm(p) for p in participants]
    
    def update_participant(self, participant_id: UUID, participant_data: ParticipantUpdate) -> ParticipantResponse:
        """Update participant information"""
        # Hash password if it's being updated
        if participant_data.password:
            participant_data_dict = participant_data.dict()
            participant_data_dict['password_hash'] = pwd_context.hash(participant_data.password)
            del participant_data_dict['password']
        else:
            participant_data_dict = participant_data.dict(exclude_unset=True)
        
        participant = self.repository.update(participant_id, participant_data_dict)
        if not participant:
            raise HTTPException(
                status_code=404,
                detail="Participant not found"
            )
        return ParticipantResponse.from_orm(participant)
    
    def delete_participant(self, participant_id: UUID) -> bool:
        """Delete a participant"""
        success = self.repository.delete(participant_id)
        if not success:
            raise HTTPException(
                status_code=404,
                detail="Participant not found"
            )
        return success
    
    def get_unassigned_participants(self) -> List[ParticipantResponse]:
        """Get participants not assigned to any team"""
        participants = self.repository.get_unassigned_participants()
        return [ParticipantResponse.from_orm(p) for p in participants]
    
    def get_participants_by_skill(self, skill: str) -> List[ParticipantResponse]:
        """Get participants by skill"""
        participants = self.repository.get_participants_by_skill(skill)
        return [ParticipantResponse.from_orm(p) for p in participants]
    
    def get_skill_distribution(self) -> dict:
        """Get distribution of participants across skills"""
        return self.repository.get_skill_distribution()
    
    def get_team_members(self, team_id: UUID) -> List[ParticipantResponse]:
        """Get all members of a specific team"""
        participants = self.repository.get_team_members(team_id)
        return [ParticipantResponse.from_orm(p) for p in participants]

    def check_email_exists(self, email: str) -> bool:
        """Check if an email already exists in the database"""
        existing_participant = self.repository.get_by_email(email)
        return existing_participant is not None

    def check_usn_exists(self, usn: str) -> bool:
        """Check if a USN already exists in the database"""
        existing_participant = self.repository.get_by_usn(usn)
        return existing_participant is not None
