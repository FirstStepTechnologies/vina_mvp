"""
Pydantic schemas for learner state and session management.
"""
from datetime import datetime
from typing import Dict, List
from pydantic import BaseModel, Field


class LearnerState(BaseModel):
    """
    Represents the current learning state for a user in a course.
    Tracks progress, difficulty adjustments, and quiz performance.
    """
    
    session_id: str = Field(..., description="Unique session identifier (UUID)")
    user_profile_id: int = Field(..., description="Foreign key to UserProfile")
    course_id: str = Field(..., description="Course identifier (e.g., 'c_llm_foundations')")
    current_lesson_index: int = Field(
        default=0, 
        description="Index of the current lesson (0-based)"
    )
    lesson_difficulty_history: Dict[str, int] = Field(
        default_factory=dict,
        description="Difficulty level used for each completed lesson {lesson_id: difficulty_level}"
    )
    current_difficulty: int = Field(
        default=3,
        description="Current difficulty level (1=Guided, 3=Practical, 5=Direct)"
    )
    completed_lessons: List[str] = Field(
        default_factory=list,
        description="List of completed lesson IDs"
    )
    quiz_scores: Dict[str, int] = Field(
        default_factory=dict,
        description="Quiz scores for each lesson {lesson_id: score_out_of_3}"
    )
    adaptation_count: int = Field(
        default=0,
        description="Total number of adaptations (simplify, get_to_point, etc.) requested"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_profile_id": 1,
                "course_id": "c_llm_foundations",
                "current_lesson_index": 3,
                "lesson_difficulty_history": {
                    "l01_what_llms_are": 3,
                    "l02_tokens_context": 3,
                    "l03_why_outputs_vary": 4
                },
                "current_difficulty": 4,
                "completed_lessons": ["l01_what_llms_are", "l02_tokens_context", "l03_why_outputs_vary"],
                "quiz_scores": {
                    "l01_what_llms_are": 3,
                    "l02_tokens_context": 2,
                    "l03_why_outputs_vary": 3
                },
                "adaptation_count": 1
            }
        }


class SessionCreateRequest(BaseModel):
    """Request to create a new learning session."""
    
    user_profile_id: int = Field(..., description="ID of the user profile")
    course_id: str = Field(..., description="Course to start", example="c_llm_foundations")
    initial_difficulty: int = Field(
        default=3,
        ge=1,
        le=5,
        description="Starting difficulty level (1, 3, or 5)"
    )


class SessionResponse(BaseModel):
    """Response containing session information."""
    
    session: LearnerState
    next_lesson_id: str = Field(..., description="ID of the next lesson to take")
    progress_percentage: float = Field(..., description="Course completion percentage (0-100)")
