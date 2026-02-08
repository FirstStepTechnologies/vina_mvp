from typing import Dict, Any, List
import logging
from pathlib import Path
import json
from jinja2 import Template

from vina_backend.integrations.llm.client import get_llm_client
from vina_backend.domain.schemas.practice_quiz import PracticeQuestion, PracticeQuizOption

logger = logging.getLogger(__name__)

class PracticeQuestionGeneratorAgent:
    """
    Generates a batch of 10 practice questions for a lesson using the dedicated prompt.
    """
    
    def __init__(self):
        self.llm = get_llm_client()
        self.template = self._load_template()
        
    def _load_template(self) -> Template:
        prompt_path = Path(__file__).parent.parent.parent / "prompts" / "practice_question" / "generator.md"
        with open(prompt_path, "r") as f:
            return Template(f.read())
        
    def generate(self, lesson_content: str, profession: str, lesson_id: str) -> List[PracticeQuestion]:
        """
        Generate 10 practice questions for the given lesson and profession.
        """
        logger.info(f"Generating practice questions for lesson {lesson_id} ({profession})")
        
        # Prepare prompt
        prompt = self.template.render(
            lesson_content=lesson_content,
            profession=profession
        )
        
        # Call LLM
        try:
            # Using generate_json assuming the client supports it as seen in other agents
            data = self.llm.generate_json(prompt, temperature=0.7)
            
            questions_data = data.get("questions", [])
            
            # Convert to Pydantic models
            questions = []
            for idx, q_data in enumerate(questions_data):
                # Generate a stable ID
                safe_profession = profession.lower().replace(" ", "_")
                # Extract clean lesson number from ID like 'l01_...' -> 'l01'
                lesson_prefix = lesson_id.split("_")[0]
                q_id = f"pq_{lesson_prefix}_{safe_profession}_{idx+1:02d}"
                
                # Ensure options are properly structured
                options = [
                    PracticeQuizOption(**opt) if isinstance(opt, dict) else opt 
                    for opt in q_data.get("options", [])
                ]
                
                question = PracticeQuestion(
                    id=q_id,
                    lessonId=lesson_id,
                    text=q_data.get("text"),
                    options=options,
                    correctAnswer=q_data.get("correctAnswer"),
                    explanation=q_data.get("explanation"),
                    conceptTested=q_data.get("conceptTested", "General Understanding")
                )
                questions.append(question)
                
            logger.info(f"Successfully parsed {len(questions)} practice questions")
            return questions
            
        except Exception as e:
            logger.error(f"Error processing practice questions: {e}")
            raise
