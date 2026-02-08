
import json
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any
from sqlmodel import Session, select, create_engine, SQLModel

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from vina_backend.services.lesson_cache import LessonCache
from vina_backend.core.config import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

BACKUP_FILE = Path("data/lesson_cache_backup.json")
DB_URL = settings.database_url

def get_engine():
    return create_engine(DB_URL, connect_args={"check_same_thread": False})

def backup_lesson_cache():
    """Export all LessonCache entries to a JSON file."""
    engine = get_engine()
    
    # Check if table exists
    try:
        with Session(engine) as session:
            statement = select(LessonCache)
            results = session.exec(statement).all()
            
            data = [route.model_dump() for route in results]
            
            with open(BACKUP_FILE, "w") as f:
                json.dump(data, f, indent=2, default=str)
                
            logger.info(f"Successfully backed up {len(data)} lesson cache entries to {BACKUP_FILE}")
            return True
    except Exception as e:
        logger.error(f"Backup failed: {e}")
        return False

def restore_lesson_cache():
    """Import LessonCache entries from JSON file into the database."""
    if not BACKUP_FILE.exists():
        logger.error(f"Backup file {BACKUP_FILE} not found.")
        return False
        
    engine = get_engine()
    
    # Ensure table exists (init_db should have been run, but just in case)
    SQLModel.metadata.create_all(engine)
    
    try:
        with open(BACKUP_FILE, "r") as f:
            data = json.load(f)
            
        with Session(engine) as session:
            count = 0
            for item in data:
                # Handle potential ID conflicts or let DB assign new IDs if needed
                # For cache restoration, we likely want to keep keys intact but IDs might change
                # Let's remove ID to allow auto-increment if we are rigorous, 
                # but if we want exact restoration, we keep it. 
                # SQLModel `.model_validate` handles dict -> object conversion
                
                # Clean up specific fields if needed (e.g. datetime strings back to objects)
                # Pydantic/SQLModel usually handles ISO strings automatically.
                
                # Check for duplicates before inserting
                existing = session.exec(select(LessonCache).where(LessonCache.cache_key == item["cache_key"])).first()
                if not existing:
                    entry = LessonCache.model_validate(item)
                    session.add(entry)
                    count += 1
            
            session.commit()
            logger.info(f"Successfully restored {count} entries (skipped {len(data) - count} duplicates).")
            return True

    except Exception as e:
        logger.error(f"Restore failed: {e}")
        return False

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Backup/Restore Lesson Cache")
    parser.add_argument("action", choices=["backup", "restore"], help="Action to perform")
    
    args = parser.parse_args()
    
    if args.action == "backup":
        backup_lesson_cache()
    elif args.action == "restore":
        restore_lesson_cache()
