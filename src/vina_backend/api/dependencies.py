from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlmodel import Session
from vina_backend.core.config import get_settings
from vina_backend.integrations.db.session import get_session
from vina_backend.integrations.db.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")
settings = get_settings()

# Alias for compatibility
get_db = get_session


import logging

logger = logging.getLogger(__name__)

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session: Session = Depends(get_session)) -> User:
    """Validate JWT token and retrieve current user."""
    # ... (existing setup code for credentials_exception) ...
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.algorithm])
        user_id: str = payload.get("sub")
        if user_id is None:
            logger.warning("Token payload missing 'sub' claim")
            raise credentials_exception
    except JWTError as e:
        logger.warning(f"JWT validation error: {str(e)}")
        raise credentials_exception
    
    user = session.get(User, user_id)
    if user is None:
        logger.warning(f"User ID {user_id} from token not found in database")
        raise credentials_exception
        
    logger.debug(f"Authenticated user: {user.email} (ID: {user.id})")
    return user

async def get_current_user_optional(
    token: Annotated[str, Depends(OAuth2PasswordBearer(tokenUrl="api/v1/auth/login", auto_error=False))],
    session: Session = Depends(get_session)
) -> User | None:
    """
    Validate JWT token if present, but return None instead of raising 401 if missing/invalid.
    Useful for endpoints that support both authenticated and anonymous access.
    """
    if not token:
        return None
        
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.algorithm])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
    except JWTError:
        return None
    
    user = session.get(User, user_id)
    return user
