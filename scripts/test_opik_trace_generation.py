"""
Script to generate Opik traces for Vina LLM operations.
This runs the lesson generation and quiz generation logic to populate the Opik dashboard.
"""
import sys
import asyncio
import logging
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from vina_backend.services.profile_builder import get_or_create_user_profile
from vina_backend.services.lesson_generator import LessonGenerator
from vina_backend.services.agents.quiz_generator import QuizGeneratorAgent
from vina_backend.services.agents.lesson_evaluator import LessonEvaluatorAgent
from vina_backend.domain.schemas.profile import UserProfileData
from vina_backend.utils.logging import setup_logging
from vina_backend.integrations.db.engine import init_db

# Setup logging
setup_logging("INFO")
logger = logging.getLogger("OPIK_TRACE_GEN")

async def generate_traces():
    logger.info("🚀 Starting Opik Trace Generation (Test Mode)")
    
    # Ensure DB is initialized
    init_db()
    
    # 1. Single profession for testing
    profiles_to_test = [
        ("HR Manager", "Tech Company", "Beginner"),
    ]
    
    # 1. Single lesson for testing
    lessons_to_generate = [
        "l01_what_llms_are"
    ]
    
    lesson_gen = LessonGenerator()
    quiz_gen = QuizGeneratorAgent()
    evaluator = LessonEvaluatorAgent()
    
    for profession, industry, level in profiles_to_test:
        logger.info(f"\n--- Generating traces for {profession} ({len(lessons_to_generate)} lessons) ---")
        
        # Create/Get Profile
        user = get_or_create_user_profile(profession, industry, level)
        # Convert to Pydantic model needed by generator
        # Note: DB stores lists as JSON strings, but UserProfileData expects lists
        import json
        
        user_profile_data = UserProfileData(
            profession=user.profession,
            industry=user.industry,
            experience_level=user.experience_level,
            daily_goal_minutes=user.daily_goal_minutes,
            onboarding_responses=user.onboarding_responses,
            generated_at=datetime.utcnow(),
            professional_goals=json.loads(user.professional_goals) if isinstance(user.professional_goals, str) else user.professional_goals,
            safety_priorities=json.loads(user.safety_priorities) if isinstance(user.safety_priorities, str) else user.safety_priorities,
            high_stakes_areas=json.loads(user.high_stakes_areas) if isinstance(user.high_stakes_areas, str) else user.high_stakes_areas
        )
        
        for lesson_id in lessons_to_generate:
            # 2. Generate Lesson (Tracks 'generate_lesson')
            logger.info(f"📝 Generating Lesson {lesson_id} for {profession}...")
            lesson_content = {}
            try:
                lesson = lesson_gen.generate_lesson(
                    lesson_id=lesson_id,
                    course_id="c_llm_foundations",
                    user_profile=user_profile_data,
                    difficulty_level=3,
                    bypass_cache=True  # Force LLM call to ensure trace is generated
                )
                logger.info(f"✅ Lesson {lesson_id} generated successfully")
                
                # Check if lesson is GeneratedLesson object or dict
                if hasattr(lesson, 'lesson_content'):
                    lesson_content = lesson.lesson_content.model_dump()
                elif isinstance(lesson, dict):
                    lesson_content = lesson
                
                # 3. Evaluate Lesson (Tracks 'evaluate_lesson_quality')
                logger.info(f"⚖️ Evaluating Lesson Quality...")
                scores = evaluator.evaluate(lesson_content, user_profile_data)
                logger.info(f"✅ Evaluation Scores: {scores}")

            except Exception as e:
                logger.error(f"❌ Lesson {lesson_id} generation/evaluation failed: {e}")
            
        # 3. Generate Quiz (Tracks 'generate_quiz_draft')
        logger.info(f"❓ Generating Quiz for {profession}...")
        try:
            # Context for quiz generation
            course_name = "LLM Foundations"
            curriculum = "Lesson 1: What are LLMs?"
            diff_mapping = "Q1: Basic, Q2: Apply, Q3: Analyze"
            
            quiz = quiz_gen.generate(
                profession=profession,
                course_name=course_name,
                curriculum_guidance=curriculum,
                difficulty_mapping=diff_mapping
            )
            logger.info("✅ Quiz generated successfully")
        except Exception as e:
            logger.error(f"❌ Quiz generation failed: {e}")
            
    logger.info("\n🎉 Trace generation complete! Check your Opik dashboard.")

if __name__ == "__main__":
    asyncio.run(generate_traces())
