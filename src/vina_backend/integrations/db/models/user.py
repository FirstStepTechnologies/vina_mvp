from typing import Optional, List, Dict, Any
import uuid
from datetime import date, datetime
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, JSON

class User(SQLModel, table=True):
    __tablename__ = "users"
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    email: str = Field(unique=True, index=True)
    full_name: str
    hashed_password: Optional[str] = None
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    profile: Optional["UserProfile"] = Relationship(back_populates="user")
    progress: Optional["UserProgress"] = Relationship(back_populates="user")


class UserProfile(SQLModel, table=True):
    __tablename__ = "user_profiles"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[str] = Field(default=None, foreign_key="users.id")
    
    # Core identity (Optional until onboarding)
    profession: Optional[str] = Field(default=None, index=True)
    industry: Optional[str] = Field(default=None, index=True)
    experience_level: Optional[str] = Field(default=None, index=True)
    
    # Profile data (stored as JSON arrays)
    daily_responsibilities: List[str] = Field(default=[], sa_column=Column(JSON))
    pain_points: List[str] = Field(default=[], sa_column=Column(JSON))
    typical_outputs: List[str] = Field(default=[], sa_column=Column(JSON))
    professional_goals: List[str] = Field(default=[], sa_column=Column(JSON))
    safety_priorities: List[str] = Field(default=[], sa_column=Column(JSON))
    high_stakes_areas: List[str] = Field(default=[], sa_column=Column(JSON))
    
    # Profile metadata
    technical_comfort_level: Optional[str] = None
    learning_style_notes: Optional[str] = None
    
    # Settings & Onboarding
    resolution: str = Field(default="", description="User's learning resolution")
    daily_goal_minutes: int = Field(default=15, description="Daily learning goal in minutes")
    onboarding_responses: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    user: Optional[User] = Relationship(back_populates="profile")


class UserProgress(SQLModel, table=True):
    """Stores gamification state: diamonds, streaks, lesson progress."""
    __tablename__ = "user_progress"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id")
    
    # Currency & Engagement
    diamonds: int = Field(default=0)
    streak: int = Field(default=0)
    minutes_today: int = Field(default=0)
    minutes_this_week: int = Field(default=0)
    last_active_date: str = Field(default_factory=lambda: date.today().isoformat())
    
    # Tour Status
    tour_completed: bool = Field(default=False)
    current_tour_step: int = Field(default=0)
    
    # Learning Records
    completed_lessons: List[str] = Field(default=[], sa_column=Column(JSON))
    daily_goal_history: Dict[str, bool] = Field(default={}, sa_column=Column(JSON))
    lesson_scores: Dict[str, Any] = Field(default={}, sa_column=Column(JSON)) # lessonId -> {score, total, passedAt}
    current_difficulty: int = Field(default=3)
    
    user: Optional[User] = Relationship(back_populates="progress")