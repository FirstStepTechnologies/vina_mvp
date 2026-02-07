
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict
from pydantic import BaseModel

from vina_backend.services.quiz_engine import quiz_engine, QuizEngine
from vina_backend.domain.schemas.quiz import ProfessionQuiz

router = APIRouter(prefix="/onboarding", tags=["onboarding"])

class QuizSubmission(BaseModel):
    profession: str
    answers: Dict[str, str]  # question_id -> answer_letter (A/B/C/D)

class AssessmentResult(BaseModel):
    score: int
    total: int
    starting_lesson: str
    stage: str
    message: str

@router.get("/quiz/{profession}", response_model=ProfessionQuiz)
async def get_quiz(profession: str):
    """Get the onboarding quiz for a specific profession."""
    quiz = quiz_engine.get_quiz_for_profession(profession)
    if not quiz:
        # Fallback or error? For MVP, error if profession not supported
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No quiz available for profession: {profession}"
        )
    # Remove correct answers from response? Currently schema includes everything.
    # TODO: In a real app, we should use a response model that excludes `correctAnswer`.
    # For now, we trust the client not to cheat from the network tab, or create a PublicQuiz model.
    return quiz

@router.post("/submit", response_model=AssessmentResult)
async def submit_quiz(submission: QuizSubmission):
    """Submit quiz answers and get placement result."""
    try:
        result = quiz_engine.calculate_score(submission.answers, submission.profession)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
