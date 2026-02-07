
import logging
import json
from typing import Dict, Any
from pathlib import Path
from jinja2 import Template

from vina_backend.integrations.llm.client import get_llm_client
from vina_backend.domain.schemas.lesson_quiz import ReviewResult

logger = logging.getLogger(__name__)

class LessonQuizReviewerAgent:
    """Agent responsible for evaluating lesson quiz quality."""
    
    def __init__(self):
        self.llm = get_llm_client()
        self.template = self._load_template()

    def _load_template(self) -> Template:
        """Load prompt template from markdown file."""
        prompt_path = Path(__file__).parent.parent.parent / "prompts/lesson_quiz/reviewer.md"
        try:
            with open(prompt_path, "r") as f:
                return Template(f.read())
        except Exception as e:
            logger.error(f"Failed to load reviewer prompt: {e}")
            raise
    
    def evaluate(
        self, 
        quiz_json: Dict[str, Any],
        lesson_id: str,
        profession: str,
        lesson_objectives: list
    ) -> ReviewResult:
        """
        Evaluate quiz quality against rubric.
        
        Args:
            quiz_json: Raw quiz JSON to evaluate
            lesson_id: Lesson ID for context
            profession: Target profession
            lesson_objectives: Learning objectives for alignment check
            
        Returns:
            ReviewResult with pass/fail and issues
        """
        logger.info(f"🔍 Reviewer: Evaluating {lesson_id} ({profession})")
        
        quiz_str = json.dumps(quiz_json, indent=2)
        objectives_str = "\n".join(f"- {obj}" for obj in lesson_objectives)
        
        prompt = self.template.render(
            quiz_json=quiz_str,
            lesson_id=lesson_id,
            profession=profession,
            lesson_objectives=objectives_str
        )
        
        try:
            review_json = self.llm.generate_json(
                prompt,
                temperature=0.2,  # Low temp for consistent evaluation
                max_tokens=1000
            )
            
            result = ReviewResult(**review_json)
            
            if result.passed:
                logger.info("   ✅ Quiz PASSED review")
            else:
                logger.warning(f"   ❌ Quiz FAILED - Issues: {len(result.issues)}")
                for issue in result.issues:
                    logger.warning(f"      • {issue}")
            
            return result
            
        except Exception as e:
            logger.error(f"   ❌ Review failed: {e}")
            raise
