from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON
from typing import List, Optional

class UserProfile(SQLModel, table=True):
    """User profile database model."""
    
    __tablename__ = "user_profiles"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    profession: str = Field(index=True)
    industry: str = Field(index=True)
    experience_level: str = Field(index=True)
    
    # Existing fields
    daily_responsibilities: List[str] = Field(sa_column=Column(JSON))
    pain_points: List[str] = Field(sa_column=Column(JSON))
    typical_outputs: List[str] = Field(sa_column=Column(JSON))
    professional_goals: List[str] = Field(sa_column=Column(JSON))
    technical_comfort_level: str
    learning_style_notes: str
    
    # NEW FIELDS - Add these
    safety_priorities: List[str] = Field(sa_column=Column(JSON))
    high_stakes_areas: List[str] = Field(sa_column=Column(JSON))
    
    created_at: Optional[str] = None
    updated_at: Optional[str] = None