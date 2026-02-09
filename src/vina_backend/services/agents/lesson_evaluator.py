
import logging
from pathlib import Path
from typing import Dict, Any, List
from jinja2 import Template
import json
from vina_backend.integrations.llm.client import get_llm_client
from vina_backend.integrations.opik_tracker import track_llm_call, OpikTracker

logger = logging.getLogger(__name__)

PROMPTS_DIR = Path(__file__).parent.parent.parent / "prompts" / "evaluation"

class LessonEvaluatorAgent:
    """Agent responsible for evaluating lesson quality (LLM-as-a-Judge)."""
    
    def __init__(self):
        self.llm = get_llm_client()
        self.template = self._load_template("lesson_judge.md")
        self.tracker = OpikTracker()
    
    def _load_template(self, filename: str) -> Template:
        path = PROMPTS_DIR / filename
        with open(path, "r") as f:
            return Template(f.read())
            
    @track_llm_call("evaluate_lesson_quality", "gemini-2.0-flash-exp")
    def evaluate(self, lesson_content: Dict[str, Any], user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a generated lesson against the user profile.
        
        Args:
            lesson_content: The full JSON content of the lesson
            user_profile: The user profile data (dict or object)
            
        Returns:
            Review constraints and scores
        """
        logger.info(f"⚖️ Evaluator Agent: Scoring lesson for quality...")
        
        # safely extract profile fields
        if hasattr(user_profile, 'profession'):
            prof = user_profile.profession
            ind = getattr(user_profile, 'industry', 'unknown')
            exp = getattr(user_profile, 'experience_level', 'unknown')
        else:
            prof = user_profile.get('profession', 'unknown')
            ind = user_profile.get('industry', 'unknown')
            exp = user_profile.get('experience_level', 'unknown')

        # Prepare snippet (first few slides or summary) to save tokens
        snippet = str(lesson_content)[:2000] # Safe truncation
        
        prompt = self.template.render(
            profession=prof,
            industry=ind,
            experience_level=exp,
            lesson_title=lesson_content.get('title', 'Untitled'),
            lesson_content_snippet=snippet
        )
        
        try:
            scores = self.llm.generate_json(
                prompt,
                temperature=0.1,  # Strict evaluation
                max_tokens=1000
            )
            
            logger.info(f"   ✅ Evaluation Complete. Scores: P={scores.get('personalization_score')}, C={scores.get('clarity_score')}")
            
            # Log separate metric/feedback event to Opik if possible
            # (Adding metadata to trace is handled by @track_llm_call automatically)
            
            return scores
            
        except Exception as e:
            logger.error(f"   ❌ Evaluation failed: {e}")
            return {
                "error": str(e),
                "personalization_score": 0,
                "clarity_score": 0,
                "engagement_score": 0
            }
