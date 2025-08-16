from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.services.discovery_service import DiscoveryService
from app.services.team_request_service import TeamRequestService
from app.services.team_service import TeamService
from app.services.notification_service import NotificationService
from app.schemas.discovery import DiscoveryFilters, DiscoveryResponse
from app.schemas.team_request import TeamRequestCreate, TeamRequestResponse, TeamRequestUpdate, TeamRequestResponseResult
from app.schemas.team import TeamResponse, TeamLock
from app.schemas.auth import TeamCreationRequest

router = APIRouter()

@router.get("/discover/{participant_id}", response_model=DiscoveryResponse)
async def discover_teammates(
    participant_id: str,
    interest_cluster: int = None,
    department: str = None,
    year: int = None,
    max_team_size: str = None,
    include_locked_teams: bool = False,
    db: Session = Depends(get_db)
):
    """Discover potential teammates and available teams"""
    service = DiscoveryService(db)
    
    filters = DiscoveryFilters(
        interest_cluster=interest_cluster,
        department=department,
        year=year,
        max_team_size=max_team_size,
        include_locked_teams=include_locked_teams
    )
    
    return service.discover_teammates(participant_id, filters)

@router.post("/send-request/{from_participant_id}", response_model=TeamRequestResponse)
async def send_team_request(
    from_participant_id: str,
    request_data: TeamRequestCreate,
    db: Session = Depends(get_db)
):
    """Send a team request to another participant"""
    service = TeamRequestService(db)
    return service.send_request(from_participant_id, request_data)

@router.post("/respond-request/{request_id}/{to_participant_id}", response_model=TeamRequestResponseResult)
async def respond_to_request(
    request_id: str,
    to_participant_id: str,
    response: TeamRequestUpdate,
    db: Session = Depends(get_db)
):
    """Respond to a team request (accept/decline)"""
    service = TeamRequestService(db)
    return service.respond_to_request(request_id, to_participant_id, response)

@router.get("/requests/{participant_id}")
async def get_user_requests(
    participant_id: str,
    db: Session = Depends(get_db)
):
    """Get all requests for a participant"""
    service = TeamRequestService(db)
    return service.get_user_requests(participant_id)

@router.delete("/cancel-request/{request_id}/{from_participant_id}")
async def cancel_request(
    request_id: str,
    from_participant_id: str,
    db: Session = Depends(get_db)
):
    """Cancel a sent request"""
    service = TeamRequestService(db)
    return service.cancel_request(request_id, from_participant_id)

@router.post("/lock-team/{team_id}/{leader_id}")
async def lock_team(
    team_id: str,
    leader_id: str,
    lock_data: TeamLock,
    db: Session = Depends(get_db)
):
    """Lock/unlock a team (only leader can do this)"""
    service = TeamService(db)
    return service.lock_team(team_id, leader_id, lock_data.is_locked)

@router.post("/toggle-requests/{team_id}/{leader_id}")
async def toggle_team_requests(
    team_id: str,
    leader_id: str,
    is_open: bool,
    db: Session = Depends(get_db)
):
    """Toggle whether team accepts new requests"""
    service = TeamService(db)
    return service.toggle_team_requests(team_id, leader_id, is_open)

@router.get("/team-status/{team_id}")
async def get_team_status(
    team_id: str,
    db: Session = Depends(get_db)
):
    """Get detailed team status and statistics"""
    service = TeamService(db)
    return service.get_team_status(team_id)

@router.get("/notifications/{participant_id}")
async def get_notifications(
    participant_id: str,
    db: Session = Depends(get_db)
):
    """Get notification summary and recent requests"""
    service = NotificationService(db)
    return service.get_request_summary(participant_id)

@router.get("/unread-count/{participant_id}")
async def get_unread_count(
    participant_id: str,
    db: Session = Depends(get_db)
):
    """Get count of unread team requests"""
    service = NotificationService(db)
    return {"unread_count": service.get_unread_request_count(participant_id)}
