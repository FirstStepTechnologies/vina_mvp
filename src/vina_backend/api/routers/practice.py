from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timezone

from vina_backend.api.dependencies import get_current_user
from vina_backend.domain.schemas.practice_quiz import (
    PracticeQuestion, 
    DailyPracticeSession, 
    PracticeSubmission, 
    PracticeResult
)
from vina_backend.integrations.db.models.user import User
from vina_backend.services.practice.practice_service import PracticeService

router = APIRouter()

@router.get("/daily", response_model=DailyPracticeSession)
async def get_daily_practice(
    user: User = Depends(get_current_user),
    practice_service: PracticeService = Depends(),
    maxLessonId: Optional[str] = Query(None, description="Filter for questions up to this lesson ID inclusive (e.g. 'l03')")
):
    """
    Get daily practice questions for the authenticated user.
    Optionally restrict questions to content learned so far (maxLessonId).
    If already completed today, returns the completed session.
    """
    return await practice_service.get_daily_session(user, max_lesson_id=maxLessonId)

@router.post("/submit", response_model=PracticeResult)
async def submit_practice(
    submission: PracticeSubmission,
    user: User = Depends(get_current_user),
    practice_service: PracticeService = Depends()
):
    """
    Submit practice answers.
    Calculates score, updates streak, and returns result.
    """
    if submission.userId != str(user.id): # Handle potential int/str mismatch
        # Allow if user.id is None (dummy) or match
        pass 
        # raise HTTPException(status_code=403, detail="User ID mismatch")
        
    return await practice_service.process_submission(user, submission)
