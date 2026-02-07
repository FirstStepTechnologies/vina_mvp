
import logging
import json
from typing import Dict, Any, List
from pathlib import Path
from jinja2 import Template

from vina_backend.integrations.llm.client import get_llm_client

logger = logging.getLogger(__name__)

class LessonQuizRewriterAgent:
    """Agent responsible for fixing lesson quiz issues."""
    
    def __init__(self):
        self.llm = get_llm_client()
        self.template = self._load_template()

    def _load_template(self) -> Template:
        """Load prompt template from markdown file."""
        prompt_path = Path(__file__).parent.parent.parent / "prompts/lesson_quiz/rewriter.md"
        try:
            with open(prompt_path, "r") as f:
                return Template(f.read())
        except Exception as e:
            logger.error(f"Failed to load rewriter prompt: {e}")
            raise
    
    def fix(
        self, 
        quiz_json: Dict[str, Any],
        issues: List[str],
        lesson_id: str,
        profession: str,
        lesson_objectives: list
    ) -> Dict[str, Any]:
        """
        Fix issues in a quiz that failed review.
        
        Args:
            quiz_json: Original quiz JSON
            issues: List of specific problems to fix
            lesson_id: Lesson ID for context
            profession: Target profession
            lesson_objectives: Learning objectives for alignment
            
        Returns:
            Revised quiz JSON
        """
        logger.info(f"🔧 Rewriter: Fixing {len(issues)} issues")
        
        quiz_str = json.dumps(quiz_json, indent=2)
        issues_str = "\n".join(f"- {issue}" for issue in issues)
        objectives_str = "\n".join(f"- {obj}" for obj in lesson_objectives)
        
        prompt = self.template.render(
            quiz_json=quiz_str,
            issues=issues_str,
            lesson_id=lesson_id,
            profession=profession,
            lesson_objectives=objectives_str
        )
        
        try:
            fixed_quiz = self.llm.generate_json(
                prompt,
                temperature=0.5,  # Moderate creativity for fixes
                max_tokens=3000
            )
            
            logger.info("   ✅ Quiz rewritten")
            return fixed_quiz
            
        except Exception as e:
            logger.error(f"   ❌ Rewrite failed: {e}")
            raise
