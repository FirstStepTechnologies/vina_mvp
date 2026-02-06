"""
Utility script to clear the Lesson Cache.
Useful after major prompt updates to ensure all cached lessons 
conform to the new structure.
"""
import logging
from sqlmodel import Session, select, delete
from vina_backend.integrations.db.engine import engine
from vina_backend.services.lesson_cache import LessonCache

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clear_cache(keep_last: bool = True):
    with Session(engine) as session:
        if keep_last:
            # Find the ID of the most recently created lesson
            statement = select(LessonCache).order_by(LessonCache.created_at.desc()).limit(1)
            last_lesson = session.exec(statement).first()
            
            if last_lesson:
                logger.info(f"Keeping the most recent lesson: {last_lesson.lesson_id} (ID: {last_lesson.id})")
                # Delete everything EXCEPT this ID
                delete_statement = delete(LessonCache).where(LessonCache.id != last_lesson.id)
                result = session.exec(delete_statement)
                session.commit()
                logger.info(f"Cleanup complete. Removed {result.rowcount} old lessons.")
            else:
                logger.info("Cache is already empty.")
        else:
            # Delete everything
            delete_statement = delete(LessonCache)
            result = session.exec(delete_statement)
            session.commit()
            logger.info(f"Cleanup complete. Removed all {result.rowcount} lessons.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true", help="Delete ALL lessons (don't keep the last one)")
    args = parser.parse_args()
    
    clear_cache(keep_last=not args.all)
