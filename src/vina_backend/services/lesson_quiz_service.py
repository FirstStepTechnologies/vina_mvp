
import logging
import json
from pathlib import Path
from typing import Dict, Any, Optional
from vina_backend.domain.schemas.lesson_quiz import LessonQuiz

logger = logging.getLogger(__name__)

# Path to the JSON file containing pre-generated quizzes
QUIZZES_FILE_PATH = Path(__file__).parent.parent / "domain/constants/lesson_quizzes.json"

async def get_lesson_quiz(lesson_id: str, profession: str) -> Optional[LessonQuiz]:
    """
    Retrieve specific quiz for a lesson and profession.
    
    Args:
        lesson_id: The lesson ID (e.g. "l05_hallucinations")
        profession: The user's profession (e.g. "Clinical Researcher")
        
    Returns:
        LessonQuiz object or None if not found
    """
    try:
        # Load quizzes from JSON file
        # In production, this might come from a DB or be cached in memory
        if not QUIZZES_FILE_PATH.exists():
            logger.error(f"Quiz file not found at: {QUIZZES_FILE_PATH}")
            return None
            
        with open(QUIZZES_FILE_PATH, "r") as f:
            quizzes_data = json.load(f)
            
        if lesson_id not in quizzes_data:
            logger.warning(f"No quizzes found for lesson: {lesson_id}")
            return None
            
        lesson_quizzes = quizzes_data[lesson_id]
        
        if profession not in lesson_quizzes:
            logger.warning(f"No quiz found for {lesson_id} and profession {profession}")
            return None
            
        quiz_data = lesson_quizzes[profession]
        return LessonQuiz(**quiz_data)
        
    except Exception as e:
        logger.error(f"Error retrieving quiz: {e}")
        return None

async def get_next_lesson(current_lesson_id: str) -> Optional[str]:
    """
    Determine the next lesson ID based on current lesson.
    Values ideally come from course_config.
    """
    try:
         # TODO: Load this from actual Course structure/config
         # For now, simplistic logic based on naming convention l01 -> l02
         
         # Parse number
         parts = current_lesson_id.split('_')
         if not parts or not parts[0].startswith('l'):
             return None
             
         num_str = parts[0][1:] # '01'
         current_num = int(num_str)
         next_num = current_num + 1
         
         # Check if next lesson exists in our known list (or file)
         # Simplistic look ahead specific to this MVP
         if next_num > 17: # Max lessons
             return None
             
         # We need the full ID.
         # For this specific task, lets utilize the lesson loader if needed, 
         # or just return the ID if we strictly follow numeric order.
         # But we don't know the NAME suffix (e.g. _what_llms_are) without looking it up.
         
         from vina_backend.services.course_loader import load_course_config
         config = load_course_config("c_llm_foundations")
         lessons = config.get("lessons", [])
         
         for i, lesson in enumerate(lessons):
             if lesson["lesson_id"] == current_lesson_id:
                 if i + 1 < len(lessons):
                     return lessons[i+1]["lesson_id"]
                 else:
                     return None # Last lesson
                     
         return None
         
    except Exception as e:
        logger.error(f"Error determining next lesson: {e}")
        return None
