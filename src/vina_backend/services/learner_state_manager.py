"""
Learner State Manager - Core service for managing learner progress and state.
"""
import uuid
import logging
from typing import Optional
from datetime import datetime

from vina_backend.domain.schemas.learner_state import LearnerState
from vina_backend.domain.schemas.profile import UserProfileData
from vina_backend.integrations.db.repositories.session_repository import SessionRepository
from vina_backend.services.course_loader import load_course_config

logger = logging.getLogger(__name__)


class LearnerStateManager:
    """
    Manages learner state including progress tracking, difficulty adjustments,
    and quiz performance.
    """
    
    def __init__(self, session_repository: SessionRepository):
        self.repo = session_repository
    
    def create_session(
        self,
        user_profile_id: int,
        course_id: str,
        initial_difficulty: int = 3
    ) -> LearnerState:
        """
        Create a new learning session for a user.
        
        Args:
            user_profile_id: ID of the user profile
            course_id: Course identifier (e.g., 'c_llm_foundations')
            initial_difficulty: Starting difficulty level (1, 3, or 5)
        
        Returns:
            New LearnerState
        """
        # Validate difficulty level
        if initial_difficulty not in [1, 3, 5]:
            logger.warning(f"Invalid difficulty {initial_difficulty}, defaulting to 3")
            initial_difficulty = 3
        
        # Validate course exists
        try:
            course_config = load_course_config(course_id)
        except FileNotFoundError:
            raise ValueError(f"Course {course_id} not found")
        
        # Generate unique session ID
        session_id = str(uuid.uuid4())
        
        # Create learner state
        learner_state = LearnerState(
            session_id=session_id,
            user_profile_id=user_profile_id,
            course_id=course_id,
            current_lesson_index=0,
            current_difficulty=initial_difficulty,
            lesson_difficulty_history={},
            completed_lessons=[],
            quiz_scores={},
            adaptation_count=0
        )
        
        # Persist to database
        self.repo.create_session(learner_state)
        
        logger.info(
            f"Created session {session_id} for user_profile {user_profile_id} "
            f"in course {course_id} at difficulty {initial_difficulty}"
        )
        
        return learner_state
    
    def get_session(self, session_id: str) -> Optional[LearnerState]:
        """
        Retrieve a learning session by ID.
        
        Args:
            session_id: Session identifier
        
        Returns:
            LearnerState if found, None otherwise
        """
        db_session = self.repo.get_session_by_id(session_id)
        
        if not db_session:
            logger.warning(f"Session {session_id} not found")
            return None
        
        return self.repo.to_learner_state(db_session)
    
    def get_or_create_session(
        self,
        user_profile_id: int,
        course_id: str,
        initial_difficulty: int = 3
    ) -> LearnerState:
        """
        Get existing session or create new one if none exists.
        
        Args:
            user_profile_id: User profile ID
            course_id: Course identifier
            initial_difficulty: Difficulty if creating new session
        
        Returns:
            Existing or new LearnerState
        """
        # Try to get existing session
        db_session = self.repo.get_active_session_for_user(user_profile_id, course_id)
        
        if db_session:
            logger.info(f"Found existing session {db_session.session_id} for user {user_profile_id}")
            return self.repo.to_learner_state(db_session)
        
        # Create new session
        logger.info(f"No existing session found, creating new one for user {user_profile_id}")
        return self.create_session(user_profile_id, course_id, initial_difficulty)
    
    def update_difficulty(self, session_id: str, new_difficulty: int) -> LearnerState:
        """
        Update the current difficulty level for a session.
        
        Args:
            session_id: Session identifier
            new_difficulty: New difficulty level (1, 3, or 5)
        
        Returns:
            Updated LearnerState
        
        Raises:
            ValueError: If session not found or invalid difficulty
        """
        # Validate difficulty
        if new_difficulty not in [1, 3, 5]:
            raise ValueError(f"Invalid difficulty level: {new_difficulty}. Must be 1, 3, or 5.")
        
        # Get current state
        learner_state = self.get_session(session_id)
        if not learner_state:
            raise ValueError(f"Session {session_id} not found")
        
        # Update difficulty
        old_difficulty = learner_state.current_difficulty
        learner_state.current_difficulty = new_difficulty
        learner_state.updated_at = datetime.utcnow()
        
        # Persist changes
        self.repo.update_session(learner_state)
        
        logger.info(
            f"Updated difficulty for session {session_id}: {old_difficulty} → {new_difficulty}"
        )
        
        return learner_state
    
    def mark_lesson_complete(
        self,
        session_id: str,
        lesson_id: str,
        quiz_score: int,
        difficulty_used: Optional[int] = None
    ) -> LearnerState:
        """
        Mark a lesson as complete and adjust difficulty based on quiz score.
        
        Difficulty adjustment rules:
        - 3/3 correct: increase difficulty by 1 (max 5)
        - 2/3 correct: maintain current difficulty
        - 0-1/3 correct: decrease difficulty by 1 (min 1)
        
        Args:
            session_id: Session identifier
            lesson_id: Lesson that was completed
            quiz_score: Score out of 3
            difficulty_used: Difficulty level used for this lesson (defaults to current)
        
        Returns:
            Updated LearnerState
        
        Raises:
            ValueError: If session not found or invalid quiz score
        """
        # Validate quiz score
        if quiz_score not in [0, 1, 2, 3]:
            raise ValueError(f"Invalid quiz score: {quiz_score}. Must be 0-3.")
        
        # Get current state
        learner_state = self.get_session(session_id)
        if not learner_state:
            raise ValueError(f"Session {session_id} not found")
        
        # Use current difficulty if not specified
        if difficulty_used is None:
            difficulty_used = learner_state.current_difficulty
        
        # Record quiz score
        learner_state.quiz_scores[lesson_id] = quiz_score
        
        # Record difficulty used for this lesson
        learner_state.lesson_difficulty_history[lesson_id] = difficulty_used
        
        # Add to completed lessons if not already there
        if lesson_id not in learner_state.completed_lessons:
            learner_state.completed_lessons.append(lesson_id)
        
        # Advance lesson index
        learner_state.current_lesson_index += 1
        
        # Adjust difficulty based on quiz performance
        old_difficulty = learner_state.current_difficulty
        
        if quiz_score == 3:
            # Perfect score: increase difficulty
            learner_state.current_difficulty = min(5, learner_state.current_difficulty + 1)
            adjustment = "increased" if learner_state.current_difficulty > old_difficulty else "maintained (at max)"
        elif quiz_score == 2:
            # Passing score: maintain difficulty
            adjustment = "maintained"
        else:  # quiz_score in [0, 1]
            # Failing score: decrease difficulty
            learner_state.current_difficulty = max(1, learner_state.current_difficulty - 1)
            adjustment = "decreased" if learner_state.current_difficulty < old_difficulty else "maintained (at min)"
        
        learner_state.updated_at = datetime.utcnow()
        
        # Persist changes
        self.repo.update_session(learner_state)
        
        logger.info(
            f"Lesson {lesson_id} completed in session {session_id}. "
            f"Quiz score: {quiz_score}/3. Difficulty {adjustment}: {old_difficulty} → {learner_state.current_difficulty}"
        )
        
        return learner_state
    
    def get_next_lesson(self, session_id: str) -> Optional[str]:
        """
        Get the ID of the next lesson to take.
        
        Args:
            session_id: Session identifier
        
        Returns:
            Next lesson ID, or None if course is complete
        
        Raises:
            ValueError: If session not found
        """
        learner_state = self.get_session(session_id)
        if not learner_state:
            raise ValueError(f"Session {session_id} not found")
        
        # Load course config
        course_config = load_course_config(learner_state.course_id)
        lessons = course_config["lessons"]
        
        # Check if course is complete
        if learner_state.current_lesson_index >= len(lessons):
            logger.info(f"Course complete for session {session_id}")
            return None
        
        # Get next lesson
        next_lesson = lessons[learner_state.current_lesson_index]
        next_lesson_id = next_lesson["lesson_id"]
        
        logger.info(
            f"Next lesson for session {session_id}: {next_lesson_id} "
            f"(index {learner_state.current_lesson_index})"
        )
        
        return next_lesson_id
    
    def record_adaptation(
        self,
        session_id: str,
        lesson_id: str,
        adaptation_type: str
    ) -> None:
        """
        Record that a learner requested an adaptation (simplify, get_to_point, etc.).
        
        Args:
            session_id: Session identifier
            lesson_id: Lesson where adaptation was requested
            adaptation_type: Type of adaptation requested
        
        Raises:
            ValueError: If session not found
        """
        learner_state = self.get_session(session_id)
        if not learner_state:
            raise ValueError(f"Session {session_id} not found")
        
        # Increment adaptation count
        learner_state.adaptation_count += 1
        learner_state.updated_at = datetime.utcnow()
        
        # Persist changes
        self.repo.update_session(learner_state)
        
        logger.info(
            f"Adaptation '{adaptation_type}' recorded for session {session_id}, "
            f"lesson {lesson_id}. Total adaptations: {learner_state.adaptation_count}"
        )
    
    def get_progress_percentage(self, session_id: str) -> float:
        """
        Calculate course completion percentage.
        
        Args:
            session_id: Session identifier
        
        Returns:
            Completion percentage (0-100)
        
        Raises:
            ValueError: If session not found
        """
        learner_state = self.get_session(session_id)
        if not learner_state:
            raise ValueError(f"Session {session_id} not found")
        
        # Load course config
        course_config = load_course_config(learner_state.course_id)
        total_lessons = len(course_config["lessons"])
        
        if total_lessons == 0:
            return 0.0
        
        completed = len(learner_state.completed_lessons)
        percentage = (completed / total_lessons) * 100
        
        return round(percentage, 2)
