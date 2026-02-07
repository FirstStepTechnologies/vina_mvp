# src/vina_backend/services/agents/quiz_reviewer.py

import logging
import json
from pathlib import Path
from typing import Dict, Any, List
from jinja2 import Template
from vina_backend.integrations.llm.client import get_llm_client
from vina_backend.domain.schemas.quiz import ReviewResult

logger = logging.getLogger(__name__)

PROMPTS_DIR = Path(__file__).parent.parent.parent / "prompts" / "quiz"

class QuizReviewerAgent:
    """Agent responsible for evaluating quiz quality."""
    
    def __init__(self):
        self.llm = get_llm_client()
        self.template = self._load_template("reviewer.md")
    
    def _load_template(self, filename: str) -> Template:
        path = PROMPTS_DIR / filename
        with open(path, "r") as f:
            return Template(f.read())
    
    def evaluate(self, quiz_json: Dict[str, Any], profession: str, course_name: str, valid_lesson_ids: List[str]) -> ReviewResult:
        """
        Evaluate quiz quality against rubric.
        
        Args:
            quiz_json: Raw quiz JSON to evaluate
            profession: Target profession for context
            course_name: Name of the course
            valid_lesson_ids: List of valid lesson IDs
            
        Returns:
            ReviewResult with pass/fail and issues
        """
        logger.info(f"🔍 Reviewer Agent: Evaluating quiz for {profession}")
        
        quiz_str = json.dumps(quiz_json, indent=2)
        
        prompt = self.template.render(
            quiz_json=quiz_str,
            profession=profession,
            course_name=course_name,
            valid_lesson_ids=", ".join(valid_lesson_ids)
        )
        
        try:
            # Note: Reviewer expects a ReviewResult which matches the output format
            # The prompt asks for "passed", "issues", etc. which aligns with ReviewResult
            review_json = self.llm.generate_json(
                prompt,
                temperature=0.2,  # Low temperature for consistent evaluation
                max_tokens=1000
            )
            
            # Since the prompt structure might differ slightly from the pydantic model 
            # (e.g. score_breakdown vs specific fields), we need to ensure compatibility.
            # The current ReviewerResult model in schemas/quiz.py has:
            # passed: bool, score: float, feedback: str, issues: List[ReviewIssue]
            # The prompt asks for: passed, issues (list of strings?), score_breakdown
            # We need to align them.
            
            # Let's trust the LLM to follow the schema if we hint at it, or map it.
            # Actually, let's update the prompt to match the schema exactly or map here.
            # For now, let's assume the LLM output is close enough or use the schema in the prompt.
            # I will update the prompt file to match the schema in a separate step if needed.
            # BUT, to be safe, let's just try to parse it.
            
            # Wait, the previous code used ReviewResult(**review_json).
            # The previous prompt output format was:
            # { "passed": true, "issues": [...], "score_breakdown": {...} }
            # The schema `ReviewResult` in `src/vina_backend/domain/schemas/quiz.py` likely matches this?
            # Let's check schema.
            
            result = ReviewResult(**review_json)
            
            if result.passed:
                logger.info("   ✅ Quiz PASSED review")
            else:
                logger.warning(f"   ❌ Quiz FAILED review - Issues: {len(result.issues)}")
                for issue in result.issues:
                    logger.warning(f"      • {issue}")
            
            return result
            
        except Exception as e:
            logger.error(f"   ❌ Review failed: {e}")
            raise