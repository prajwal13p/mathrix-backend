from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.core.database import get_db
from app.services.participant_service import ParticipantService
from app.services.team_service import TeamService
from app.services.suggestion_service import SuggestionService
from app.schemas.participant import ParticipantResponse
from app.schemas.team import TeamResponse

router = APIRouter()

@router.get("/participants", response_model=List[ParticipantResponse])
async def get_all_participants(
    db: Session = Depends(get_db)
):
    """Get all participants (admin view)"""
    service = ParticipantService(db)
    return service.get_all_participants()

@router.get("/teams", response_model=List[TeamResponse])
async def get_all_teams(
    db: Session = Depends(get_db)
):
    """Get all teams (admin view)"""
    service = TeamService(db)
    return service.get_all_teams()

@router.get("/participants/unassigned", response_model=List[ParticipantResponse])
async def get_unassigned_participants(
    db: Session = Depends(get_db)
):
    """Get participants not assigned to any team"""
    service = ParticipantService(db)
    return service.get_unassigned_participants()

@router.get("/participants/cluster-distribution")
async def get_cluster_distribution(
    db: Session = Depends(get_db)
):
    """Get distribution of participants across interest clusters"""
    service = ParticipantService(db)
    return service.get_cluster_distribution()

@router.get("/teams/statistics")
async def get_team_statistics(
    db: Session = Depends(get_db)
):
    """Get team statistics overview"""
    service = TeamService(db)
    return service.get_team_statistics()

@router.get("/auto-assign-suggestions")
async def get_auto_team_suggestions(
    db: Session = Depends(get_db)
):
    """Get suggestions for automatic team formation"""
    service = SuggestionService(db)
    return service.get_auto_team_suggestions()

@router.post("/auto-assign-teams")
async def auto_assign_teams(
    db: Session = Depends(get_db)
):
    """Automatically assign participants to teams based on diversity"""
    # This is a placeholder for the auto-assignment logic
    # In a real implementation, this would use the suggestion service
    # to create balanced teams
    
    suggestion_service = SuggestionService(db)
    suggestions = suggestion_service.get_auto_team_suggestions()
    
    if suggestions["total_participants"] < 4:
        raise HTTPException(
            status_code=400,
            detail="Not enough participants to form teams"
        )
    
    # For now, return the suggestions
    # TODO: Implement actual auto-assignment algorithm
    return {
        "message": "Auto-assignment suggestions generated",
        "suggestions": suggestions,
        "note": "Actual auto-assignment not yet implemented"
    }

@router.get("/system-overview")
async def get_system_overview(
    db: Session = Depends(get_db)
):
    """Get comprehensive system overview"""
    participant_service = ParticipantService(db)
    team_service = TeamService(db)
    suggestion_service = SuggestionService(db)
    
    # Get all statistics
    total_participants = len(participant_service.get_all_participants())
    unassigned_participants = len(participant_service.get_unassigned_participants())
    total_teams = len(team_service.get_all_teams())
    cluster_distribution = participant_service.get_cluster_distribution()
    team_stats = team_service.get_team_statistics()
    auto_suggestions = suggestion_service.get_auto_team_suggestions()
    
    return {
        "participants": {
            "total": total_participants,
            "unassigned": unassigned_participants,
            "assigned": total_participants - unassigned_participants,
            "cluster_distribution": cluster_distribution
        },
        "teams": {
            "total": total_teams,
            "statistics": team_stats
        },
        "auto_assignment": auto_suggestions,
        "system_status": "operational"
    }
