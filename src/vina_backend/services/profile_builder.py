"""
User profile generation service.
Handles the creation of personalized user profiles based on profession, industry, and experience.
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any

from vina_backend.integrations.llm.client import get_llm_client
from vina_backend.domain.schemas.profile import UserProfileData
from vina_backend.integrations.db.session import get_session
from vina_backend.integrations.db.repositories.profile_repository import ProfileRepository

logger = logging.getLogger(__name__)


# Load prompt template
PROMPTS_DIR = Path(__file__).parent.parent / "prompts" / "profile"
with open(PROMPTS_DIR / "user_profile_gen.md", "r") as f:
    USER_PROFILE_PROMPT_TEMPLATE = f.read()


def generate_user_profile(
    profession: str,
    industry: str,
    experience_level: str,
) -> UserProfileData:
    """
    Generate a user profile using the LLM.
    
    Args:
        profession: User's profession (e.g., "Clinical Researcher")
        industry: User's industry (e.g., "Pharma/Biotech")
        experience_level: Experience level ("Beginner", "Intermediate", "Advanced")
    
    Returns:
        Generated user profile
    
    Raises:
        ValueError: If generation fails or produces invalid data
    """
    # Format the prompt with user inputs
    prompt = USER_PROFILE_PROMPT_TEMPLATE.format(
        profession=profession,
        industry=industry,
        experience_level=experience_level,
    )
    
    # Get LLM client and generate JSON response
    llm_client = get_llm_client()
    
    logger.info(f"Generating user profile for {profession} in {industry}")
    
    try:
        profile_data = llm_client.generate_json(
            prompt=prompt,
            max_tokens=2000,  # Increased for safety_priorities and high_stakes_areas
            # temperature will be automatically set to safest default (1.0 for Gemini 3)
            
        )
        
        # Validate and parse into Pydantic model
        profile = UserProfileData(**profile_data)
        
        logger.info(f"Successfully generated profile for {profession}")
        return profile
    
    except Exception as e:
        logger.error(f"Failed to generate profile for {profession}: {str(e)}")
        raise ValueError(
            f"Failed to generate profile for {profession} in {industry}: {str(e)}"
        ) from e


def get_or_create_user_profile(
    profession: str,
    industry: str,
    experience_level: str,
    force_refresh: bool = False,
) -> UserProfileData:
    """
    Get a user profile from the database, or generate it if it doesn't exist.
    
    Args:
        profession: User's profession
        industry: User's industry
        experience_level: Experience level
        force_refresh: If True, regenerate profile even if it exists in DB
    
    Returns:
        User profile data
    """
    # Use the session generator
    session_gen = get_session()
    session = next(session_gen)
    
    try:
        repo = ProfileRepository(session)
        
        # 1. Check if it exists in DB (unless force_refresh is True)
        if not force_refresh:
            db_profile = repo.get_profile(profession, industry, experience_level)
            
            if db_profile:
                logger.info(f"Retrieved profile for {profession} from database")
                # Convert back to UserProfileData schema
                return UserProfileData(
                    profession=db_profile.profession,
                    industry=db_profile.industry,
                    experience_level=db_profile.experience_level,
                    daily_responsibilities=db_profile.daily_responsibilities,
                    pain_points=db_profile.pain_points,
                    typical_outputs=db_profile.typical_outputs,
                    technical_comfort_level=db_profile.technical_comfort_level,
                    learning_style_notes=db_profile.learning_style_notes,
                    professional_goals=db_profile.professional_goals,
                    safety_priorities=db_profile.safety_priorities,
                    high_stakes_areas=db_profile.high_stakes_areas
                )
        else:
            logger.info(f"Force refresh requested for {profession}. Ignoring DB.")
        
        # 2. Not found or force refresh, generate it
        if not force_refresh:
            logger.info(f"Profile for {profession} not found in DB, generating new one...")
        
        profile_data = generate_user_profile(profession, industry, experience_level)
        
        # 3. Save it for next time (Repo will overwrite if force_refresh was used)
        repo.save_profile(profile_data)
        
        logger.info(f"Saved profile for {profession} to database")
        
        return profile_data
        
    finally:
        # Closing the session
        session.close()


def validate_profile(profile_data: Dict[str, Any]) -> bool:
    """
    Validate that a profile has all required fields and reasonable content.
    
    Args:
        profile_data: Profile dictionary to validate
    
    Returns:
        True if valid, False otherwise
    """
    try:
        # Try to parse as Pydantic model (will raise if invalid)
        UserProfileData(**profile_data)
        
        # Additional validation: check that lists aren't empty or too short
        if len(profile_data.get("daily_responsibilities", [])) < 2:
            logger.warning("Profile validation failed: insufficient daily_responsibilities")
            return False
        if len(profile_data.get("pain_points", [])) < 2:
            logger.warning("Profile validation failed: insufficient pain_points")
            return False
        if len(profile_data.get("professional_goals", [])) < 1:
            logger.warning("Profile validation failed: insufficient professional_goals")
            return False
        if len(profile_data.get("typical_outputs", [])) < 2:
            logger.warning("Profile validation failed: insufficient typical_outputs")
            return False
        if len(profile_data.get("safety_priorities", [])) < 2:
            logger.warning("Profile validation failed: insufficient safety_priorities")
            return False
        if len(profile_data.get("high_stakes_areas", [])) < 2:
            logger.warning("Profile validation failed: insufficient high_stakes_areas")
            return False
        
        return True
    
    except Exception as e:
        logger.warning(f"Profile validation failed: {str(e)}")
        return False