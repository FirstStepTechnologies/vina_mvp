from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

class QuizAttempt(SQLModel, table=True):
    """Database model for tracking quiz results."""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="learner_sessions.id")
    lesson_id: str  # ID or slug of the lesson
    
    score: float
    total_questions: int
    correct_answers: int
    
    attempted_at: datetime = Field(default_factory=datetime.utcnow)
