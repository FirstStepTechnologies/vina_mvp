
from sqlmodel import Session, select, create_engine, SQLModel
# Ensure models are registered
from vina_backend.integrations.db.models.user import User, UserProgress
from vina_backend.core.config import get_settings

settings = get_settings()
# Force correct DB path relative to root
db_url = "sqlite:///data/vina.db" # Default
engine = create_engine(db_url)

def inspect_progress():
    print(f"Inspecting DB at: {db_url}")
    with Session(engine) as session:
        try:
            statement = select(User)
            users = session.exec(statement).all()
            print(f"Found {len(users)} users.")
            
            for u in users:
                print(f"User: {u.email} (ID: {u.id})")
                if u.progress:
                    print(f"  Completed Lessons: {u.progress.completed_lessons}")
                    print(f"  Diamonds: {u.progress.diamonds}")
                    # print(f"  Current Lesson: {u.progress.current_lesson_id}") 
                else:
                    print("  No Progress Record")
                print("-" * 20)
        except Exception as e:
            print(f"Error querying DB: {e}")

if __name__ == "__main__":
    inspect_progress()
