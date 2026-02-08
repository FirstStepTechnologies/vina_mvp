from typing import Annotated, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlmodel import Session
from vina_backend.integrations.db.session import get_session
from vina_backend.integrations.db.models.user import User, UserProfile
from vina_backend.domain.schemas.profile import UserProfileResponse, UserProfileData
from vina_backend.api.dependencies import get_current_user

router = APIRouter(prefix="/user/profile", tags=["user"])


def _map_profile_to_response(user: User) -> UserProfileResponse:
    """Helper to map DB User model to Pydantic Response."""
    p = user.profile
    if not p:
        # Fallback for bare user accounts
        profile_data = UserProfileData(
            profession="Unassigned",
            industry="Unassigned",
            experience_level="Beginner",
            daily_responsibilities=[],
            pain_points=[],
            typical_outputs=[],
            professional_goals=[],
            safety_priorities=[],
            high_stakes_areas=[],
            technical_comfort_level="Low",
            learning_style_notes="",
            resolution="",
            daily_goal_minutes=15,
            onboarding_responses={}
        )
    else:
        profile_data = UserProfileData(
            profession=p.profession or "Unassigned",
            industry=p.industry or "Unassigned",
            experience_level=p.experience_level or "Beginner",
            leadership_level=p.leadership_level or "Individual Contributor",
            daily_responsibilities=p.daily_responsibilities,
            pain_points=p.pain_points,
            typical_outputs=p.typical_outputs,
            professional_goals=p.professional_goals,
            safety_priorities=p.safety_priorities,
            high_stakes_areas=p.high_stakes_areas,
            technical_comfort_level=p.technical_comfort_level or "Low",
            learning_style_notes=p.learning_style_notes or "",
            resolution=p.resolution,
            daily_goal_minutes=p.daily_goal_minutes,
            onboarding_responses=p.onboarding_responses
        )

    return UserProfileResponse(
        profile=profile_data,
        generated_from_cache=False,
        id=str(user.id),
        email=user.email,
        created_at=user.created_at.isoformat(),
        resolution=profile_data.resolution,
        dailyGoalMinutes=profile_data.daily_goal_minutes
    )


@router.get("", response_model=UserProfileResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    """Get the current user's profile."""
    return _map_profile_to_response(current_user)


@router.patch("", response_model=UserProfileResponse)
def update_profile(
    updates: Dict[str, Any] = Body(...),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Update specific profile fields (e.g., dailyGoalMinutes, resolution)."""
    profile = current_user.profile
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
        
    # Allowed updates whitelist (simple implementation)
    allowed_fields = {
        "daily_goal_minutes", "resolution", "profession", "industry", 
        "experience_level", "leadership_level", "onboarding_responses"
    }
    
    # Map camelCase from frontend to snake_case if needed
    key_map = {
        "dailyGoalMinutes": "daily_goal_minutes",
        "role": "profession",
        "experience": "experience_level",
        "level": "leadership_level"
    }
    
    for key, value in updates.items():
        db_key = key_map.get(key, key)
        if db_key in allowed_fields and hasattr(profile, db_key):
             setattr(profile, db_key, value)
    
    session.add(profile)
    session.commit()
    session.refresh(current_user)
    return _map_profile_to_response(current_user)


@router.post("/reset-pathway")
def reset_pathway(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Reset user progress to trigger a new pathway generation."""
    # Logic: Clear progress, keep profile identity
    if current_user.progress:
        current_user.progress.completed_lessons = []
        current_user.progress.lesson_scores = {}
        current_user.progress.current_tour_step = 0
        current_user.progress.tour_completed = False
        # Do not reset accumulated diamonds/streak for now (retention feature)
        
        session.add(current_user.progress)
        session.commit()
    
    # Note: Frontend will redirect to Onboarding/Loading after this
    return {
        "status": "reset_complete",
        "newCourseMapId": "generated_at_runtime" 
    }
