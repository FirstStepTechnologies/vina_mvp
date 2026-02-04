"""
Pydantic schemas for lesson content and generation.
"""
from typing import List, Dict, Optional, Literal
from pydantic import BaseModel, Field


class SlideContent(BaseModel):
    """Content for a single slide in a lesson."""
    
    slide_number: int = Field(..., ge=1, description="Slide number (1-indexed)")
    slide_type: Literal["hook", "concept", "example", "connection"] = Field(
        ...,
        description="Type of slide content"
    )
    heading: str = Field(..., min_length=1, max_length=100, description="Slide heading")
    content: List[str] = Field(
        ...,
        min_items=1,
        max_items=5,
        description="Bullet points for the slide"
    )
    speaker_notes: str = Field(
        ...,
        min_length=10,
        description="What to say when presenting this slide (for TTS)"
    )


class LessonContent(BaseModel):
    """Complete lesson content with slides."""
    
    lesson_title: str = Field(..., min_length=1, max_length=150)
    slides: List[SlideContent] = Field(..., min_items=3, max_items=6)
    references_to_previous_lessons: Optional[str] = Field(
        default=None,
        description="How this lesson builds on previous lessons"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "lesson_title": "What LLMs Are",
                "slides": [
                    {
                        "slide_number": 1,
                        "slide_type": "hook",
                        "heading": "Ever Wonder How ChatGPT Works?",
                        "content": [
                            "You've probably used AI tools that write emails or answer questions",
                            "But what's actually happening behind the scenes?",
                            "Let's demystify Large Language Models (LLMs)"
                        ],
                        "speaker_notes": "Think about the last time you used ChatGPT or a similar tool..."
                    }
                ],
                "references_to_previous_lessons": None
            }
        }


class ReviewResult(BaseModel):
    """Result from lesson review agent."""
    
    quality_score: float = Field(..., ge=0, le=10, description="Quality score 0-10")
    approval_status: Literal["approved", "approved_with_minor_fixes", "needs_revision"]
    critical_issues: List[str] = Field(default_factory=list)
    minor_issues: List[str] = Field(default_factory=list)
    suggested_fixes: List[str] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)


class GenerationMetadata(BaseModel):
    """Metadata about lesson generation process."""
    
    cache_hit: bool = Field(default=False)
    llm_model: Optional[str] = None
    generation_time_seconds: Optional[float] = None
    review_passed_first_time: Optional[bool] = None
    rewrite_count: int = Field(default=0)
    quality_score: Optional[float] = None


class GeneratedLesson(BaseModel):
    """Complete generated lesson with metadata."""
    
    lesson_id: str
    course_id: str
    difficulty_level: int
    lesson_content: LessonContent
    generation_metadata: GenerationMetadata
    
    class Config:
        json_schema_extra = {
            "example": {
                "lesson_id": "l01_what_llms_are",
                "course_id": "c_llm_foundations",
                "difficulty_level": 3,
                "lesson_content": {
                    "lesson_title": "What LLMs Are",
                    "slides": [],
                    "references_to_previous_lessons": None
                },
                "generation_metadata": {
                    "cache_hit": False,
                    "llm_model": "gemini-3-flash",
                    "generation_time_seconds": 4.5,
                    "review_passed_first_time": True,
                    "rewrite_count": 0,
                    "quality_score": 8.5
                }
            }
        }
