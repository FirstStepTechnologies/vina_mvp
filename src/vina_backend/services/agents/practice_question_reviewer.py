from typing import Dict, Any, List
import logging
from pathlib import Path
import json
from jinja2 import Template

from vina_backend.integrations.llm.client import get_llm_client

logger = logging.getLogger(__name__)

class PracticeQuestionReviewerAgent:
    """
    Reviews generated practice questions for quality and schema compliance.
    """
    
    def __init__(self):
        self.llm = get_llm_client()
        self.template = self._load_template()
        
    def _load_template(self) -> Template:
        prompt_path = Path(__file__).parent.parent.parent / "prompts" / "practice_question" / "reviewer.md"
        with open(prompt_path, "r") as f:
            return Template(f.read())
        
    def review(self, lesson_content: str, questions: List[Any], profession: str) -> List[Dict[str, Any]]:
        """
        Review the batch of questions.
        Returns a list of review objects (status, feedback).
        """
        logger.info(f"Reviewing {len(questions)} practice questions")
        
        # Serialize questions for prompt
        questions_json = json.dumps([q.dict() for q in questions], indent=2)
        
        prompt = self.template.render(
            lesson_content=lesson_content,
            questions=questions_json,
            profession=profession
        )
        
        try:
            data = self.llm.generate_json(prompt, temperature=0.3)
            return data.get("reviews", [])
        except Exception as e:
            logger.error(f"Error parsing review response: {e}")
            return []
