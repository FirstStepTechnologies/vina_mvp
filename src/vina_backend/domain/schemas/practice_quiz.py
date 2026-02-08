from typing import List, Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime

class PracticeQuizOption(BaseModel):
    """Single answer option for a practice question."""
    
    text: str = Field(
        ..., 
        description="Option text WITHOUT letter prefix"
    )
    
    is_correct: bool = Field(
        ..., 
        description="Whether this is the correct answer"
    )

class PracticeQuestion(BaseModel):
    """Single question in the practice pool."""
    
    id: str = Field(
        ..., 
        description="Unique question ID (e.g., 'pq_l01_clinical_01')",
        pattern="^pq_l\\d{2}_[a-z_]+_\\d{2}$"
    )
    
    lessonId: str = Field(
        ..., 
        description="Source lesson ID (e.g., 'l01_what_llms_are')"
    )
    
    text: str = Field(
        ..., 
        description="Question text (scenario based)",
        min_length=20
    )
    
    options: List[PracticeQuizOption] = Field(
        ..., 
        min_items=4, 
        max_items=4,
        description="Exactly 4 options per question"
    )
    
    correctAnswer: str = Field(
        ..., 
        description="Letter of correct answer (A/B/C/D)",
        pattern="^[A-D]$"
    )
    
    explanation: str = Field(
        ..., 
        description="Explanation of correct answer (2-3 sentences)",
        min_length=50
    )
    
    conceptTested: str = Field(
        ..., 
        description="Core concept tested from the lesson"
    )
    
    @validator('options')
    def validate_one_correct_option(cls, v):
        """Ensure exactly one option is marked correct."""
        correct_count = sum(1 for opt in v if opt.is_correct)
        if correct_count != 1:
            raise ValueError(f"Expected exactly 1 correct answer, found {correct_count}")
        return v
    
    @validator('correctAnswer')
    def validate_correct_answer_matches(cls, v, values):
        """Ensure correctAnswer letter matches the is_correct option."""
        if 'options' not in values:
            return v
        
        letter_map = {0: 'A', 1: 'B', 2: 'C', 3: 'D'}
        correct_index = next(
            (i for i, opt in enumerate(values['options']) if opt.is_correct), 
            None
        )
        
        if correct_index is None:
            raise ValueError("No option marked as correct")
        
        expected_letter = letter_map[correct_index]
        if v != expected_letter:
            raise ValueError(
                f"correctAnswer is '{v}' but option at index {correct_index} "
                f"is marked correct (expected '{expected_letter}')"
            )
        
        return v

class DailyPracticeSession(BaseModel):
    """Practice session data."""
    
    userId: str
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    questions: List[PracticeQuestion] = Field(
        ...,
        min_items=0,
        max_items=10,
        description="Questions for this session (0-10)"
    )

class PracticeSubmission(BaseModel):
    """User's practice quiz submission."""
    
    userId: str
    date: str = Field(..., description="Date of practice (YYYY-MM-DD)")
    answers: List[dict] = Field(
        ...,
        description="List of {questionId, selectedAnswer, isCorrect}"
    )

class PracticeResult(BaseModel):
    """Result after practice submission."""
    
    score: int = Field(..., ge=0, le=10, description="Number correct")
    total: int = Field(..., ge=1, le=10, description="Total questions")
    pointsEarned: int = Field(..., description="Points awarded (score × 10)")
    checkmarkPattern: str = Field(..., description="Visual pattern (e.g., '✓✓✗✓✓✓✗✓✓✓')")
    streakExtended: bool = Field(..., description="Whether streak was extended")
    nextResetTime: str = Field(..., description="ISO timestamp of next midnight reset")
