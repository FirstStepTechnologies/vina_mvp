"""
Database models for user-related data.
"""
from typing import Optional, List
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON
from datetime import datetime


class UserProfile(SQLModel, table=True):
    """User profile database model."""
    
    __tablename__ = "user_profiles"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Core identity (indexed for fast lookups)
    profession: str = Field(index=True)
    industry: str = Field(index=True)
    experience_level: str = Field(index=True)
    
    # Profile data (stored as JSON arrays)
    daily_responsibilities: List[str] = Field(sa_column=Column(JSON))
    pain_points: List[str] = Field(sa_column=Column(JSON))
    typical_outputs: List[str] = Field(sa_column=Column(JSON))
    professional_goals: List[str] = Field(sa_column=Column(JSON))
    safety_priorities: List[str] = Field(sa_column=Column(JSON))
    high_stakes_areas: List[str] = Field(sa_column=Column(JSON))
    
    # Profile metadata
    technical_comfort_level: str
    learning_style_notes: str
    
    # Timestamps
    created_at: Optional[str] = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: Optional[str] = Field(default_factory=lambda: datetime.utcnow().isoformat())