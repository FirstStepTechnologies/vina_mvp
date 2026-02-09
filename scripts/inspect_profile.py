
from sqlmodel import Session, select, create_engine
from vina_backend.integrations.db.models.user import User, UserProfile, UserProgress
from vina_backend.core.config import get_settings

settings = get_settings()
db_url = "sqlite:///data/vina.db"
engine = create_engine(db_url)

def inspect_profile():
    print(f"Inspecting Profile for vina.learner@example.com")
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == "vina.learner@example.com")).first()
        if not user:
            print("User not found")
            return
            
        print(f"User ID: {user.id}")
        if user.profile:
            print(f"Profession: {user.profile.profession}")
            print(f"Industry: {user.profile.industry}")
            print(f"Onboarding Responses: {user.profile.onboarding_responses}")
        else:
            print("No Profile")
            
        if user.progress:
             print(f"Completed Lessons: {user.progress.completed_lessons}")
             print(f"Lesson Scores: {user.progress.lesson_scores}")

if __name__ == "__main__":
    inspect_profile()
