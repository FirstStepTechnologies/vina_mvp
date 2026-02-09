
import sys
from sqlmodel import Session, select, create_engine
from vina_backend.integrations.db.models.user import User, UserProgress
from vina_backend.core.config import get_settings

# Force correct DB path relative to root
db_url = "sqlite:///data/vina.db"
engine = create_engine(db_url)

def reset_progress(email: str):
    print(f"Resetting progress for: {email}")
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == email)).first()
        if not user:
            print("User not found")
            return
            
        if not user.progress:
            print("User has no progress record")
            return
            
        print(f"Current completed: {user.progress.completed_lessons}")
        
        # Reset
        user.progress.completed_lessons = []
        user.progress.lesson_scores = {}
        # user.progress.diamonds = 0 # Optional
        
        session.add(user.progress)
        session.commit()
        session.refresh(user.progress)
        
        print(f"New completed: {user.progress.completed_lessons}")
        print("Progress reset successfully.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/reset_user_progress.py <email>")
        sys.exit(1)
    reset_progress(sys.argv[1])
