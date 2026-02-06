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
    View a complete lesson and export its markdown report.
    """
    print(f"\n🔍 Processing lesson for:")
    print(f"   Target: {profession} ({experience})")
    print(f"   Lesson: {lesson_id}")
    
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
        
        # Export the Markdown Report (The Audit Trail)
        report_path = generator.export_generation_report(
            generated_lesson,
            Path("cache/reports"),
            profile
        )
        
        print_separator("-")
        print(f"✅ Lesson Title: {generated_lesson.lesson_content.lesson_title}")
        print(f"✅ Metadata: Model={generated_lesson.generation_metadata.llm_model}, Cached={generated_lesson.generation_metadata.cache_hit}")
        print(f"📄 Markdown Audit Report saved to: {report_path}")
        print_separator("-")
        
        # Optionally show small preview or full content
        # print_lesson_full_content(generated_lesson)
        
    finally:
        db_session.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="VINA Lesson Content Viewer & Report Generator")
    parser.add_argument("--prof", default=None, help="Profession name")
    parser.add_argument("--prof-num", type=int, choices=[1, 2, 3, 4], help="Profession Code (1:HR, 2:PM, 3:Marketing, 4:Clinical)")
    parser.add_argument("--ind", default=None, help="Industry (Auto-mapped if omitted)")
    parser.add_argument("--exp", default="Beginner", choices=["Beginner", "Intermediate", "Advanced"], help="Experience level (default: Beginner)")
    parser.add_argument("--lesson", default="l01_what_llms_are", help="Lesson ID")
    parser.add_argument("--lesson-num", type=int, help="Lesson Number (overrides --lesson)")
    parser.add_argument("--diff", type=int, default=3, help="Difficulty level 1, 3, or 5 (default: 3)")
    
    args = parser.parse_args()

    # 1. Resolve Profession and Industry
    prof_map = {
        1: ("HR Manager", "Tech Company"),
        2: ("Project Manager", "Software/Tech"),
        3: ("Marketing Manager", "E-Commerce"),
        4: ("Clinical Researcher", "Pharma/Biotech")
    }
    
    # Reverse map for string-to-industry lookups
    reverse_prof_map = {name: ind for code, (name, ind) in prof_map.items()}

    final_prof = args.prof
    final_ind = args.ind

    # If code is provided, it takes priority
    if args.prof_num:
        final_prof, auto_ind = prof_map[args.prof_num]
        if not final_ind:
            final_ind = auto_ind
    
    # If prof string is provided but no industry, try to auto-map it
    if final_prof and not final_ind:
        final_ind = reverse_prof_map.get(final_prof)

    # Final Fallback
    if not final_prof:
        final_prof = "HR Manager"
    if not final_ind:
        final_ind = "Tech Company"

    # 2. Resolve Lesson ID
    final_lesson_id = args.lesson
    if args.lesson_num:
        try:
            from vina_backend.services.course_loader import load_course_config
            config = load_course_config("c_llm_foundations")
            lessons = config.get("lessons", [])
            if 1 <= args.lesson_num <= len(lessons):
                final_lesson_id = lessons[args.lesson_num - 1]["lesson_id"]
        except:
            pass
    
    setup_logging("WARNING")
    init_db()
    
    print_separator("=")
    print("📖 VINA LESSON REPORT GENERATOR")
    print_separator("=")
    
    view_lesson(
        profession=final_prof,
        industry=final_ind,
        experience=args.exp,
        lesson_id=final_lesson_id,
        difficulty=args.diff
    )
