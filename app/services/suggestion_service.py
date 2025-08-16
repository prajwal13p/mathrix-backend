from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.repositories.participant_repository import ParticipantRepository
from app.repositories.team_repository import TeamRepository
from app.schemas.suggestion import TeammateSuggestion, SuggestionResponse
from app.schemas.participant import ParticipantResponse
from fastapi import HTTPException

class SuggestionService:
    def __init__(self, db: Session):
        self.db = db
        self.participant_repository = ParticipantRepository(db)
        self.team_repository = TeamRepository(db)
    
    def get_teammate_suggestions(self, participant_id: UUID, max_suggestions: int = 5) -> SuggestionResponse:
        """Get intelligent teammate suggestions based on interest cluster diversity"""
        # Verify participant exists
        participant = self.participant_repository.get_by_id(participant_id)
        if not participant:
            raise HTTPException(
                status_code=404,
                detail="Participant not found"
            )
        
        # Get current team members' clusters
        current_clusters = set()
        team_size = 0
        
        if participant.team_id:
            team_members = self.participant_repository.get_team_members(participant.team_id)
            current_clusters = {member.interest_cluster for member in team_members}
            team_size = len(team_members)
        
        # Add participant's own cluster
        current_clusters.add(participant.interest_cluster)
        
        # If team is full, no suggestions needed
        if team_size >= 4:
            return SuggestionResponse(suggestions=[], total_found=0)
        
        # Find clusters not represented in current team
        all_clusters = {1, 2, 3, 4, 5}
        available_clusters = all_clusters - current_clusters
        
        suggestions = []
        
        # Priority 1: Participants from different clusters (diversity)
        for cluster in available_clusters:
            cluster_participants = self.participant_repository.get_participants_by_cluster(cluster)
            
            for cluster_participant in cluster_participants:
                if len(suggestions) >= max_suggestions:
                    break
                
                # Calculate match score based on diversity
                match_score = self._calculate_diversity_score(
                    participant, cluster_participant, current_clusters
                )
                
                suggestion = TeammateSuggestion(
                    participant=ParticipantResponse.from_orm(cluster_participant),
                    match_score=match_score,
                    reason=f"Different interest cluster ({cluster_participant.interest_cluster}) for team diversity"
                )
                
                suggestions.append(suggestion)
            
            if len(suggestions) >= max_suggestions:
                break
        
        # Priority 2: If we don't have enough suggestions, add from any unassigned participants
        if len(suggestions) < max_suggestions:
            remaining_needed = max_suggestions - len(suggestions)
            unassigned = self.participant_repository.get_unassigned_participants()
            
            # Exclude already suggested participants and the requesting participant
            suggested_ids = {s.participant.participant_id for s in suggestions}
            suggested_ids.add(participant_id)
            
            additional = [
                p for p in unassigned 
                if p.participant_id not in suggested_ids
            ][:remaining_needed]
            
            for additional_participant in additional:
                match_score = self._calculate_collaboration_score(
                    participant, additional_participant
                )
                
                suggestion = TeammateSuggestion(
                    participant=ParticipantResponse.from_orm(additional_participant),
                    match_score=match_score,
                    reason="Additional unassigned participant for team completion"
                )
                
                suggestions.append(suggestion)
        
        # Sort by match score (highest first)
        suggestions.sort(key=lambda x: x.match_score, reverse=True)
        
        return SuggestionResponse(
            suggestions=suggestions[:max_suggestions],
            total_found=len(suggestions)
        )
    
    def _calculate_diversity_score(self, requester, candidate, current_clusters: set) -> float:
        """Calculate match score based on diversity"""
        base_score = 10.0
        
        # Bonus for different cluster
        if candidate.interest_cluster not in current_clusters:
            base_score += 5.0
        
        # Bonus for different department (cross-disciplinary collaboration)
        if requester.department != candidate.department:
            base_score += 2.0
        
        # Bonus for different year (experience diversity)
        year_diff = abs(requester.year - candidate.year)
        if year_diff > 0:
            base_score += min(year_diff, 3) * 0.5
        
        return base_score
    
    def _calculate_collaboration_score(self, requester, candidate) -> float:
        """Calculate match score based on collaboration potential"""
        base_score = 5.0
        
        # Bonus for same department (easier communication)
        if requester.department == candidate.department:
            base_score += 3.0
        
        # Bonus for similar year (similar experience level)
        year_diff = abs(requester.year - candidate.year)
        if year_diff == 0:
            base_score += 2.0
        elif year_diff == 1:
            base_score += 1.0
        
        # Bonus for same interest cluster (shared passion)
        if requester.interest_cluster == candidate.interest_cluster:
            base_score += 2.0
        
        return base_score
    
    def get_auto_team_suggestions(self) -> dict:
        """Get suggestions for automatic team formation"""
        # Get cluster distribution
        cluster_distribution = self.participant_repository.get_cluster_distribution()
        
        # Get unassigned participants
        unassigned = self.participant_repository.get_unassigned_participants()
        
        # Calculate optimal team distribution
        total_participants = len(unassigned)
        optimal_teams = total_participants // 4
        remaining_participants = total_participants % 4
        
        suggestions = {
            "total_participants": total_participants,
            "optimal_teams": optimal_teams,
            "remaining_participants": remaining_participants,
            "cluster_distribution": cluster_distribution,
            "recommendation": self._generate_auto_team_recommendation(
                cluster_distribution, optimal_teams
            )
        }
        
        return suggestions
    
    def _generate_auto_team_recommendation(self, cluster_distribution: dict, team_count: int) -> str:
        """Generate recommendation for automatic team formation"""
        if team_count == 0:
            return "Not enough participants to form teams"
        
        # Calculate how many participants we need from each cluster per team
        total_participants = sum(cluster_distribution.values())
        participants_per_team = 4
        
        # Ideal distribution: try to have 1 participant from each cluster per team
        ideal_distribution = {}
        for cluster in range(1, 6):
            cluster_count = cluster_distribution.get(cluster, 0)
            ideal_distribution[cluster] = min(cluster_count, team_count)
        
        # Check if we can achieve good diversity
        diverse_teams_possible = all(count > 0 for count in ideal_distribution.values())
        
        if diverse_teams_possible:
            return f"Can form {team_count} diverse teams with participants from all interest clusters"
        else:
            # Find which clusters are underrepresented
            underrepresented = [cluster for cluster, count in ideal_distribution.items() if count == 0]
            return f"Can form {team_count} teams, but clusters {underrepresented} are underrepresented"
