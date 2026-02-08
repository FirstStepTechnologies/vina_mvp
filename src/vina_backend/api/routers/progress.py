from typing import Annotated, Dict, Any
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlmodel import Session
from vina_backend.integrations.db.session import get_session
from vina_backend.integrations.db.models.user import User, UserProgress
from vina_backend.domain.schemas.progress import VinaProgress, ProgressSyncRequest, LessonScore
from vina_backend.api.dependencies import get_current_user

router = APIRouter(prefix="/user/progress", tags=["progress"])


@router.get("", response_model=VinaProgress)
def get_progress(current_user: User = Depends(get_current_user)):
    """Get the current user's progress summary."""
    p = current_user.progress
    if not p:
        # Should have been created at register
        raise HTTPException(status_code=404, detail="Progress not initialized")

    # Create LessonScore objects from JSON dicts
    scores = {}
    if p.lesson_scores:
        for lid, data in p.lesson_scores.items():
            if isinstance(data, dict):
                 # Handle missing fields gracefully
                 try:
                    scores[lid] = LessonScore(**data)
                 except:
                    pass

    return VinaProgress(
        user_id=str(current_user.id),
        diamonds=p.diamonds,
        streak=p.streak,
        minutes_today=p.minutes_today,
        minutes_this_week=p.minutes_this_week,
        last_active_date=p.last_active_date,
        tour_completed=p.tour_completed,
        current_tour_step=p.current_tour_step,
        completed_lessons=p.completed_lessons or [],
        daily_goal_history=p.daily_goal_history or {},
        lesson_scores=scores,
        current_difficulty=p.current_difficulty,
        minutes_total=p.minutes_total
    )


@router.post("/sync", response_model=VinaProgress)
def sync_progress(
    sync_data: ProgressSyncRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Sync client-side progress updates (minutes, diamonds)."""
    p = current_user.progress
    if not p:
         raise HTTPException(status_code=404, detail="Progress not initialized")

    if sync_data.minutes_added > 0:
        # Simple Date Logic
        today = date.today().isoformat()
        
        if p.last_active_date != today:
            # New day: Reset daily minutes
            p.minutes_today = sync_data.minutes_added
            # Logic for streak update could happen here too, but frontend usually handles streak logic locally + backend verification.
            # We'll rely on explicit actions or just login activity for streaks for now.
            p.last_active_date = today
        else:
            p.minutes_today += sync_data.minutes_added
            
        p.minutes_this_week += sync_data.minutes_added
        p.minutes_total += sync_data.minutes_added

    if sync_data.diamonds_earned > 0:
        p.diamonds += sync_data.diamonds_earned
        
    session.add(p)
    session.commit()
    session.refresh(current_user)
    return get_progress(current_user)


@router.post("/lesson/{lesson_id}/complete", response_model=VinaProgress)
def complete_lesson(
    lesson_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Mark a lesson as complete and award completion bonuses."""
    p = current_user.progress
    if not p:
         raise HTTPException(status_code=404, detail="Progress not initialized")
    
    # Add to completed list
    completed_set = set(p.completed_lessons or [])
    if lesson_id not in completed_set:
        completed_list = list(completed_set)
        completed_list.append(lesson_id)
        p.completed_lessons = completed_list
        
        # Award Diamonds (First time completion bonus)
        p.diamonds += 50
        
        # Update Streak if first activity today
        today = date.today().isoformat()
        if p.last_active_date != today:
            p.streak += 1
            p.last_active_date = today

    session.add(p)
    session.commit()
    session.refresh(current_user)
    return get_progress(current_user)
