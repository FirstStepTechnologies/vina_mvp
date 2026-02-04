"""
Course configuration loader.
Loads global config and course-specific configs.
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional

# Path to the constants directory relative to this file
CONSTANTS_DIR = Path(__file__).resolve().parent.parent / "domain" / "constants"


def load_global_config() -> Dict[str, Any]:
    """Load global course configuration (shared across all courses)."""
    global_path = CONSTANTS_DIR / "course_config_global.json"
    if not global_path.exists():
        raise FileNotFoundError(f"Global config not found at {global_path}")
        
    with open(global_path, "r") as f:
        return json.load(f)


def load_course_config(course_id: str) -> Dict[str, Any]:
    """
    Load course-specific configuration.
    
    Args:
        course_id: Course identifier (e.g., "c_llm_foundations")
    
    Returns:
        Course configuration
    """
    # Convert course_id to filename (e.g., "c_llm_foundations" -> "llm_foundations.json")
    course_filename = course_id.replace("c_", "") + ".json"
    
    # Files are currently directly in the constants directory
    course_path = CONSTANTS_DIR / course_filename
    
    if not course_path.exists():
        # Try checking in a 'courses' subdirectory just in case the structure changes
        course_path_sub = CONSTANTS_DIR / "courses" / course_filename
        if course_path_sub.exists():
            course_path = course_path_sub
        else:
            raise FileNotFoundError(f"Course config for {course_id} not found at {course_path}")
    
    with open(course_path, "r") as f:
        return json.load(f)


def load_full_course_config(course_id: str) -> Dict[str, Any]:
    """
    Load complete course configuration (global + course-specific merged).
    
    Args:
        course_id: Course identifier
    
    Returns:
        Dictionary with 'global' and 'course' keys
    """
    return {
        "global": load_global_config(),
        "course": load_course_config(course_id)
    }


def get_lesson_config(course_id: str, lesson_id: str) -> Dict[str, Any]:
    """
    Get configuration for a specific lesson.
    
    Args:
        course_id: Course identifier
        lesson_id: Lesson identifier (e.g., "l01_what_llms_are")
    
    Returns:
        Lesson configuration
    
    Raises:
        ValueError: If lesson not found in course
    """
    course_config = load_course_config(course_id)
    
    # Find the lesson
    lesson = next(
        (lesson for lesson in course_config["lessons"] if lesson["lesson_id"] == lesson_id),
        None
    )
    
    if not lesson:
        raise ValueError(f"Lesson {lesson_id} not found in course {course_id}")
    
    return lesson


def get_difficulty_knobs(difficulty_level: int) -> Dict[str, Any]:
    """
    Get the delivery metrics for a specific difficulty level.
    
    Args:
        difficulty_level: 1 (Guided), 3 (Practical), or 5 (Direct)
    
    Returns:
        Difficulty configuration with delivery metrics
    """
    global_config = load_global_config()
    
    difficulty_str = str(difficulty_level)
    if difficulty_str not in global_config["global_difficulty_framework"]:
        raise ValueError(f"Invalid difficulty level: {difficulty_level}. Must be 1, 3, or 5.")
    
    return global_config["global_difficulty_framework"][difficulty_str]


def get_adaptation_rules(adaptation_type: str) -> Dict[str, Any]:
    """
    Get the rules for a specific adaptation type.
    
    Args:
        adaptation_type: "simplify_this", "get_to_the_point", "i_know_this_already", "more_examples"
    
    Returns:
        Adaptation rules
    """
    global_config = load_global_config()
    
    if adaptation_type not in global_config["global_adaptation_rules"]:
        raise ValueError(f"Invalid adaptation type: {adaptation_type}")
    
    return global_config["global_adaptation_rules"][adaptation_type]


def get_pedagogical_stage(course_id: str, lesson_id: str) -> Optional[Dict[str, Any]]:
    """
    Get the pedagogical stage for a lesson.
    
    Args:
        course_id: Course identifier
        lesson_id: Lesson identifier
    
    Returns:
        Pedagogical stage config, or None if not defined
    """
    course_config = load_course_config(course_id)
    
    if "pedagogical_progression" not in course_config:
        return None
    
    # Find which stage this lesson belongs to
    for stage_name, stage_config in course_config["pedagogical_progression"].items():
        if lesson_id in stage_config["lesson_range"]:
            return {
                "stage_name": stage_name,
                **stage_config
            }
    
    return None
