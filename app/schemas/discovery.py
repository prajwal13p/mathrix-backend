from pydantic import BaseModel
from typing import List, Optional
from .participant import ParticipantResponse
from .team import TeamResponse

class TeammateSuggestion(BaseModel):
    participant: ParticipantResponse
    compatibility_score: int
    reasons: List[str]  # Why they're a good match
    department_diversity: bool
    year_diversity: bool
    interest_complement: bool

class TeamDiscovery(BaseModel):
    team: TeamResponse
    open_slots: int
    compatibility_score: int
    reasons: List[str]

class DiscoveryFilters(BaseModel):
    interest_cluster: Optional[int] = None
    department: Optional[str] = None
    year: Optional[int] = None
    max_team_size: Optional[str] = None
    include_locked_teams: bool = False

class DiscoveryResponse(BaseModel):
    potential_teammates: List[TeammateSuggestion]
    available_teams: List[TeamDiscovery]
    total_participants: int
    total_teams: int
