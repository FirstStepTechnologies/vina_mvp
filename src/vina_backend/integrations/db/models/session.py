"""
SQLModel for learner sessions and state persistence.
"""
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON


class LearnerSession(SQLModel, table=True):
    """
    Database model for learner sessions.
    Tracks learning progress, difficulty adjustments, and quiz performance.
    """
    
    __tablename__ = "learner_sessions"
    
    # Primary key
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Session identifier (UUID string)
    session_id: str = Field(unique=True, index=True)
    
    # Foreign key to user profile
    user_profile_id: int = Field(foreign_key="user_profiles.id", index=True)
    
    # Course information
    course_id: str = Field(index=True)
    
    # Progress tracking
    current_lesson_index: int = Field(default=0)
    completed_lessons: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    
    # Difficulty management
    current_difficulty: int = Field(default=3)
    lesson_difficulty_history: dict = Field(default_factory=dict, sa_column=Column(JSON))
    
    # Quiz performance
    quiz_scores: dict = Field(default_factory=dict, sa_column=Column(JSON))
    
    # Adaptation tracking
    adaptation_count: int = Field(default=0)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_active: datetime = Field(default_factory=datetime.utcnow)
