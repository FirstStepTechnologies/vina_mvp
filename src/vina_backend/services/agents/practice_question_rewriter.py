from typing import Dict, Any, List
import logging
from pathlib import Path
import json
from jinja2 import Template

from vina_backend.integrations.llm.client import get_llm_client
from vina_backend.domain.schemas.practice_quiz import PracticeQuestion, PracticeQuizOption

logger = logging.getLogger(__name__)

class PracticeQuestionRewriterAgent:
    """
    Rewrites practice questions based on reviewer feedback.
    """
    
    def __init__(self):
        self.llm = get_llm_client()
        self.template = self._load_template()
        
    def _load_template(self) -> Template:
        prompt_path = Path(__file__).parent.parent.parent / "prompts" / "practice_question" / "rewriter.md"
        with open(prompt_path, "r") as f:
            return Template(f.read())
        
    def rewrite(self, original_questions: List[PracticeQuestion], feedback: List[Dict], profession: str) -> List[PracticeQuestion]:
        """
        Apply feedback to improve questions.
        """
        logger.info("Rewriting practice questions based on feedback")
        
        # Only send if there's actionable feedback
        needs_rewrite = any(item.get("status") != "approved" for item in feedback)
        if not needs_rewrite:
            logger.info("No rewrite needed, returning originals")
            return original_questions
            
        questions_json = json.dumps([q.dict() for q in original_questions], indent=2)
        feedback_json = json.dumps(feedback, indent=2)
        
        prompt = self.template.render(
            original_questions=questions_json,
            feedback=feedback_json,
            profession=profession
        )
        
        try:
            data = self.llm.generate_json(prompt, temperature=0.5)
            rewritten_data = data.get("questions", [])
            
            final_questions = []
            for idx, q_data in enumerate(rewritten_data):
                # Preserve original ID if possible, else generate new (careful with matching)
                # Ideally, the rewriter keeps the ID. If not, we regenerate logic.
                
                # Check if we can find the matching original ID by index
                original_id = original_questions[idx].id if idx < len(original_questions) else f"pq_rewritten_{idx}"
                
                # Extract clean lesson number from ID like 'l01_...' -> 'l01'
                lesson_id = original_questions[idx].lessonId if idx < len(original_questions) else "unknown"
                
                options = [
                    PracticeQuizOption(**opt) if isinstance(opt, dict) else opt 
                    for opt in q_data.get("options", [])
                ]
                
                question = PracticeQuestion(
                    id=q_data.get("id", original_id), # Prefer returned ID if present
                    lessonId=q_data.get("lessonId", lesson_id),
                    text=q_data.get("text"),
                    options=options,
                    correctAnswer=q_data.get("correctAnswer"),
                    explanation=q_data.get("explanation"),
                    conceptTested=q_data.get("conceptTested", "General")
                )
                final_questions.append(question)
                
            return final_questions
            
        except Exception as e:
            logger.error(f"Error parsing rewrite response: {e}")
            logger.warning("Returning original questions due to rewrite failure")
            return original_questions
