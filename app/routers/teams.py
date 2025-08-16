from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from typing import Union
from app.core.database import get_db
from app.services.team_service import TeamService
from app.services.participant_service import ParticipantService
from app.schemas.team import TeamCreate, TeamResponse, TeamUpdate, TeamJoin
from app.schemas.auth import TeamCreationRequest

router = APIRouter()

@router.post("/create-by-email", response_model=TeamResponse)
async def create_team_by_email(
    team_data: TeamCreationRequest,
    db: Session = Depends(get_db)
):
    """Create a new team using participant email"""
    participant_service = ParticipantService(db)
    team_service = TeamService(db)
    
    # Find participant by email
    participant = participant_service.repository.get_by_email(team_data.leader_email)
    if not participant:
        raise HTTPException(
            status_code=404,
            detail="Participant not found with this email"
        )
    
    # Check if participant is already in a team
    if participant.team_id:
        raise HTTPException(
            status_code=400,
            detail="Participant is already part of a team"
        )
    
    # Create team data
    team_create_data = TeamCreate(
        team_name=team_data.team_name,
        leader_id=participant.participant_id
    )
    
    return team_service.create_team(team_create_data)

@router.post("/create", response_model=TeamResponse)
async def create_team(
    team_data: TeamCreate,
    db: Session = Depends(get_db)
):
    """Create a new team"""
    service = TeamService(db)
    return service.create_team(team_data)

@router.get("/{team_id}", response_model=TeamResponse)
async def get_team(
    team_id: str,
    db: Session = Depends(get_db)
):
    """Get team by ID with members"""
    service = TeamService(db)
    return service.get_team(team_id)

@router.get("/", response_model=List[TeamResponse])
async def get_all_teams(
    db: Session = Depends(get_db)
):
    """Get all teams with their members"""
    service = TeamService(db)
    return service.get_all_teams()

@router.put("/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: str,
    team_data: TeamUpdate,
    db: Session = Depends(get_db)
):
    """Update team information"""
    service = TeamService(db)
    return service.update_team(team_id, team_data)

@router.delete("/{team_id}")
async def delete_team(
    team_id: str,
    db: Session = Depends(get_db)
):
    """Delete a team"""
    service = TeamService(db)
    return service.delete_team(team_id)

@router.post("/join", response_model=TeamResponse)
async def join_team(
    join_data: TeamJoin,
    db: Session = Depends(get_db)
):
    """Join an existing team"""
    service = TeamService(db)
    return service.join_team(join_data)

@router.post("/{team_id}/leave/{participant_id}")
async def leave_team(
    team_id: str,
    participant_id: str,
    db: Session = Depends(get_db)
):
    """Remove a participant from a team"""
    service = TeamService(db)
    return service.leave_team(team_id, participant_id)

@router.post("/{team_id}/transfer-leadership/{new_leader_id}", response_model=TeamResponse)
async def transfer_leadership(
    team_id: str,
    new_leader_id: str,
    db: Session = Depends(get_db)
):
    """Transfer team leadership to another member"""
    service = TeamService(db)
    return service.transfer_leadership(team_id, new_leader_id)

@router.get("/statistics/overview")
async def get_team_statistics(
    db: Session = Depends(get_db)
):
    """Get team statistics overview"""
    service = TeamService(db)
    return service.get_team_statistics()
