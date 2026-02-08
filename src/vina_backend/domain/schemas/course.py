from typing import List, Optional
from pydantic import BaseModel, Field

class LessonSummary(BaseModel):
    """Summary of a lesson for the course map."""
    
    lesson_id: str = Field(..., alias="lessonId")
    lesson_number: int = Field(..., alias="lessonNumber")
    lesson_name: str = Field(..., alias="lessonName")
    short_title: str = Field(..., alias="shortTitle")
    topic_group: str = Field(..., alias="topicGroup")
    estimated_duration: int = Field(..., alias="estimatedDuration") # in minutes
    prerequisites: List[str] = []
    status: str = Field(default="locked", description="locked | active | completed")

    class Config:
        populate_by_name = True
