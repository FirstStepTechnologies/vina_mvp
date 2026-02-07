# scripts/generate_onboarding_quizzes_new.py

import json
import logging
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from vina_backend.services.agents.quiz_generator import QuizGeneratorAgent
from vina_backend.services.agents.quiz_reviewer import QuizReviewerAgent
from vina_backend.services.agents.quiz_rewriter import QuizRewriterAgent
from vina_backend.services.course_loader import load_course_config
from vina_backend.domain.schemas.quiz import ProfessionQuiz
from vina_backend.domain.constants.enums import Profession
from vina_backend.utils.logging import setup_logging

# Optional: Opik integration (if installed)
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
logger = logging.getLogger("QUIZ_PIPELINE")

COURSE_ID = "c_llm_foundations"
OUTPUT_FILE = Path(__file__).parent.parent / "src/vina_backend/domain/constants/onboarding_quizzes.json"

# Get professions from enums for consistency
TARGET_PROFESSIONS = [p.value for p in Profession]

def analyze_curriculum(config: Dict[str, Any]) -> Tuple[str, str, List[str]]:
    """
    Analyze course config to build dynamic curriculum guidance and difficulty mapping.
    
    Returns:
        (curriculum_guidance, difficulty_mapping, valid_lesson_ids)
    """
    course_name = config.get("course_name", "Course")
    lessons = config.get("lessons", [])
    progression = config.get("pedagogical_progression", {})
    
    valid_ids = [l["lesson_id"] for l in lessons]
    
    # Map stages to lesson ranges
    stage_info = []
    difficulty_map_lines = []
    
    # Helper to find lessons in a range
    def get_lessons_in_range(lesson_ids):
        return [l for l in lessons if l["lesson_id"] in lesson_ids]
    
    # STAGE 1 (Foundations) -> Q1, Q2
    s1 = progression.get("stage_1_foundations", {})
    if s1:
        l_range = s1.get("lesson_range", [])
        l_objs = get_lessons_in_range(l_range)
        concepts = ", ".join([l.get("what_learners_will_understand", ["Concepts"])[0] for l in l_objs])
        
        stage_info.append(f"**Stage 1: {s1.get('focus', 'Foundations')}**")
        for l in l_objs:
             stage_info.append(f"- {l['lesson_id']}: {l['lesson_name']}")
             
        difficulty_map_lines.append(f"- Q1 (Difficulty 1): Test basic concepts from Stage 1 ({concepts})")
        difficulty_map_lines.append(f"- Q2 (Difficulty 2): Test slightly deeper understanding of Stage 1 concepts")
        
    # STAGE 2 (Application) -> Q3, Q4
    s2 = progression.get("stage_2_application", {})
    if s2:
        l_range = s2.get("lesson_range", [])
        l_objs = get_lessons_in_range(l_range)
        concepts = ", ".join([l.get("what_learners_will_understand", ["Concepts"])[0] for l in l_objs[:3]]) # First few concepts
        
        stage_info.append(f"\n**Stage 2: {s2.get('focus', 'Application')}**")
        for l in l_objs:
             stage_info.append(f"- {l['lesson_id']}: {l['lesson_name']}")
             
        difficulty_map_lines.append(f"- Q3 (Difficulty 3): Test application/risk concepts from Stage 2")
        difficulty_map_lines.append(f"- Q4 (Difficulty 4): **PROFESSION-SPECIFIC** - Test Stage 2 concepts in a job scenario")

    # STAGE 3 (Mastery) -> Q5
    s3 = progression.get("stage_3_mastery", {})
    if s3:
        l_range = s3.get("lesson_range", [])
        l_objs = get_lessons_in_range(l_range)
        
        stage_info.append(f"\n**Stage 3: {s3.get('focus', 'Mastery')}**")
        for l in l_objs:
             stage_info.append(f"- {l['lesson_id']}: {l['lesson_name']}")
             
        difficulty_map_lines.append(f"- Q5 (Difficulty 5): **PROFESSION-SPECIFIC** - Test advanced Stage 3 concepts")

    return "\n".join(stage_info), "\n   ".join(difficulty_map_lines), valid_ids


@track(name="generate_quiz_for_profession")
def generate_quiz_for_profession(
    profession: str,
    course_name: str,
    curriculum_guidance: str,
    difficulty_mapping: str,
    valid_lesson_ids: List[str],
    generator: QuizGeneratorAgent,
    reviewer: QuizReviewerAgent,
    rewriter: QuizRewriterAgent,
    max_rewrites: int = 2
) -> ProfessionQuiz:
    """Multi-agent pipeline to generate high-quality quiz."""
    logger.info(f"\n{'='*60}")
    logger.info(f"🎯 Starting Quiz Generation Pipeline: {profession}")
    logger.info(f"{'='*60}")
    
    # STAGE 1: Generator
    draft_quiz = generator.generate(
        profession=profession,
        course_name=course_name,
        curriculum_guidance=curriculum_guidance, 
        difficulty_mapping=difficulty_mapping
    )
    
    # STAGE 2: Review Loop
    for attempt in range(max_rewrites + 1):
        logger.info(f"\n📋 Review Cycle {attempt + 1}/{max_rewrites + 1}")
        
        review = reviewer.evaluate(
            quiz_json=draft_quiz, 
            profession=profession,
            course_name=course_name,
            valid_lesson_ids=valid_lesson_ids
        )
        
        if review.passed:
            logger.info("✅ Quiz passed all quality checks!")
            break
        
        if attempt < max_rewrites:
            # STAGE 3: Rewrite
            logger.info(f"🔄 Triggering rewrite (attempt {attempt + 1}/{max_rewrites})")
            draft_quiz = rewriter.fix(draft_quiz, review.issues, profession)
        else:
            # Max attempts reached
            logger.warning(f"⚠️  Quiz did not pass after {max_rewrites} rewrites")
            logger.warning("   Proceeding with best attempt, but flagging for manual review")
    
    # STAGE 4: Final Validation
    try:
        validated_quiz = ProfessionQuiz(**draft_quiz)
        logger.info("✅ Pydantic validation passed")
        return validated_quiz
    except Exception as e:
        logger.error(f"❌ Final validation failed: {e}")
        logger.error(f"   Quiz JSON: {json.dumps(draft_quiz, indent=2)}")
        raise


@track(name="generate_all_quizzes")
def main():
    """Main execution: Generate quizzes for all professions."""
    logger.info("🎓 Vina Quiz Generator - Generic Multi-Agent Pipeline")
    logger.info(f"📦 Opik Integration: {'✅ Enabled' if OPIK_AVAILABLE else '❌ Disabled'}")
    
    # 1. Load Course Structure
    try:
        config = load_course_config(COURSE_ID)
        course_name = config.get("course_name", "Unknown Course")
        
        # Dynamic Analysis
        curriculum_guidance, difficulty_mapping, valid_lesson_ids = analyze_curriculum(config)
        
        logger.info(f"✅ Loaded context for '{course_name}'")
        logger.info(f"   Lessons: {len(valid_lesson_ids)}")
        logger.info(f"   Curriculum Size: {len(curriculum_guidance)} chars")
        
    except Exception as e:
        logger.error(f"❌ Failed to load course config: {e}")
        return
    
    # 2. Initialize Agents
    generator = QuizGeneratorAgent()
    reviewer = QuizReviewerAgent()
    rewriter = QuizRewriterAgent()
    
    # 3. Generate for Each Profession
    final_output = {}
    
    for profession in TARGET_PROFESSIONS:
        try:
            quiz = generate_quiz_for_profession(
                profession=profession,
                course_name=course_name,
                curriculum_guidance=curriculum_guidance,
                difficulty_mapping=difficulty_mapping,
                valid_lesson_ids=valid_lesson_ids,
                generator=generator,
                reviewer=reviewer,
                rewriter=rewriter
            )
            
            final_output[profession] = quiz.dict()
            logger.info(f"✅ SUCCESS: {profession} quiz complete\n")
            
        except Exception as e:
            logger.error(f"❌ FAILED: {profession} - {e}\n")
            continue
    
    # 4. Save Output
    if not final_output:
        logger.error("❌ No quizzes generated successfully. Aborting save.")
        return
    
    try:
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        with open(OUTPUT_FILE, "w") as f:
            json.dump(final_output, f, indent=2)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"🎉 Generation Complete!")
        logger.info(f"📁 Output: {OUTPUT_FILE}")
        logger.info(f"✅ Successfully generated {len(final_output)}/{len(TARGET_PROFESSIONS)} quizzes")
        logger.info(f"{'='*60}")
        
    except Exception as e:
        logger.error(f"❌ Failed to save output: {e}")


if __name__ == "__main__":
    main()