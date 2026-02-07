
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from vina_backend.domain.schemas.quiz import ProfessionQuiz, QuizQuestion
from vina_backend.domain.constants.enums import Profession

logger = logging.getLogger(__name__)

QUIZ_FILE = Path(__file__).parent.parent / "domain/constants/onboarding_quizzes.json"

class QuizEngine:
    def __init__(self):
        self.quizzes: Dict[str, ProfessionQuiz] = {}
        self._load_quizzes()
    
    def _load_quizzes(self):
        if not QUIZ_FILE.exists():
            logger.warning(f"Quiz file not found at {QUIZ_FILE}")
            return

        try:
            with open(QUIZ_FILE, "r") as f:
                data = json.load(f)
                for profession, quiz_data in data.items():
                    # The stored JSON matches ProfessionQuiz schema
                    self.quizzes[profession] = ProfessionQuiz(**quiz_data)
            logger.info(f"Loaded quizzes for {len(self.quizzes)} professions")
        except Exception as e:
            logger.error(f"Failed to load quizzes: {e}")

    def get_quiz_for_profession(self, profession: str) -> Optional[ProfessionQuiz]:
        """Retrieve the quiz for a given profession."""
        # Normalize profession string if needed, currently exact match
        return self.quizzes.get(profession)

    def calculate_score(self, submission: Dict[str, str], profession: str) -> dict:
        """
        Calculate score and determine starting lesson.
        
        Args:
            submission: Dict mapping question_id -> selected_option_letter (e.g. {'q1': 'B'})
            profession: User's profession
            
        Returns:
            Dict with score, starting_lesson, feedback
        """
        quiz = self.get_quiz_for_profession(profession)
        if not quiz:
            raise ValueError(f"No quiz found for profession: {profession}")
            
        total_questions = len(quiz.questions)
        correct_count = 0
        
        # Grading
        for question in quiz.questions:
            user_answer = submission.get(question.id)
            if user_answer and user_answer.upper() == question.correctAnswer.upper():
                correct_count += 1
                
        # Placement Logic (0-1: L01, 2-3: L04, 4-5: L11)
        if correct_count <= 1:
            starting_lesson = "l01_what_llms_are"
            stage = "Foundations"
            message = "Welcome! We'll start with the basics to build a strong foundation."
        elif correct_count <= 3:
            starting_lesson = "l04_where_llms_excel"
            stage = "Application"
            message = "Good job! You have the basics down. We'll start you at the Application stage."
        else:
            starting_lesson = "l11_cloud_apis"
            stage = "Mastery"
            message = "Excellent work! You're ready for advanced topics. Jumping to Mastery stage."
            
        return {
            "score": correct_count,
            "total": total_questions,
            "starting_lesson": starting_lesson,
            "stage": stage,
            "message": message
        }

quiz_engine = QuizEngine()
