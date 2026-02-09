"""
Pydantic schemas for user profiles.
"""
from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class UserProfileData(BaseModel):
    """User profile data structure."""
    
    profession: str = Field(..., description="User's profession")
    industry: str = Field(..., description="User's industry sector")
    experience_level: Optional[str] = Field(None, description="Experience level")
    leadership_level: Optional[str] = Field(None, description="Leadership/Management level")
    daily_responsibilities: List[str] = Field(
        default=[], description="Day-to-day responsibilities"
    )
    pain_points: List[str] = Field(
        default=[], description="Professional pain points and challenges"
    )
    typical_outputs: List[str] = Field(
        default=[], 
        description="Documents, deliverables, or artifacts this person creates in their work"
    )
    technical_comfort_level: Optional[str] = Field(
        None, description="Technical proficiency level"
    )
    learning_style_notes: Optional[str] = Field(
        default="", description="How this person prefers to learn"
    )
    professional_goals: List[str] = Field(
        ..., description="Career and skill development goals"
    )
    safety_priorities: List[str] = Field(
        ..., 
        description="Critical safety, ethical, or compliance considerations for this role"
    )
    high_stakes_areas: List[str] = Field(
        ..., 
        description="Specific work outputs or decisions where errors have serious consequences"
    )
    # Gamification & Onboarding Fields (New)
    resolution: Optional[str] = Field(
        default="", 
        description="User's learning resolution (e.g. 'Master AI Strategy')"
    )
    daily_goal_minutes: int = Field(
        default=15, 
        description="Daily learning goal in minutes"
    )
    onboarding_responses: dict = Field(
        default_factory=dict, 
        description="Raw responses from onboarding quiz"
    )

class UserProfileRequest(BaseModel):
    """Request to generate a user profile."""
    
    profession: str = Field(..., example="Clinical Researcher")
    industry: str = Field(..., example="Pharma/Biotech")
    experience_level: Literal["Beginner", "Intermediate", "Advanced"] = Field(
        ..., example="Intermediate"
    )


class UserProfileResponse(BaseModel):
    """Response containing a generated user profile."""
    
    profile: UserProfileData
    generated_from_cache: bool = Field(
        default=False,
        description="Whether this profile was retrieved from cache/database"
    )
    id: str = Field(..., description="The UUID of the user")
    email: str = Field(..., description="User email")
    created_at: str = Field(..., description="ISO timestamp")
    resolution: Optional[str] = None
    dailyGoalMinutes: Optional[int] = None