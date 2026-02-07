
import json
import logging
import sys
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from vina_backend.services.agents.lesson_quiz_generator import LessonQuizGeneratorAgent
from vina_backend.services.agents.lesson_quiz_reviewer import LessonQuizReviewerAgent
from vina_backend.services.agents.lesson_quiz_rewriter import LessonQuizRewriterAgent
from vina_backend.services.course_loader import load_course_config
from vina_backend.services.profile_builder import get_or_create_user_profile
from vina_backend.domain.schemas.lesson_quiz import LessonQuiz
from vina_backend.domain.constants.enums import Profession, INDUSTRIES_BY_PROFESSION, ExperienceLevel
from vina_backend.utils.logging import setup_logging

# Optional: Opik integration
try:
    from opik import track
    OPIK_AVAILABLE = True
except ImportError:
    OPIK_AVAILABLE = False
    def track(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

setup_logging("INFO")
logger = logging.getLogger("LESSON_QUIZ_PIPELINE")

COURSE_ID = "c_llm_foundations"
OUTPUT_FILE = Path(__file__).parent.parent / "src/vina_backend/domain/constants/lesson_quizzes.json"

# Get professions from enums
TARGET_PROFESSIONS = [p.value for p in Profession]

@track(name="generate_quiz_for_lesson")
def generate_quiz_for_lesson(
    lesson_id: str,
    profession: str,
    lesson_data: dict,
    user_profile: dict,
    generator: LessonQuizGeneratorAgent,
    reviewer: LessonQuizReviewerAgent,
    rewriter: LessonQuizRewriterAgent,
    max_rewrites: int = 2
) -> LessonQuiz:
    """
    Multi-agent pipeline to generate high-quality lesson quiz.
    
    Flow: Generator → Reviewer → [Rewriter if needed] → Validation
    """
    logger.info(f"\n{'='*70}")
    logger.info(f"🎯 Pipeline: {lesson_id} × {profession}")
    logger.info(f"{'='*70}")
    
    # Extract lesson objectives
    lesson_objectives = lesson_data.get('what_learners_will_understand', [])
    
    # STAGE 1: Generator
    draft_quiz = generator.generate(
        lesson_id=lesson_id,
        profession=profession,
        lesson_objectives=lesson_objectives,
        user_profile=user_profile
    )
    
    # STAGE 2: Review Loop
    for attempt in range(max_rewrites + 1):
        logger.info(f"\n📋 Review Cycle {attempt + 1}/{max_rewrites + 1}")
        
        review = reviewer.evaluate(
            quiz_json=draft_quiz,
            lesson_id=lesson_id,
            profession=profession,
            lesson_objectives=lesson_objectives
        )
        
        if review.passed:
            logger.info("✅ Quiz passed all quality checks!")
            break
        
        if attempt < max_rewrites:
            # STAGE 3: Rewrite
            logger.info(f"🔄 Triggering rewrite (attempt {attempt + 1}/{max_rewrites})")
            draft_quiz = rewriter.fix(
                quiz_json=draft_quiz,
                issues=review.issues,
                lesson_id=lesson_id,
                profession=profession,
                lesson_objectives=lesson_objectives
            )
        else:
            # Max attempts reached
            logger.warning(f"⚠️  Quiz did not pass after {max_rewrites} rewrites")
            logger.warning("   Using best attempt (manual review recommended)")
    
    # STAGE 4: Final Validation
    try:
        validated_quiz = LessonQuiz(**draft_quiz)
        logger.info("✅ Pydantic validation passed")
        return validated_quiz
    except Exception as e:
        logger.error(f"❌ Final validation failed: {e}")
        logger.error(f"   Quiz JSON: {json.dumps(draft_quiz, indent=2)}")
        raise

@track(name="generate_all_lesson_quizzes")
def main():
    parser = argparse.ArgumentParser(description="Generate lesson quizzes")
    parser.add_argument("--start", type=int, required=True, help="Start lesson number (inclusive)")
    parser.add_argument("--end", type=int, required=True, help="End lesson number (inclusive)")
    parser.add_argument("--profession", type=str, help="Specific profession (optional)")
    args = parser.parse_args()

    # Filter professions
    professions_to_process = [args.profession] if args.profession else TARGET_PROFESSIONS
    
    logger.info("🎓 Vina Lesson Quiz Generator")
    logger.info(f"🎯 Range: Lessons {args.start}-{args.end}")
    logger.info(f"👥 Professions: {professions_to_process}")
    
    # 1. Load Course Structure
    try:
        config = load_course_config(COURSE_ID)
        all_lessons = config["lessons"]
        logger.info(f"✅ Loaded {len(all_lessons)} lessons from config")
    except Exception as e:
        logger.error(f"❌ Failed to load course config: {e}")
        return
    
    # 2. Filter Lessons
    target_lessons = []

    def get_lesson_number(lesson_id: str) -> int:
        """Extract numeric ID from lesson string (e.g., 'l05_hallucinations' -> 5)."""
        try:
            # Assumes format "lXX_name"
            # Remove 'l' and take first 2 chars
            num_str = lesson_id.split('_')[0][1:]
            return int(num_str)
        except (ValueError, IndexError):
            return -1

    for l in all_lessons:
        l_num = get_lesson_number(l["lesson_id"])
        if args.start <= l_num <= args.end:
            target_lessons.append(l)
            
    if not target_lessons:
        logger.error(f"❌ No lessons found in range {args.start}-{args.end}")
        return
        
    logger.info(f"📝 Processing {len(target_lessons)} lessons: {[l['lesson_id'] for l in target_lessons]}\n")

    # 3. Load User Profiles for target professions
    user_profiles = {}
    for profession in professions_to_process:
        try:
            # Determine default industry based on profession
            industry = INDUSTRIES_BY_PROFESSION.get(profession, ["Technology"])[0]
            
            profile = get_or_create_user_profile(
                profession=profession,
                industry=industry,
                experience_level=ExperienceLevel.INTERMEDIATE.value
            )
            user_profiles[profession] = profile
        except Exception as e:
            logger.error(f"❌ Failed to load profile for {profession}: {e}")
            return
            
    # 4. Initialize Agents
    generator = LessonQuizGeneratorAgent()
    reviewer = LessonQuizReviewerAgent()
    rewriter = LessonQuizRewriterAgent()
    
    # 5. Load Existing Data (Merge Strategy)
    final_output = {}
    if OUTPUT_FILE.exists():
        try:
            with open(OUTPUT_FILE, "r") as f:
                logger.info(f"📂 Loading existing quizzes from {OUTPUT_FILE}")
                final_output = json.load(f)
        except json.JSONDecodeError:
            logger.warning(f"⚠️  Could not parse existing quiz file. Starting fresh.")
    
    # 6. Generate Quizzes
    success_count = 0
    total_expected = len(target_lessons) * len(professions_to_process)
    
    for lesson in target_lessons:
        lesson_id = lesson["lesson_id"]
        
        # Ensure lesson entry exists
        if lesson_id not in final_output:
            final_output[lesson_id] = {}
            
        for profession in professions_to_process:
            try:
                quiz = generate_quiz_for_lesson(
                    lesson_id=lesson_id,
                    profession=profession,
                    lesson_data=lesson,
                    user_profile=user_profiles[profession].model_dump(),
                    generator=generator,
                    reviewer=reviewer,
                    rewriter=rewriter
                )
                
                # Update/Overwrite specific entry
                # Convert Pydantic model to dict
                final_output[lesson_id][profession] = quiz.dict()  # Use model_dump() for Pydantic v2
                success_count += 1
                logger.info(f"✅ SUCCESS: {lesson_id} × {profession}\n")
                
            except Exception as e:
                logger.error(f"❌ FAILED: {lesson_id} × {profession} - {e}\n")
                continue

    # 7. Save merged output
    if success_count > 0:
        try:
            OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(OUTPUT_FILE, "w") as f:
                json.dump(final_output, f, indent=2)
                
            logger.info(f"\n{'='*70}")
            logger.info(f"🎉 Batch Complete: {success_count}/{total_expected} successful")
            logger.info(f"📁 Output updated: {OUTPUT_FILE}")
            logger.info(f"{'='*70}\n")
            
        except Exception as e:
            logger.error(f"❌ Failed to save output: {e}")
    else:
        logger.warning("\n⚠️  No new quizzes were generated successfully. File not updated.")

if __name__ == "__main__":
    main()
