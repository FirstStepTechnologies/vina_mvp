"""
Script to view the complete contents of a generated lesson.
Displays all slides with full content and speaker notes.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import json
from vina_backend.utils.logging import setup_logging
from vina_backend.integrations.db.engine import init_db, get_session
from vina_backend.services.profile_builder import get_or_create_user_profile
from vina_backend.services.lesson_cache import LessonCacheService
from vina_backend.services.lesson_generator import LessonGenerator

import logging
logger = logging.getLogger(__name__)


def print_separator(char="=", length=100):
    """Print a separator line."""
    print(char * length)


def print_lesson_full_content(generated_lesson):
    """Print the raw JSON of the lesson as stored in the database."""
    
    # Convert the entire generated lesson to a dictionary
    lesson_dict = {
        "lesson_id": generated_lesson.lesson_id,
        "course_id": generated_lesson.course_id,
        "difficulty_level": generated_lesson.difficulty_level,
        "lesson_content": generated_lesson.lesson_content.model_dump(),
        "generation_metadata": generated_lesson.generation_metadata.model_dump()
    }
    
    # Print as formatted JSON
    print(json.dumps(lesson_dict, indent=2))


def view_lesson(
    profession: str = "Clinical Researcher",
    industry: str = "Pharma/Biotech",
    experience: str = "Intermediate",
    lesson_id: str = "l01_what_llms_are",
    course_id: str = "c_llm_foundations",
    difficulty: int = 3
):
    """
    View a complete lesson with all content.
    
    Args:
        profession: User profession
        industry: User industry
        experience: Experience level
        lesson_id: Lesson to view
        course_id: Course ID
        difficulty: Difficulty level (1, 3, or 5)
    """
    print(f"\n🔍 Retrieving lesson for:")
    print(f"   Profession: {profession}")
    print(f"   Industry: {industry}")
    print(f"   Experience: {experience}")
    print(f"   Lesson: {lesson_id}")
    print(f"   Difficulty: {difficulty}\n")
    
    session_gen = get_session()
    db_session = next(session_gen)
    
    try:
        # Get user profile
        profile = get_or_create_user_profile(profession, industry, experience)
        
        # Initialize services
        cache_service = LessonCacheService(db_session)
        generator = LessonGenerator(cache_service)
        
        # Generate/retrieve lesson
        generated_lesson = generator.generate_lesson(
            lesson_id=lesson_id,
            course_id=course_id,
            user_profile=profile,
            difficulty_level=difficulty
        )
        
        # Display full content
        print_lesson_full_content(generated_lesson)
        
    finally:
        db_session.close()


if __name__ == "__main__":
    setup_logging()
    init_db()
    
    print_separator("=")
    print("📖 LESSON CONTENT VIEWER")
    print_separator("=")
    
    # You can modify these parameters to view different lessons
    view_lesson(
        profession="Clinical Researcher",
        industry="Pharma/Biotech",
        experience="Intermediate",
        lesson_id="l01_what_llms_are",
        course_id="c_llm_foundations",
        difficulty=3
    )
