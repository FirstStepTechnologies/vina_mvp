from typing import List, Optional
from pydantic import BaseModel, Field, validator

class QuizOption(BaseModel):
    """Single answer option for a quiz question."""
    text: str = Field(
        ..., 
        description="Option text WITHOUT letter prefix (frontend adds A/B/C/D)"
    )
    is_correct: bool = Field(
        ..., 
        description="Whether this is the correct answer"
    )

class LessonQuizQuestion(BaseModel):
    """Single question in a post-lesson quiz."""
    
    id: str = Field(
        ..., 
        description="Question ID (e.g., 'q1', 'q2', 'q3')"
    )
    
    text: str = Field(
        ..., 
        description="Question text (scenario-based, profession-specific)",
        min_length=5
    )
    
    options: List[QuizOption] = Field(
        ..., 
        min_items=4, 
        max_items=4,
        description="Exactly 4 answer options"
    )
    
    correctAnswer: str = Field(
        ..., 
        description="Correct answer letter (A/B/C/D)",
        pattern="^[ABCD]$"
    )
    
    explanation: str = Field(
        ..., 
        description="User-facing explanation (2-3 sentences) of why correct answer is right",
        min_length=20
    )
    
    conceptTested: str = Field(
        ..., 
        description="Core LLM concept tested (e.g., 'hallucinations', 'context_windows')"
    )
    
    rationale: str = Field(
        ..., 
        description="Internal note on pedagogical intent (for reviewers/developers)"
    )
    
    @validator('options')
    def validate_exactly_one_correct(cls, v):
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


class LessonQuiz(BaseModel):
    """Complete quiz for a lesson (profession-specific)."""
    
    lessonId: str = Field(
        ..., 
        description="Lesson ID (e.g., 'l05_hallucinations')",
        pattern="^l\\d{2}_[a-z_]+$"
    )
    
    profession: str = Field(
        ..., 
        description="Target profession (e.g., 'Clinical Researcher')"
    )
    
    questions: List[LessonQuizQuestion] = Field(
        ..., 
        min_items=3, 
        max_items=3,
        description="Exactly 3 questions"
    )
    
    passThreshold: int = Field(
        default=2, 
        description="Number of correct answers required to pass (2/3)"
    )
    
    @validator('questions')
    def validate_unique_concepts(cls, v):
        """Ensure each question tests a different concept."""
        concepts = [q.conceptTested for q in v]
        if len(concepts) != len(set(concepts)):
            duplicates = [c for c in concepts if concepts.count(c) > 1]
            raise ValueError(f"Questions test duplicate concepts: {duplicates}")
        return v


class QuizSubmission(BaseModel):
    """User's quiz submission."""
    
    lessonId: str
    userId: str
    answers: List[dict] = Field(
        ...,
        description="List of {questionId, selectedAnswer, isCorrect}"
    )
    
    @validator('answers')
    def validate_answer_count(cls, v):
        """Ensure exactly 3 answers submitted."""
        if len(v) != 3:
            raise ValueError(f"Expected 3 answers, got {len(v)}")
        return v


class QuizResult(BaseModel):
    """Result after quiz submission."""
    
    score: int = Field(..., ge=0, le=3, description="Number of correct answers")
    total: int = Field(default=3, description="Total questions")
    passed: bool = Field(..., description="Whether user passed (score >= 2)")
    pointsEarned: int = Field(..., description="Points awarded (0, 20, or 30)")
    feedback: str = Field(..., description="Encouragement message")
    
    # Optional: Next lesson info (if passed)
    nextLessonId: Optional[str] = Field(None, description="Next lesson to unlock")


class ReviewResult(BaseModel):
    """Result of Reviewer Agent evaluation."""
    
    passed: bool = Field(
        ..., 
        description="True if quiz meets all quality standards"
    )
    
    issues: List[str] = Field(
        default_factory=list, 
        description="Specific problems found (empty if passed)"
    )
    
    score_breakdown: dict = Field(
        default_factory=dict, 
        description="Scores for each quality dimension"
    )
