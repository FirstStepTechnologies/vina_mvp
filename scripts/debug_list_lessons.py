"""
Script to list all valid LESSON_ID values for a given course.
Defaults to "c_llm_foundations".
"""
import sys
import json
from pathlib import Path

# Add src to path so we can import modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from vina_backend.services.course_loader import load_course_config

def list_lessons(course_id: str = "c_llm_foundations"):
    print(f"\n📚 Listing lessons for Course ID: {course_id}")
    print("=" * 60)
    
    try:
        config = load_course_config(course_id)
        lessons = config.get("lessons", [])
        
        if not lessons:
            print("⚠️ No lessons found in configuration.")
            return

        print(f"{'#':<5} | {'LESSON ID':<30} | {'TITLE'}")
        print("-" * 60)
        
        for i, lesson in enumerate(lessons):
            # i+1 makes it 1-based index for user friendliness
            print(f"{i+1:<5} | {lesson.get('lesson_id'):<30} | {lesson.get('lesson_name')}")
            
        print("=" * 60)
        print(f"Total: {len(lessons)} lessons found.\n")
        
    except FileNotFoundError:
        print(f"❌ Course configuration file not found for: {course_id}")
    except Exception as e:
        print(f"❌ Error loading course config: {e}")

if __name__ == "__main__":
    # Allow user to pass a different course_id if desired
    # Usage: python scripts/debug_list_lessons.py [course_id]
    target_course = sys.argv[1] if len(sys.argv) > 1 else "c_llm_foundations"
    list_lessons(target_course)
