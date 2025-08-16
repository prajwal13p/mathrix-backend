from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional, Dict
from uuid import UUID
from app.models.participant import Participant
from app.models.team import Team

class ParticipantRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, participant_data: dict) -> Participant:
        db_participant = Participant(**participant_data)
        self.db.add(db_participant)
        self.db.commit()
        self.db.refresh(db_participant)
        return db_participant
    
    def get_by_id(self, participant_id: UUID) -> Optional[Participant]:
        return self.db.query(Participant).filter(Participant.participant_id == str(participant_id)).first()
    
    def get_by_email(self, email: str) -> Optional[Participant]:
        return self.db.query(Participant).filter(Participant.email == email).first()
    
    def get_by_usn(self, usn: str) -> Optional[Participant]:
        return self.db.query(Participant).filter(Participant.usn == usn).first()
    
    def get_all(self) -> List[Participant]:
        return self.db.query(Participant).all()
    
    def update(self, participant_id: UUID, participant_data: dict) -> Optional[Participant]:
        participant = self.get_by_id(participant_id)
        if participant:
            for field, value in participant_data.items():
                setattr(participant, field, value)
            self.db.commit()
            self.db.refresh(participant)
        return participant
    
    def delete(self, participant_id: UUID) -> bool:
        participant = self.get_by_id(participant_id)
        if participant:
            self.db.delete(participant)
            self.db.commit()
            return True
        return False
    
    def get_unassigned_participants(self) -> List[Participant]:
        return self.db.query(Participant).filter(Participant.team_id.is_(None)).all()
    
    def get_available_participants(self) -> List[Participant]:
        """Get all participants who can join teams (not in locked teams)"""
        return self.db.query(Participant).filter(
            or_(
                Participant.team_id.is_(None),
                Participant.team_id.in_(
                    self.db.query(Team.team_id).filter(Team.is_locked == False)
                )
            )
        ).all()
    
    def get_participants_by_skill(self, skill: str) -> List[Participant]:
        """Get participants who have a specific skill"""
        return self.db.query(Participant).filter(
            and_(
                Participant.skills.contains([skill]),
                Participant.team_id.is_(None)
            )
        ).all()
    
    def get_team_members(self, team_id: str) -> List[Participant]:
        return self.db.query(Participant).filter(Participant.team_id == team_id).all()
    
    def get_skill_distribution(self) -> Dict[str, int]:
        """Get count of participants by skill"""
        # This is a simplified approach - in production you might want to use a more sophisticated method
        # for counting JSON array elements
        all_participants = self.get_all()
        skill_counts = {}
        
        for participant in all_participants:
            if participant.skills:
                for skill in participant.skills:
                    skill_counts[skill] = skill_counts.get(skill, 0) + 1
        
        return skill_counts
    
    def get_suggestions_for_participant(self, participant_id: UUID, max_suggestions: int = 5) -> List[Participant]:
        """Get teammate suggestions based on skill diversity"""
        participant = self.get_by_id(participant_id)
        if not participant:
            return []
        
        # Get current team members' skills
        current_skills = set()
        if participant.team_id:
            team_members = self.get_team_members(participant.team_id)
            for member in team_members:
                if member.skills:
                    current_skills.update(member.skills)
        
        # Add participant's own skills
        if participant.skills:
            current_skills.update(participant.skills)
        
        # Find participants with different skills
        available_participants = self.get_unassigned_participants()
        suggestions = []
        
        for available_participant in available_participants:
            if available_participant.participant_id == participant.participant_id:
                continue
                
            # Calculate skill diversity score
            if available_participant.skills:
                new_skills = set(available_participant.skills) - current_skills
                diversity_score = len(new_skills)
                
                if diversity_score > 0:
                    suggestions.append((available_participant, diversity_score))
        
        # Sort by diversity score and return top suggestions
        suggestions.sort(key=lambda x: x[1], reverse=True)
        return [participant for participant, _ in suggestions[:max_suggestions]]
    
    def get_participants_with_skill_overlap(self, participant_id: UUID, min_overlap: int = 1) -> List[Participant]:
        """Get participants with skill overlap for team formation"""
        participant = self.get_by_id(participant_id)
        if not participant or not participant.skills:
            return []
        
        available_participants = self.get_unassigned_participants()
        suggestions = []
        
        for available_participant in available_participants:
            if available_participant.participant_id == participant.participant_id:
                continue
                
            if available_participant.skills:
                overlap = len(set(participant.skills) & set(available_participant.skills))
                if overlap >= min_overlap:
                    suggestions.append((available_participant, overlap))
        
        # Sort by overlap score
        suggestions.sort(key=lambda x: x[1], reverse=True)
        return [participant for participant, _ in suggestions]
