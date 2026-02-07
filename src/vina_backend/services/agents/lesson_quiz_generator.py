
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from jinja2 import Template

from vina_backend.integrations.llm.client import get_llm_client

logger = logging.getLogger(__name__)

class LessonQuizGeneratorAgent:
    """Agent responsible for generating initial lesson quiz drafts."""
    
    def __init__(self):
        self.llm = get_llm_client()
        self.template = self._load_template()
    
    def _load_template(self) -> Template:
        """Load prompt template from markdown file."""
        prompt_path = Path(__file__).parent.parent.parent / "prompts/lesson_quiz/generator.md"
        try:
            with open(prompt_path, "r") as f:
                return Template(f.read())
        except Exception as e:
            logger.error(f"Failed to load generator prompt: {e}")
            raise

    def generate(
        self, 
        lesson_id: str, 
        profession: str,
        lesson_objectives: list,
        user_profile: dict
    ) -> Dict[str, Any]:
        """
        Generate initial quiz for a lesson.
        
        Args:
            lesson_id: Lesson ID (e.g., "l05_hallucinations")
            profession: Target profession
            lesson_objectives: Learning objectives from course config
            user_profile: User profile data for contextualization
            
        Returns:
            Raw JSON dict of quiz (not yet validated)
        """
        logger.info(f"🤖 Generator: Creating quiz for {lesson_id} ({profession})")
        
        # Build context
        objectives_str = "\n".join(f"- {obj}" for obj in lesson_objectives)
        profile_str = self._format_profile(user_profile)
        
        prompt = self.template.render(
            lesson_id=lesson_id,
            profession=profession,
            lesson_objectives=objectives_str,
            user_profile_summary=profile_str
        )
        
        try:
            quiz_json = self.llm.generate_json(
                prompt,
                temperature=0.7,  # Creative scenarios
                max_tokens=3000
            )
            
            logger.info(f"   ✅ Generated {len(quiz_json.get('questions', []))} questions")
            return quiz_json
            
        except Exception as e:
            logger.error(f"   ❌ Generation failed: {e}")
            raise
    
    def _format_profile(self, profile: dict) -> str:
        """Format user profile for prompt."""
        return f"""
Daily Responsibilities:
{', '.join(profile.get('daily_responsibilities', [])[:3])}

Typical Outputs:
{', '.join(profile.get('typical_outputs', [])[:3])}

Pain Points:
{', '.join(profile.get('pain_points', [])[:2])}
        """.strip()
