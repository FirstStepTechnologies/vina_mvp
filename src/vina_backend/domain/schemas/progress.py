from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from datetime import date

class LessonScore(BaseModel):
    """Score record for a completed lesson quiz."""
    score: int
    total: int
    passed_at: str = Field(..., description="ISO 8601 timestamp")

class VinaProgress(BaseModel):
    """Complete gamification and progress state for a user."""
    user_id: str
    
    # Currency & Engagement
    diamonds: int = Field(default=0, description="Main currency earned")
    streak: int = Field(default=0, description="Current daily streak")
    minutes_today: int = Field(default=0, description="Minutes spent learning today")
    minutes_this_week: int = Field(default=0, description="Minutes spent this week")
    last_active_date: str = Field(
        default_factory=lambda: date.today().isoformat(),
        description="YYYY-MM-DD of last activity"
    )
    
    # Onboarding / Tour
    tour_completed: bool = Field(default=False, description="Has completed the main UI tour")
    current_tour_step: int = Field(default=0, description="Last seen step in the tour")
    
    # Learning Progress
    completed_lessons: List[str] = Field(default_factory=list, description="List of completed Lesson IDs")
    daily_goal_history: Dict[str, bool] = Field(
        default_factory=dict, 
        description="Map of date string to boolean indicating if daily goal was met"
    )
    lesson_scores: Dict[str, LessonScore] = Field(
        default_factory=dict,
        description="Map of lessonId to score details"
    )
    current_difficulty: int = Field(default=3, description="Current adaptation difficulty level (1-5)")


class ProgressSyncRequest(BaseModel):
    """Request to sync client-side progress events to backend."""
    minutes_added: int = 0
    diamonds_earned: int = 0
    action: Optional[str] = None  # e.g., "daily_goal_met", "lesson_complete"


class TourUpdate(BaseModel):
    """Request to update tour status."""
    tour_completed: bool
    current_tour_step: int
