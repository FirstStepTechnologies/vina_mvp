from typing import Optional
from sqlmodel import Session, select
from vina_backend.integrations.db.models.user import UserProfile
from vina_backend.domain.schemas.profile import UserProfileData

class ProfileRepository:
    """Repository for managing user profile persistence."""
    
    def __init__(self, session: Session):
        self.session = session

    def get_profile(
        self, 
        profession: str, 
        industry: str, 
        experience_level: str
    ) -> Optional[UserProfile]:
        """Retrieve a profile by profession, industry, and experience level."""
        statement = select(UserProfile).where(
            UserProfile.profession == profession,
            UserProfile.industry == industry,
            UserProfile.experience_level == experience_level
        )
        return self.session.exec(statement).first()

    def delete_profile(self, profession: str, industry: str, experience_level: str) -> bool:
        """Delete a profile from the database."""
        db_profile = self.get_profile(profession, industry, experience_level)
        if db_profile:
            self.session.delete(db_profile)
            self.session.commit()
            return True
        return False

    def save_profile(self, profile_data: UserProfileData) -> UserProfile:
        """Save a generated profile to the database (overwrites existing)."""
        # Ensure we don't have a duplicate
        self.delete_profile(
            profile_data.profession, 
            profile_data.industry, 
            profile_data.experience_level
        )

        db_profile = UserProfile(
            profession=profile_data.profession,
            industry=profile_data.industry,
            experience_level=profile_data.experience_level,
            daily_responsibilities=profile_data.daily_responsibilities,
            pain_points=profile_data.pain_points,
            typical_outputs=profile_data.typical_outputs,
            professional_goals=profile_data.professional_goals,
            technical_comfort_level=profile_data.technical_comfort_level,
            learning_style_notes=profile_data.learning_style_notes,
            safety_priorities=profile_data.safety_priorities,
            high_stakes_areas=profile_data.high_stakes_areas
        )
        self.session.add(db_profile)
        self.session.commit()
        self.session.refresh(db_profile)
        return db_profile
