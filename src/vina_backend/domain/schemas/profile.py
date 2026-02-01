"""
Pydantic schemas for user profiles.
"""
from typing import List, Literal
from pydantic import BaseModel, Field


class UserProfileData(BaseModel):
    """User profile data structure."""
    
    profession: str = Field(..., description="User's profession")
    industry: str = Field(..., description="User's industry sector")
    experience_level: Literal["Beginner", "Intermediate", "Advanced"] = Field(
        ..., description="Experience level"
    )
    daily_responsibilities: List[str] = Field(
        ..., description="Day-to-day responsibilities"
    )
    pain_points: List[str] = Field(
        ..., description="Professional pain points and challenges"
    )
    typical_outputs: List[str] = Field(
        ..., 
        description="Documents, deliverables, or artifacts this person creates in their work"
    )
    technical_comfort_level: Literal["Low", "Medium", "High"] = Field(
        ..., description="Technical proficiency level"
    )
    learning_style_notes: str = Field(
        ..., description="How this person prefers to learn"
    )
    professional_goals: List[str] = Field(
        ..., description="Career and skill development goals"
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