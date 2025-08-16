from uuid import UUID
from sqlalchemy.orm import Session
from typing import List, Optional
from app.repositories.team_repository import TeamRepository
from app.repositories.participant_repository import ParticipantRepository
from app.schemas.team import TeamCreate, TeamUpdate, TeamResponse, TeamJoin
from app.schemas.participant import ParticipantResponse
from fastapi import HTTPException

class TeamService:
    def __init__(self, db: Session):
        self.db = db
        self.team_repository = TeamRepository(db)
        self.participant_repository = ParticipantRepository(db)
    
    def create_team(self, team_data: TeamCreate) -> TeamResponse:
        """Create a new team"""
        # Check if team name already exists
        existing_team = self.team_repository.get_by_name(team_data.team_name)
        if existing_team:
            raise HTTPException(
                status_code=400,
                detail="A team with this name already exists"
            )
        
        # Verify leader exists and is not in another team
        leader = self.participant_repository.get_by_id(team_data.leader_id)
        if not leader:
            raise HTTPException(
                status_code=404,
                detail="Leader participant not found"
            )
        
        if leader.team_id:
            raise HTTPException(
                status_code=400,
                detail="Leader is already part of another team"
            )
        
        # Create team
        team = self.team_repository.create(team_data)
        
        # Add leader to team
        self.team_repository.add_member(team.team_id, team_data.leader_id)
        
        # Get updated team with members
        return self.get_team(team.team_id)
    
    def get_team(self, team_id: str) -> TeamResponse:
        """Get team by ID with members"""
        team = self.team_repository.get_by_id(team_id)
        if not team:
            raise HTTPException(
                status_code=404,
                detail="Team not found"
            )
        
        # Get team members
        members = self.participant_repository.get_team_members(team_id)
        member_responses = [ParticipantResponse.from_orm(m) for m in members]
        
        # Create response with members
        team_response = TeamResponse.from_orm(team)
        team_response.members = member_responses
        
        return team_response
    
    def get_all_teams(self) -> List[TeamResponse]:
        """Get all teams with their members"""
        teams = self.team_repository.get_all()
        team_responses = []
        
        for team in teams:
            team_response = self.get_team(team.team_id)
            team_responses.append(team_response)
        
        return team_responses
    
    def update_team(self, team_id: str, team_data: TeamUpdate) -> TeamResponse:
        """Update team information"""
        team = self.team_repository.update(team_id, team_data)
        if not team:
            raise HTTPException(
                status_code=404,
                detail="Team not found"
            )
        
        # If leader is being changed, verify new leader is a team member
        if team_data.leader_id:
            new_leader = self.participant_repository.get_by_id(team_data.leader_id)
            if not new_leader or new_leader.team_id != team_id:
                raise HTTPException(
                    status_code=400,
                    detail="New leader must be a member of the team"
                )
        
        return self.get_team(team_id)
    
    def delete_team(self, team_id: str) -> bool:
        """Delete a team"""
        success = self.team_repository.delete(team_id)
        if not success:
            raise HTTPException(
                status_code=404,
                detail="Team not found"
            )
        return success
    
    def join_team(self, join_data: TeamJoin) -> TeamResponse:
        """Join an existing team"""
        # Verify team exists
        team = self.team_repository.get_by_id(join_data.team_id)
        if not team:
            raise HTTPException(
                status_code=404,
                detail="Team not found"
            )
        
        # Verify participant exists
        participant = self.participant_repository.get_by_id(join_data.participant_id)
        if not participant:
            raise HTTPException(
                status_code=404,
                detail="Participant not found"
            )
        
        # Check if participant is already in a team
        if participant.team_id:
            raise HTTPException(
                status_code=400,
                detail="Participant is already part of a team"
            )
        
        # Check if team is full
        current_size = self.team_repository.get_team_size(join_data.team_id)
        if current_size >= 4:
            raise HTTPException(
                status_code=400,
                detail="Team is already full (maximum 4 members)"
            )
        
        # Add participant to team
        success = self.team_repository.add_member(join_data.team_id, join_data.participant_id)
        if not success:
            raise HTTPException(
                status_code=400,
                detail="Failed to add participant to team"
            )
        
        return self.get_team(join_data.team_id)
    
    def leave_team(self, team_id: str, participant_id: str) -> bool:
        """Remove a participant from a team"""
        # Verify team exists
        team = self.team_repository.get_by_id(team_id)
        if not team:
            raise HTTPException(
                status_code=404,
                detail="Team not found"
            )
        
        # Check if participant is trying to leave their own team
        if team.leader_id == participant_id:
            raise HTTPException(
                status_code=400,
                detail="Team leader cannot leave the team. Transfer leadership first."
            )
        
        success = self.team_repository.remove_member(team_id, participant_id)
        if not success:
            raise HTTPException(
                status_code=400,
                detail="Failed to remove participant from team"
            )
        
        return success
    
    def transfer_leadership(self, team_id: str, new_leader_id: str) -> TeamResponse:
        """Transfer team leadership to another member"""
        # Verify team exists
        team = self.team_repository.get_by_id(team_id)
        if not team:
            raise HTTPException(
                status_code=404,
                detail="Team not found"
            )
        
        # Verify new leader is a team member
        new_leader = self.participant_repository.get_by_id(new_leader_id)
        if not new_leader or new_leader.team_id != team_id:
            raise HTTPException(
                status_code=400,
                detail="New leader must be a member of the team"
            )
        
        success = self.team_repository.transfer_leadership(team_id, new_leader_id)
        if not success:
            raise HTTPException(
                status_code=400,
                detail="Failed to transfer leadership"
            )
        
        return self.get_team(team_id)
    
    def get_team_statistics(self) -> dict:
        """Get team statistics"""
        teams = self.team_repository.get_all()
        total_teams = len(teams)
        full_teams = len(self.team_repository.get_full_teams())
        empty_teams = len(self.team_repository.get_empty_teams())
        
        return {
            "total_teams": total_teams,
            "full_teams": full_teams,
            "empty_teams": empty_teams,
            "teams_with_members": total_teams - empty_teams
        }
    
    def lock_team(self, team_id: str, leader_id: str, is_locked: bool) -> bool:
        """Lock or unlock a team"""
        return self.team_repository.lock_team(team_id, leader_id, is_locked)
    
    def toggle_team_requests(self, team_id: str, leader_id: str, is_open: bool) -> bool:
        """Toggle whether team accepts new requests"""
        return self.team_repository.toggle_team_requests(team_id, leader_id, is_open)
    
    def get_team_status(self, team_id: str) -> dict:
        """Get detailed team status and statistics"""
        team = self.team_repository.get_team_with_members(team_id)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        
        # Calculate member count
        member_count = len(team.members) if hasattr(team, 'members') else 0
        
        # Get cluster distribution
        cluster_dist = self.team_repository.get_team_cluster_distribution(team_id)
        
        return {
            "team_id": team.team_id,
            "team_name": team.team_name,
            "is_locked": team.is_locked,
            "is_open_to_requests": team.is_open_to_requests,
            "member_count": member_count,
            "max_members": team.max_members,
            "cluster_distribution": cluster_dist,
            "created_at": team.created_at
        }
