from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from vina_backend.core.security import get_password_hash, verify_password, create_access_token
from vina_backend.core.config import get_settings
from vina_backend.integrations.db.session import get_session
from vina_backend.integrations.db.models.user import User, UserProfile, UserProgress
from vina_backend.domain.schemas.auth import UserRegister, UserLogin, Token

router = APIRouter(prefix="/auth", tags=["authentication"])
settings = get_settings()


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, session: Session = Depends(get_session)):
    """Register a new user and initialize profile/progress."""
    # 1. Check existing
    statement = select(User).where(User.email == user_data.email)
    if session.exec(statement).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # 2. Create User
    hashed_pw = get_password_hash(user_data.password) if user_data.password else None
    new_user = User(
        email=user_data.email,
        full_name=user_data.fullName,
        hashed_password=hashed_pw
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    
    # 3. Create defaults
    # Profile (empty/defaults)
    new_profile = UserProfile(user_id=new_user.id)
    session.add(new_profile)
    
    # Progress (zeroed)
    new_progress = UserProgress(user_id=new_user.id)
    session.add(new_progress)
    
    session.commit()
    
    # 4. Token
    access_token = create_access_token(subject=str(new_user.id))
    
    # Map to frontend schema
    user_resp = {
        "id": new_user.id,
        "email": new_user.email,
        "fullName": new_user.full_name,
        "onboardingResponses": new_profile.onboarding_responses if new_profile else {},
        "resolution": new_profile.resolution if new_profile else "",
        "dailyGoalMinutes": new_profile.daily_goal_minutes if new_profile else 15
    }
    
    return Token(
        access_token=access_token, 
        token_type="bearer",
        user=user_resp
    )


@router.post("/login", response_model=Token)
def login(login_data: UserLogin, session: Session = Depends(get_session)):
    """Authenticate user and return JWT."""
    statement = select(User).where(User.email == login_data.email)
    user = session.exec(statement).first()
    
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    # Simple password check
    if login_data.password and user.hashed_password:
         if not verify_password(login_data.password, user.hashed_password):
              raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif user.hashed_password and not login_data.password:
         # User has PW but didn't provide it
         raise HTTPException(status_code=400, detail="Password required")
    
    access_token = create_access_token(subject=str(user.id))
    
    # Map to frontend schema
    user_resp = {
        "id": user.id,
        "email": user.email,
        "fullName": user.full_name,
        "onboardingResponses": user.profile.onboarding_responses if user.profile else {},
        "resolution": user.profile.resolution if user.profile else "",
        "dailyGoalMinutes": user.profile.daily_goal_minutes if user.profile else 15
    }
    
    return Token(
        access_token=access_token, 
        token_type="bearer",
        user=user_resp
    )
