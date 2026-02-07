# src/vina_backend/services/agents/quiz_rewriter.py

import logging
import json
from pathlib import Path
from typing import Dict, Any, List
from jinja2 import Template
from vina_backend.integrations.llm.client import get_llm_client

logger = logging.getLogger(__name__)

PROMPTS_DIR = Path(__file__).parent.parent.parent / "prompts" / "quiz"

class QuizRewriterAgent:
    """Agent responsible for fixing quiz issues."""
    
    def __init__(self):
        self.llm = get_llm_client()
        self.template = self._load_template("rewriter.md")
    
    def _load_template(self, filename: str) -> Template:
        path = PROMPTS_DIR / filename
        with open(path, "r") as f:
            return Template(f.read())
    
    def fix(self, quiz_json: Dict[str, Any], reviews: Any, profession: str) -> Dict[str, Any]:
        """
        Fix issues in a quiz that failed review.
        
        Args:
            quiz_json: Original quiz JSON
            reviews: ReviewResult object or dict containing issues
            profession: Target profession for context
            
        Returns:
            Revised quiz JSON
        """
        # Handle both ReviewResult object and potential list of strings (legacy)
        # The new prompt expects `review_json` which is the full review output
        if hasattr(reviews, 'model_dump_json'):
             review_json_str = reviews.model_dump_json(indent=2)
             issues_count = len(reviews.issues)
        elif isinstance(reviews, list):
             # Legacy support if passed a list of strings
             review_json_str = json.dumps({"issues": reviews}, indent=2)
             issues_count = len(reviews)
        else:
             review_json_str = json.dumps(reviews, indent=2)
             issues_count = len(reviews.get('issues', [])) if isinstance(reviews, dict) else 0

        logger.info(f"🔧 Rewriter Agent: Fixing {issues_count} issues for {profession}")
        
        quiz_str = json.dumps(quiz_json, indent=2)
        
        prompt = self.template.render(
            quiz_json=quiz_str,
            review_json=review_json_str,
            profession=profession
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