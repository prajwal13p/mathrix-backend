from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import HTTPException
from app.repositories.team_request_repository import TeamRequestRepository
from app.repositories.participant_repository import ParticipantRepository
from app.repositories.team_repository import TeamRepository
from app.schemas.team_request import TeamRequestCreate, TeamRequestResponse, TeamRequestUpdate, TeamRequestResponseResult
from app.schemas.team import TeamResponse, TeamCreate
from app.models.team_request import TeamRequest
from datetime import datetime

class TeamRequestService:
    def __init__(self, db: Session):
        self.db = db
        self.request_repository = TeamRequestRepository(db)
        self.participant_repository = ParticipantRepository(db)
        self.team_repository = TeamRepository(db)
    
    def send_request(self, from_participant_id: str, request_data: TeamRequestCreate) -> TeamRequestResponse:
        """Send a team request to another participant"""
        
        # Check if from_participant exists
        from_participant = self.participant_repository.get_by_id(from_participant_id)
        if not from_participant:
            raise HTTPException(status_code=404, detail="From participant not found")
        
        # Check if to_participant exists
        to_participant = self.participant_repository.get_by_id(request_data.to_participant_id)
        if not to_participant:
            raise HTTPException(status_code=404, detail="To participant not found")
        
        # Check if request already exists
        existing_request = self.request_repository.get_existing_request(
            from_participant_id, request_data.to_participant_id
        )
        if existing_request:
            raise HTTPException(status_code=400, detail="Request already sent to this participant")
        
        # If joining existing team, verify team exists and is open
        if request_data.team_id:
            team = self.team_repository.get_by_id(request_data.team_id)
            if not team:
                raise HTTPException(status_code=404, detail="Team not found")
            if team.is_locked:
                raise HTTPException(status_code=400, detail="Team is locked and not accepting new members")
            if not team.is_open_to_requests:
                raise HTTPException(status_code=400, detail="Team is not accepting new requests")
        
        # Create request
        request = self.request_repository.create(
            from_participant_id=from_participant_id,
            to_participant_id=request_data.to_participant_id,
            team_id=request_data.team_id,
            message=request_data.message
        )
        
        return TeamRequestResponse.from_orm(request)
    
    def respond_to_request(self, request_id: str, to_participant_id: str, response: TeamRequestUpdate) -> TeamRequestResponseResult:
        """Respond to a team request (accept/decline)"""
        
        request = self.request_repository.get_by_id(request_id)
        if not request:
            raise HTTPException(status_code=404, detail="Request not found")
        
        if request.to_participant_id != to_participant_id:
            raise HTTPException(status_code=403, detail="Not authorized to respond to this request")
        
        if request.status != "pending":
            raise HTTPException(status_code=400, detail="Request already responded to")
        
        # Update request status
        self.request_repository.update_status(request_id, response.status, datetime.now())
        
        if response.status == "accepted":
            # Handle team formation logic
            team = self._handle_team_formation(request)
            return TeamRequestResponseResult(
                success=True,
                message="Team request accepted successfully",
                team=team,
                request_id=request_id,
                status="accepted"
            )
        else:
            # Request declined
            return TeamRequestResponseResult(
                success=True,
                message="Team request declined",
                team=None,
                request_id=request_id,
                status="declined"
            )
    
    def _handle_team_formation(self, request: TeamRequest) -> TeamResponse:
        """Handle team formation when request is accepted"""
        
        if request.team_id:
            # Joining existing team
            team = self.team_repository.get_by_id(request.team_id)
            if team:
                # Add participant to team
                self.team_repository.add_member(team.team_id, request.from_participant_id)
                return self.team_repository.get_team_with_members(team.team_id)
        else:
            # Creating new team with both participants
            from_participant = self.participant_repository.get_by_id(request.from_participant_id)
            to_participant = self.participant_repository.get_by_id(request.to_participant_id)
            
            # Create team with from_participant as leader
            team_data = TeamCreate(
                team_name=f"Team {from_participant.name} & {to_participant.name}",
                leader_id=request.from_participant_id,
                description=f"Team formed by {from_participant.name} and {to_participant.name}",
                max_members="4"
            )
            
            team = self.team_repository.create(team_data)
            
            # Add both participants to team
            self.team_repository.add_member(team.team_id, request.from_participant_id)
            self.team_repository.add_member(team.team_id, request.to_participant_id)
            
            return self.team_repository.get_team_with_members(team.team_id)
    
    def get_user_requests(self, participant_id: str) -> dict:
        """Get all requests for a participant (incoming and outgoing)"""
        
        incoming = self.request_repository.get_incoming_requests(participant_id)
        outgoing = self.request_repository.get_outgoing_requests(participant_id)
        
        return {
            "incoming_requests": [TeamRequestResponse.from_orm(req) for req in incoming],
            "outgoing_requests": [TeamRequestResponse.from_orm(req) for req in outgoing]
        }
    
    def cancel_request(self, request_id: str, from_participant_id: str) -> bool:
        """Cancel a sent request"""
        
        request = self.request_repository.get_by_id(request_id)
        if not request:
            raise HTTPException(status_code=404, detail="Request not found")
        
        if request.from_participant_id != from_participant_id:
            raise HTTPException(status_code=403, detail="Not authorized to cancel this request")
        
        if request.status != "pending":
            raise HTTPException(status_code=400, detail="Cannot cancel responded request")
        
        return self.request_repository.delete(request_id)
