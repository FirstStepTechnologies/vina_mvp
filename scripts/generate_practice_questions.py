"""
Generate daily practice questions for all lessons and professions.
Orchestrates the Generator -> Reviewer -> Rewriter pipeline.

Usage:
  uv run scripts/generate_practice_questions.py --start 1 --end 3
  uv run scripts/generate_practice_questions.py --profession "HR Manager"
"""

import json
import logging
import sys
import argparse
from pathlib import Path
from typing import List, Dict

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from vina_backend.services.agents.practice_question_generator import PracticeQuestionGeneratorAgent
from vina_backend.services.agents.practice_question_reviewer import PracticeQuestionReviewerAgent
from vina_backend.services.agents.practice_question_rewriter import PracticeQuestionRewriterAgent
from vina_backend.services.course_loader import load_course_config
from vina_backend.domain.schemas.practice_quiz import PracticeQuestion

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

OUTPUT_FILE = Path(__file__).parent.parent / "src" / "vina_backend" / "domain" / "constants" / "practice_questions.json"

def save_questions(new_questions: List[PracticeQuestion]):
    """Merge and save questions to JSON file."""
    
    # Load existing
    if OUTPUT_FILE.exists():
        try:
            with open(OUTPUT_FILE, "r") as f:
                data = json.load(f)
                existing_questions = data.get("questions", [])
        except json.JSONDecodeError:
            existing_questions = []
    else:
        existing_questions = []
    
    # Create a map for easy value update/deduplication by ID
    question_map = {q["id"]: q for q in existing_questions}
    
    # Update with new questions
    for q in new_questions:
        question_map[q.id] = q.model_dump()
        
    # Write back
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        json.dump({"questions": list(question_map.values())}, f, indent=2)
    
    logger.info(f"Saved {len(new_questions)} questions to {OUTPUT_FILE}")

def main():
    parser = argparse.ArgumentParser(description="Generate practice questions for lessons.")
    parser.add_argument("--start", type=int, default=1, help="Start lesson number")
    parser.add_argument("--end", type=int, default=100, help="End lesson number")
    parser.add_argument("--profession", type=str, help="Specific profession to target")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing questions if found")
    
    args = parser.parse_args()
    
    # Initialize agents
    generator = PracticeQuestionGeneratorAgent()
    reviewer = PracticeQuestionReviewerAgent()
    rewriter = PracticeQuestionRewriterAgent()
    
    course_id = "c_llm_foundations"
    try:
        course_config = load_course_config(course_id)
    except TypeError:
        # Fallback if load_course_config signature changes often 
        # (but we saw it requires course_id)
        logger.error("Failed to load course config. Check course_id.")
        return

    # Filter lessons
    lessons_to_process = []
    # config is a dict, so access "lessons" key
    all_lessons = course_config.get("lessons", [])
    
    for lesson in all_lessons:
        try:
            # Lesson is a dict, access ["lesson_id"]
            l_id = lesson.get("lesson_id", "")
            # Assume ID format "l01_..."
            # split l01 -> 01 -> int
            if not l_id.startswith("l"):
                continue
                
            lesson_num = int(l_id.split("_")[0][1:])
            
            if args.start <= lesson_num <= args.end:
                lessons_to_process.append(lesson)
        except (ValueError, IndexError):
            continue
            
    if not lessons_to_process:
        logger.warning(f"No lessons found in range {args.start}-{args.end}.")
        return

    # Determine professions
    # We can use the global Enum if available, or just hardcode for hackathon
    professions = [args.profession] if args.profession else ["HR Manager", "Product Manager", "Software Engineer", "Sales Representative"]
    
    total_generated = 0
    
    for lesson in lessons_to_process:
        lesson_id = lesson.get("lesson_id")
        lesson_title = lesson.get("title")
        logger.info(f"Processing Lesson: {lesson_title} ({lesson_id})")
        
        # Load lesson content (simulation)
        # Try to load from constants/content or construct from metadata
        # We don't have a reliable content loader in this script yet, so we construct from metadata
        # similar to lesson_quiz_generator.
        
        # Construct content string from metadata
        lesson_desc = lesson.get("description", "")
        outcomes = ", ".join(lesson.get("learning_outcomes", []))
        topic = lesson.get("topic", "")
        
        lesson_content = f"""
        Title: {lesson_title}
        Topic: {topic}
        Description: {lesson_desc}
        Learning Outcomes: {outcomes}
        """
        
        # If we had access to the full content generated by LessonGenerator, we would read it here.
        # check if there is a 'content' key or similar? No, usually generated on fly.
        # But for QUIZ generation, the summary + outcomes is usually enough context for the LLM 
        # to Hallucinate/Generate relevant scenarios if the prompt is good.
            
        for prof in professions:
            logger.info(f"  Target: {prof}")
            
            # Check if exists (unless overwrite)
            if not args.overwrite and OUTPUT_FILE.exists():
                try:
                    with open(OUTPUT_FILE, "r") as f:
                         data = json.load(f)
                         # Check if ANY questions exist for this lesson+profession
                         # ID format: pq_{lesson_prefix}_{safe_profession}_...
                         safe_prof = prof.lower().replace(" ", "_")
                         lesson_prefix = lesson_id.split("_")[0]
                         prefix = f"pq_{lesson_prefix}_{safe_prof}"
                         
                         existing_count = sum(1 for q in data.get("questions", []) if q["id"].startswith(prefix))
                         if existing_count >= 10:
                             logger.info(f"    Skipping (Found {existing_count} questions). Use --overwrite to force.")
                             continue
                except Exception:
                    pass # file error, proceed to generate

            try:
                # 1. Generate
                questions = generator.generate(lesson_content, prof, lesson_id)
                
                # 2. Review
                feedback = reviewer.review(lesson_content, questions, prof)
                
                # 3. Rewrite (if needed)
                if feedback:
                    logger.info(f"    Reviewer provided {len(feedback)} feedback items. Rewriting...")
                    questions = rewriter.rewrite(questions, feedback, prof)
                
                # Save immediately
                save_questions(questions)
                total_generated += len(questions)
                
            except Exception as e:
                logger.error(f"Failed to generate for {lesson_id} / {prof}: {e}")
                continue

    logger.info(f"Done! Generated {total_generated} new practice questions.")

if __name__ == "__main__":
    main()
