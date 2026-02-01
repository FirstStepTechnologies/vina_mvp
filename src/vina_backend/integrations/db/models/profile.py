from datetime import datetime
from typing import List, Optional
from sqlmodel import SQLModel, Field, Column, JSON
from pydantic import validator

class UserProfile(SQLModel, table=True):
    """Database model for user profiles."""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Selection criteria (used for lookup)
    profession: str = Field(index=True)
    industry: str = Field(index=True)
    experience_level: str = Field(index=True)
    
    # Generated profile data
    # We use Column(JSON) to store lists in SQLite
    daily_responsibilities: List[str] = Field(sa_column=Column(JSON))
    pain_points: List[str] = Field(sa_column=Column(JSON))
    typical_outputs: List[str] = Field(sa_column=Column(JSON))
    professional_goals: List[str] = Field(sa_column=Column(JSON))
    
    technical_comfort_level: str
    learning_style_notes: str
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True
