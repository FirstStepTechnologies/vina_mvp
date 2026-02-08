from typing import Generator, Optional
from vina_backend.integrations.db.models.user import UserProfile

async def get_current_user() -> UserProfile:
    """
    Mock dependency to return a default user for development/hackathon.
    In a real app, this would decode JWT and fetch user from DB.
    """
    # Return a dummy user compliant with the SQLModel
    return UserProfile(
        id=1,
        profession="HR Manager",
        industry="Technology",
        experience_level="Intermediate",
        daily_responsibilities=["Recruiting", "Employee Relations"],
        pain_points=["Time management"],
        typical_outputs=["Offer letters"],
        technical_comfort_level="Medium",
        learning_style_notes="Visual",
        professional_goals=["Become Director"],
        safety_priorities=["Compliance"],
        high_stakes_areas=["Hiring decisions"],
        created_at="2023-01-01T00:00:00",
        updated_at="2023-01-01T00:00:00"
    )
