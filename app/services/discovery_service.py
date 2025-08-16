from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.repositories.participant_repository import ParticipantRepository
from app.repositories.team_repository import TeamRepository
from app.schemas.discovery import (
    TeammateSuggestion, 
    TeamDiscovery, 
    DiscoveryFilters,
    ParticipantResponse,
    TeamResponse
)

class DiscoveryService:
    def __init__(self, db: Session):
        self.db = db
        self.participant_repository = ParticipantRepository(db)
        self.team_repository = TeamRepository(db)
    
    def discover_teammates(self, participant_id: UUID, filters: DiscoveryFilters) -> List[TeammateSuggestion]:
        """Discover potential teammates for a participant"""
        
        current_participant = self.participant_repository.get_by_id(participant_id)
        if not current_participant:
            return []
        
        # Get all available participants
        available_participants = self.participant_repository.get_available_participants()
        
        suggestions = []
        for participant in available_participants:
            # Skip self
            if participant.participant_id == current_participant.participant_id:
                continue
            
            # Calculate compatibility score
            score, reasons = self._calculate_compatibility(current_participant, participant)
            
            # Apply filters
            if filters.skills and participant.skills:
                # Check if participant has any of the required skills
                required_skills = set(filters.skills)
                participant_skills = set(participant.skills)
                if not required_skills.intersection(participant_skills):
                    continue
            
            # Check if score meets minimum threshold
            if score >= 5:  # Minimum compatibility score
                suggestion = TeammateSuggestion(
                    participant=ParticipantResponse.from_orm(participant),
                    compatibility_score=score,
                    reasons=reasons,
                    skill_diversity=self._calculate_skill_diversity(current_participant, participant),
                    skill_overlap=self._calculate_skill_overlap(current_participant, participant)
                )
                suggestions.append(suggestion)
        
        # Sort by compatibility score (highest first)
        suggestions.sort(key=lambda x: x.compatibility_score, reverse=True)
        return suggestions[:20]  # Limit to top 20
    
    def _get_available_teams(self, current_participant, filters: DiscoveryFilters) -> List[TeamDiscovery]:
        """Get available teams that can accept new members"""
        
        # Get teams that are open to requests
        open_teams = self.team_repository.get_open_teams()
        
        discoveries = []
        for team in open_teams:
            # Skip if team is locked
            if team.is_locked and not filters.include_locked_teams:
                continue
            
            # Calculate compatibility with team
            score, reasons = self._calculate_team_compatibility(current_participant, team)
            
            # Check team size filter
            if filters.max_team_size:
                current_size = len(team.members) if hasattr(team, 'members') else 1
                max_size = int(filters.max_team_size)
                if current_size >= max_size:
                    continue
            
            # Calculate open slots
            current_size = len(team.members) if hasattr(team, 'members') else 1
            max_size = int(team.max_members) if team.max_members else 4
            open_slots = max_size - current_size
            
            if open_slots > 0:
                discovery = TeamDiscovery(
                    team=TeamResponse.from_orm(team),
                    open_slots=open_slots,
                    compatibility_score=score,
                    reasons=reasons
                )
                discoveries.append(discovery)
        
        # Sort by compatibility score
        discoveries.sort(key=lambda x: x.compatibility_score, reverse=True)
        return discoveries[:15]  # Limit to top 15
    
    def _calculate_compatibility(self, participant1, participant2) -> tuple:
        """Calculate compatibility score between two participants based on skills"""
        
        score = 0
        reasons = []
        
        # Skill diversity (different skills = better for team variety)
        if participant1.skills and participant2.skills:
            skill_diversity = self._calculate_skill_diversity(participant1, participant2)
            skill_overlap = self._calculate_skill_overlap(participant1, participant2)
            
            # Bonus for complementary skills
            if skill_diversity > 0:
                score += min(skill_diversity * 2, 10)
                reasons.append(f"Adds {skill_diversity} new skills to team")
            
            # Moderate bonus for some skill overlap (good for communication)
            if skill_overlap > 0:
                score += min(skill_overlap, 5)
                reasons.append(f"Shares {skill_overlap} skills for better collaboration")
            
            # Bonus for balanced skill distribution
            total_skills = len(set(participant1.skills + participant2.skills))
            if total_skills >= 8:
                score += 3
                reasons.append("Wide skill coverage")
            elif total_skills >= 5:
                score += 2
                reasons.append("Good skill coverage")
        else:
            # Fallback if skills are not available
            score += 5
            reasons.append("Skills information not available")
        
        # Additional bonus for good combinations
        if participant1.skills and participant2.skills:
            # Bonus for problem-solving + technical skills combination
            problem_solving_skills = {'problem_solving', 'algorithms', 'creative_thinking'}
            technical_skills = {'algebra', 'geometry', 'algorithms', 'pattern_recognition'}
            
            p1_has_problem_solving = any(skill in problem_solving_skills for skill in participant1.skills)
            p2_has_technical = any(skill in technical_skills for skill in participant2.skills)
            
            if p1_has_problem_solving and p2_has_technical:
                score += 4
                reasons.append("Problem-solving + Technical skills synergy")
            
            # Bonus for leadership + collaboration combination
            leadership_skills = {'leadership', 'team_collaboration'}
            if any(skill in leadership_skills for skill in participant1.skills) and \
               any(skill in leadership_skills for skill in participant2.skills):
                score += 3
                reasons.append("Leadership + Collaboration synergy")
        
        return score, reasons
    
    def _calculate_skill_diversity(self, participant1, participant2) -> int:
        """Calculate how many new skills participant2 brings to participant1"""
        if not participant1.skills or not participant2.skills:
            return 0
        
        p1_skills = set(participant1.skills)
        p2_skills = set(participant2.skills)
        return len(p2_skills - p1_skills)
    
    def _calculate_skill_overlap(self, participant1, participant2) -> int:
        """Calculate how many skills both participants share"""
        if not participant1.skills or not participant2.skills:
            return 0
        
        p1_skills = set(participant1.skills)
        p2_skills = set(participant2.skills)
        return len(p1_skills & p2_skills)
    
    def _calculate_team_compatibility(self, participant, team) -> tuple:
        """Calculate compatibility score between a participant and a team"""
        
        score = 0
        reasons = []
        
        if not hasattr(team, 'members') or not team.members:
            score += 5
            reasons.append("New team formation")
            return score, reasons
        
        # Calculate team's current skill coverage
        team_skills = set()
        for member in team.members:
            if member.skills:
                team_skills.update(member.skills)
        
        # Calculate what the participant would add
        if participant.skills:
            new_skills = set(participant.skills) - team_skills
            score += len(new_skills) * 2
            if new_skills:
                reasons.append(f"Adds {len(new_skills)} new skills to team")
            
            # Bonus for filling skill gaps
            if len(team_skills) < 10 and len(new_skills) > 0:
                score += 3
                reasons.append("Fills skill gaps in team")
        
        # Bonus for balanced team size
        current_size = len(team.members)
        if current_size == 1:
            score += 4
            reasons.append("Perfect for small team")
        elif current_size == 2:
            score += 3
            reasons.append("Good for medium team")
        elif current_size == 3:
            score += 2
            reasons.append("Completes team")
        
        return score, reasons
