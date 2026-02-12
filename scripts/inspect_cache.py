
import sys
from pathlib import Path
from sqlmodel import Session, select
from sqlalchemy import create_engine

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from vina_backend.core.config import get_settings
from vina_backend.services.lesson_cache import LessonCache

def inspect_cache():
    settings = get_settings()
    engine = create_engine(settings.database_url)
    
    with Session(engine) as session:
        statement = select(LessonCache)
        entries = session.exec(statement).all()
        
        print(f"Found {len(entries)} cached lessons.")
        for entry in entries:
            print(f"\n--- Cache Entry {entry.id} ---")
            print(f"Key: {entry.cache_key}")
            print(f"Course: {entry.course_id}")
            print(f"Lesson: {entry.lesson_id}")
            print(f"Model: {entry.llm_model}")
            print(f"Difficulty: {entry.difficulty_level}")
            print(f"Context: {entry.adaptation_context}")
            print(f"Video URL: {entry.video_url}")
            print(f"Profile Hash: {entry.profile_hash}")

if __name__ == "__main__":
    inspect_cache()
