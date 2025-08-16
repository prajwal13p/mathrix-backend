from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List, Optional, Dict
from app.models.team import Team
from app.models.participant import Participant
from app.schemas.team import TeamCreate, TeamUpdate

class TeamRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, team_data: TeamCreate) -> Team:
        db_team = Team(**team_data.dict())
        self.db.add(db_team)
        self.db.commit()
        self.db.refresh(db_team)
        return db_team
    
    def get_by_id(self, team_id: str) -> Optional[Team]:
        return self.db.query(Team).filter(Team.team_id == team_id).first()
    
    def get_by_name(self, team_name: str) -> Optional[Team]:
        return self.db.query(Team).filter(Team.team_name == team_name).first()
    
    def get_all(self) -> List[Team]:
        return self.db.query(Team).all()
    
    def update(self, team_id: str, team_data: TeamUpdate) -> Optional[Team]:
        team = self.get_by_id(team_id)
        if team:
            update_data = team_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(team, field, value)
            self.db.commit()
            self.db.refresh(team)
        return team
    
    def delete(self, team_id: str) -> bool:
        team = self.get_by_id(team_id)
        if team:
            # Remove team_id from all members
            self.db.query(Participant).filter(
                Participant.team_id == team_id
            ).update({Participant.team_id: None})
            
            self.db.delete(team)
            self.db.commit()
            return True
        return False
    
    def add_member(self, team_id: str, participant_id: str) -> bool:
        """Add a participant to a team"""
        team = self.get_by_id(team_id)
        participant = self.db.query(Participant).filter(
            Participant.participant_id == participant_id
        ).first()
        
        if not team or not participant:
            return False
        
        # Check if team is full (max 4 members)
        current_members = self.db.query(Participant).filter(
            Participant.team_id == team_id
        ).count()
        
        if current_members >= 4:
            return False
        
        # Check if participant is already in a team
        if participant.team_id:
            return False
        
        participant.team_id = team_id
        self.db.commit()
        return True
    
    def remove_member(self, team_id: str, participant_id: str) -> bool:
        """Remove a participant from a team"""
        participant = self.db.query(Participant).filter(
            and_(
                Participant.participant_id == participant_id,
                Participant.team_id == team_id
            )
        ).first()
        
        if not participant:
            return False
        
        participant.team_id = None
        self.db.commit()
        return True
    
    def transfer_leadership(self, team_id: str, new_leader_id: str) -> bool:
        """Transfer team leadership to another member"""
        team = self.get_by_id(team_id)
        new_leader = self.db.query(Participant).filter(
            and_(
                Participant.participant_id == new_leader_id,
                Participant.team_id == team_id
            )
        ).first()
        
        if not team or not new_leader:
            return False
        
        team.leader_id = new_leader_id
        self.db.commit()
        return True
    
    def get_team_size(self, team_id: str) -> int:
        """Get current number of members in a team"""
        return self.db.query(Participant).filter(
            Participant.team_id == team_id
        ).count()
    
    def get_teams_by_size(self, size: int) -> List[Team]:
        """Get teams with specific number of members"""
        teams = self.get_all()
        return [team for team in teams if self.get_team_size(team.team_id) == size]
    
    def get_empty_teams(self) -> List[Team]:
        """Get teams with no members"""
        return self.get_teams_by_size(0)
    
    def get_full_teams(self) -> List[Team]:
        """Get teams with 4 members"""
        return self.get_teams_by_size(4)
    
    def get_team_cluster_distribution(self, team_id: str) -> Dict[int, int]:
        """Get interest cluster distribution within a team"""
        members = self.db.query(Participant).filter(
            Participant.team_id == team_id
        ).all()
        
        distribution = {}
        for member in members:
            cluster = member.interest_cluster
            distribution[cluster] = distribution.get(cluster, 0) + 1
        
        return distribution
    
    def get_open_teams(self) -> List[Team]:
        """Get teams that are open to new requests"""
        return self.db.query(Team).filter(
            and_(
                Team.is_locked == False,
                Team.is_open_to_requests == True
            )
        ).all()
    
    def get_team_with_members(self, team_id: str) -> Optional[Team]:
        """Get team with all its members loaded"""
        team = self.get_by_id(team_id)
        if team:
            # Load members
            team.members = self.db.query(Participant).filter(
                Participant.team_id == team_id
            ).all()
        return team
    
    def count_all(self) -> int:
        """Get total count of all teams"""
        return self.db.query(Team).count()
    
    def lock_team(self, team_id: str, leader_id: str, is_locked: bool) -> bool:
        """Lock or unlock a team (only leader can do this)"""
        team = self.get_by_id(team_id)
        if team and team.leader_id == leader_id:
            team.is_locked = is_locked
            self.db.commit()
            return True
        return False
    
    def toggle_team_requests(self, team_id: str, leader_id: str, is_open: bool) -> bool:
        """Toggle whether team accepts new requests"""
        team = self.get_by_id(team_id)
        if team and team.leader_id == leader_id:
            team.is_open_to_requests = is_open
            self.db.commit()
            return True
        return False
