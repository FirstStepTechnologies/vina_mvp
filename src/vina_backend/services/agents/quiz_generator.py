# src/vina_backend/services/agents/quiz_generator.py

import logging
from pathlib import Path
from typing import Dict, Any
from jinja2 import Template
from vina_backend.integrations.llm.client import get_llm_client
from vina_backend.integrations.opik_tracker import track_llm_call

logger = logging.getLogger(__name__)

PROMPTS_DIR = Path(__file__).parent.parent.parent / "prompts" / "quiz"

class QuizGeneratorAgent:
    """Agent responsible for generating initial quiz drafts."""
    
    def __init__(self):
        self.llm = get_llm_client()
        self.template = self._load_template("generator.md")
    
    def _load_template(self, filename: str) -> Template:
        path = PROMPTS_DIR / filename
        with open(path, "r") as f:
            return Template(f.read())
    
    @track_llm_call("generate_quiz_draft", "gemini-2.0-flash-exp")
    def generate(self, profession: str, course_name: str, curriculum_guidance: str, difficulty_mapping: str) -> Dict[str, Any]:
        """
        Generate initial quiz for a profession.
        
        Args:
            profession: Target profession (e.g., "Clinical Researcher")
            course_name: Name of the course
            curriculum_guidance: Formatted string detailing lessons/stages
            difficulty_mapping: Formatted string defining what each question (Q1-Q5) should test
            
        Returns:
            Raw JSON dict of quiz (not yet validated)
        """
        logger.info(f"🤖 Generator Agent: Creating quiz for {profession}")
        
        prompt = self.template.render(
            profession=profession,
            course_name=course_name,
            curriculum_guidance=curriculum_guidance,
            difficulty_mapping=difficulty_mapping
        )
        
        try:
            quiz_json = self.llm.generate_json(
                prompt,
                temperature=0.7,  # Creative but controlled
                max_tokens=3000
            )
            
            logger.info(f"   ✅ Generated {len(quiz_json.get('questions', []))} questions")
            return quiz_json
            
        except Exception as e:
            logger.error(f"   ❌ Generation failed: {e}")
            raise