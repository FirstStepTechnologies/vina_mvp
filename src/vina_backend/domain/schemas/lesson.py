"""
Pydantic schemas for lesson content and generation.
"""
from typing import List, Dict, Optional, Literal, Union
from pydantic import BaseModel, Field


class Figure(BaseModel):
    """Figure/image embedded in a slide."""
    id: str = Field(..., description="Unique figure ID (e.g., 'fig-1-2')")
    purpose: str = Field(..., description="Learning outcome from this visual")
    image_prompt: str = Field(..., description="Detailed prompt for image generation")
    layout: Literal["single", "side-by-side", "grid"] = Field(default="single")
    accessibility_alt: str = Field(..., description="Screen reader description")
    image_path: Optional[str] = Field(default=None, description="Path to generated image")
    generation_status: Literal["pending", "generated", "failed"] = Field(default="pending")


class SlideItem(BaseModel):
    """A single item (text or figure) on a slide."""
    type: Literal["text", "figure"] = Field(..., description="Type of slide item")
    bullet: str = Field(..., min_length=1, max_length=100, description="Text shown on slide (max 12 words)")
    talk: str = Field(..., min_length=10, description="What to say for this item (TTS script)")
    figure: Optional[Figure] = Field(default=None, description="Figure data if type is 'figure'")


class SlideContent(BaseModel):
    """Content for a single slide in a lesson."""
    
    slide_number: int = Field(..., ge=1, description="Slide number (1-indexed)")
    slide_type: Literal["hook", "concept", "example", "connection"] = Field(
        ...,
        description="Type of slide content"
    )
    title: str = Field(..., min_length=1, max_length=100, description="Slide title/heading")
    items: List[SlideItem] = Field(
        ...,
        min_items=1,
        max_items=5,
        description="Items on the slide (text bullets or figures)"
    )
    duration_seconds: Optional[int] = Field(default=None, description="Estimated duration for this slide")


class LessonContent(BaseModel):
    """Complete lesson content with slides."""
    
    lesson_id: Optional[str] = Field(default=None, description="Lesson identifier")
    course_id: Optional[str] = Field(default=None, description="Course identifier")
    difficulty_level: Optional[int] = Field(default=None, ge=1, le=5, description="Difficulty level")
    lesson_title: str = Field(..., min_length=1, max_length=150)
    total_slides: Optional[int] = Field(default=None, description="Total number of slides")
    estimated_duration_minutes: Optional[int] = Field(default=None, description="Estimated lesson duration")
    slides: List[SlideContent] = Field(..., min_items=3, max_items=6)
    references_to_previous_lessons: Optional[str] = Field(
        default=None,
        description="How this lesson builds on previous lessons"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "lesson_id": "l01_what_llms_are",
                "course_id": "c_llm_foundations",
                "difficulty_level": 3,
                "lesson_title": "What LLMs Are",
                "total_slides": 4,
                "estimated_duration_minutes": 3,
                "slides": [
                    {
                        "slide_number": 1,
                        "slide_type": "hook",
                        "title": "Ever Wonder How ChatGPT Works?",
                        "items": [
                            {
                                "type": "text",
                                "bullet": "You've used AI tools that write emails",
                                "talk": "Think about the last time you used ChatGPT or a similar tool. It probably felt like magic - you type a question, and it gives you a detailed answer. But what's actually happening behind the scenes?"
                            }
                        ],
                        "duration_seconds": 55
                    }
                ],
                "references_to_previous_lessons": None
            }
        }


class IssueDetail(BaseModel):
    """Detailed issue information from reviewer."""
    type: str
    severity: str
    description: str
    location: Optional[str] = None
    action_required: Optional[str] = None
    rewrite_instruction: Optional[Dict] = None


class DurationAnalysis(BaseModel):
    """Duration analysis from reviewer."""
    total_estimated_seconds: int
    target_seconds: int
    status: Literal["on_target", "over_target", "under_target"]
    slides_over_target: List[Dict] = Field(default_factory=list)


class PreserveElement(BaseModel):
    """Elements to preserve during rewrite."""
    location: str
    content: str
    reason: str


class ReviewResult(BaseModel):
    """Result from lesson review agent (v3.1)."""
    
    decision: Literal["approved", "fix_in_place", "regenerate_from_scratch"]
    rewrite_strategy: Literal["none", "targeted_fixes", "complete_regeneration"]
    blocking_issues: List[IssueDetail] = Field(default_factory=list)
    fixable_issues: List[IssueDetail] = Field(default_factory=list)
    preserve_elements: List[PreserveElement] = Field(default_factory=list)
    duration_analysis: DurationAnalysis
    summary: str


class AuditTrail(BaseModel):
    """Full audit trail of the generation process for QA."""
    gen_prompt: Optional[str] = None
    gen_output: Optional[Dict] = None
    rev_prompt: Optional[str] = None
    rev_output: Optional[Dict] = None
    rew_prompt: Optional[str] = None
    rew_output: Optional[Dict] = None

class GenerationMetadata(BaseModel):
    """Metadata about lesson generation process."""
    
    cache_hit: bool = Field(default=False)
    llm_model: Optional[str] = None
    generation_time_seconds: Optional[float] = None
    phase_durations: Dict[str, float] = Field(default_factory=dict)
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
    audit_trail: Optional[AuditTrail] = None
    
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
