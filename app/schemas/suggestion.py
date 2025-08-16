from pydantic import BaseModel
from typing import List
from uuid import UUID
from .participant import ParticipantResponse

class TeammateSuggestion(BaseModel):
    participant: ParticipantResponse
    match_score: float
    reason: str

class SuggestionRequest(BaseModel):
    participant_id: UUID
    max_suggestions: int = 5

class SuggestionResponse(BaseModel):
    suggestions: List[TeammateSuggestion]
    total_found: int
