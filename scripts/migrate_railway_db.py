"""
Database migration script for Railway deployment.
Run this after deploying to Railway to ensure the database schema is up-to-date.
"""
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from vina_backend.integrations.db.engine import init_db, engine
from vina_backend.integrations.db.models.user import User, UserProfile, UserProgress
from vina_backend.integrations.db.models.session import Session as UserSession
from vina_backend.integrations.db.models.quiz_attempt import QuizAttempt
from vina_backend.services.lesson_cache import LessonCache
from sqlmodel import Session, select

def migrate_database():
    """Initialize database and create all tables."""
    print("🔄 Initializing database...")
    init_db()
    print("✅ Database initialized successfully!")
    
    # Verify tables were created
    with Session(engine) as session:
        print("\n📊 Verifying tables...")
        
        # Check if tables exist by trying to query them
        tables = [
            ("users", User),
            ("user_profiles", UserProfile),
            ("user_progress", UserProgress),
            ("sessions", UserSession),
            ("quiz_attempts", QuizAttempt),
            ("lesson_cache", LessonCache)
        ]
        
        for table_name, model in tables:
            try:
                result = session.exec(select(model).limit(1)).first()
                print(f"  ✅ {table_name} - OK")
            except Exception as e:
                print(f"  ❌ {table_name} - ERROR: {e}")
    
    print("\n✨ Migration complete!")

if __name__ == "__main__":
    migrate_database()
