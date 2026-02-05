"""
Clear all cached lessons from the database.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from vina_backend.integrations.db.engine import init_db, get_session
from vina_backend.services.lesson_cache import LessonCache

def clear_cache():
    """Delete all cached lessons."""
    print("🗑️  Clearing lesson cache...")
    
    session_gen = get_session()
    db_session = next(session_gen)
    
    try:
        count = db_session.query(LessonCache).count()
        print(f"   Found {count} cached lessons")
        
        if count > 0:
            db_session.query(LessonCache).delete()
            db_session.commit()
            print(f"   ✅ Deleted {count} cached lessons")
        else:
            print(f"   ℹ️  Cache is already empty")
        
    finally:
        db_session.close()

if __name__ == "__main__":
    init_db()
    clear_cache()
    print("\n✅ Cache cleared successfully!")
