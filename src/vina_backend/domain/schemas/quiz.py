# src/vina_backend/domain/schemas/quiz.py

from typing import List, Optional
from pydantic import BaseModel, Field, validator

class QuizOption(BaseModel):
    """Single answer option for a quiz question."""
    text: str = Field(..., description="Option text (without A/B/C/D prefix)")
    is_correct: bool = Field(..., description="Whether this is the correct answer")

class QuizQuestion(BaseModel):
    """Single question in a placement quiz."""
    id: str = Field(..., description="Unique question ID (e.g., 'q1', 'q2')")
    text: str = Field(..., description="Question text (scenario-based)")
    options: List[QuizOption] = Field(..., min_items=4, max_items=4, description="Exactly 4 options")
    correctAnswer: str = Field(..., description="Correct answer letter (A/B/C/D)")
    associatedLesson: str = Field(..., description="Lesson ID this question tests (e.g., 'l01_what_llms_are')")
    difficultyLevel: int = Field(..., ge=1, le=5, description="Question difficulty (1=easiest, 5=hardest)")
    explanation: str = Field(..., description="User-facing explanation of correct answer")
    rationale: str = Field(..., description="Internal note on why this question fits this profession/stage")
    isProfessionSpecific: bool = Field(..., description="True if question uses profession context, False if universal")
    conceptTested: str = Field(..., description="Core LLM concept being tested (e.g., 'hallucinations', 'tokens')")
    
    @validator('options')
    def validate_exactly_one_correct(cls, v):
        """Ensure exactly one option is marked correct."""
        correct_count = sum(1 for opt in v if opt.is_correct)
        if correct_count != 1:
            raise ValueError(f"Expected exactly 1 correct answer, found {correct_count}")
        return v
    
    @validator('correctAnswer')
    def validate_correct_answer_letter(cls, v):
        """Ensure correctAnswer is A, B, C, or D."""
        if v not in ['A', 'B', 'C', 'D']:
            raise ValueError(f"correctAnswer must be A/B/C/D, got '{v}'")
        return v

class ProfessionQuiz(BaseModel):
    """Complete placement quiz for a profession."""
    profession: str = Field(..., description="Target profession (e.g., 'Clinical Researcher')")
    questions: List[QuizQuestion] = Field(..., min_items=5, max_items=5, description="Exactly 5 questions")
    
    @validator('questions')
    def validate_difficulty_progression(cls, v):
        """Ensure questions progress from easy (1) to hard (5)."""
        difficulties = [q.difficultyLevel for q in v]
        expected = [1, 2, 3, 4, 5]
        if difficulties != expected:
            raise ValueError(f"Questions must have difficulty [1,2,3,4,5], got {difficulties}")
        return v
    
    @validator('questions')
    def validate_profession_specific_count(cls, v):
        """Ensure 2 profession-specific questions (Q4, Q5)."""
        prof_specific = [q for q in v if q.isProfessionSpecific]
        if len(prof_specific) != 2:
            raise ValueError(f"Expected 2 profession-specific questions, found {len(prof_specific)}")
        return v
    
    @validator('questions')
    def validate_concept_diversity(cls, v):
        """Ensure no duplicate concepts tested."""
        concepts = [q.conceptTested for q in v]
        if len(concepts) != len(set(concepts)):
            raise ValueError(f"Questions test duplicate concepts: {concepts}")
        return v

class ReviewResult(BaseModel):
    """Result of Reviewer Agent evaluation."""
    passed: bool = Field(..., description="True if quiz meets all quality standards")
    issues: List[str] = Field(default_factory=list, description="Specific problems found (empty if passed)")
    score_breakdown: dict = Field(default_factory=dict, description="Scores for each quality dimension")