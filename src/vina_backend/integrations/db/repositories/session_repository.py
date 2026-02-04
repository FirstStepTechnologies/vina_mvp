"""
Repository for learner session database operations.
"""
from typing import Optional
from datetime import datetime
from sqlmodel import Session, select

from vina_backend.integrations.db.models.session import LearnerSession
from vina_backend.domain.schemas.learner_state import LearnerState


class SessionRepository:
    """Repository for managing learner session persistence."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create_session(self, learner_state: LearnerState) -> LearnerSession:
        """
        Create a new learner session in the database.
        
        Args:
            learner_state: Learner state to persist
        
        Returns:
            Created database session
        """
        db_session = LearnerSession(
            session_id=learner_state.session_id,
            user_profile_id=learner_state.user_profile_id,
            course_id=learner_state.course_id,
            current_lesson_index=learner_state.current_lesson_index,
            completed_lessons=learner_state.completed_lessons,
            current_difficulty=learner_state.current_difficulty,
            lesson_difficulty_history=learner_state.lesson_difficulty_history,
            quiz_scores=learner_state.quiz_scores,
            adaptation_count=learner_state.adaptation_count,
            created_at=learner_state.created_at,
            updated_at=learner_state.updated_at,
            last_active=datetime.utcnow()
        )
        
        self.session.add(db_session)
        self.session.commit()
        self.session.refresh(db_session)
        
        return db_session
    
    def get_session_by_id(self, session_id: str) -> Optional[LearnerSession]:
        """
        Retrieve a session by its session_id.
        
        Args:
            session_id: UUID string of the session
        
        Returns:
            LearnerSession if found, None otherwise
        """
        statement = select(LearnerSession).where(LearnerSession.session_id == session_id)
        return self.session.exec(statement).first()
    
    def get_active_session_for_user(
        self, 
        user_profile_id: int, 
        course_id: str
    ) -> Optional[LearnerSession]:
        """
        Get the most recent active session for a user in a specific course.
        
        Args:
            user_profile_id: User profile ID
            course_id: Course identifier
        
        Returns:
            Most recent session if found, None otherwise
        """
        statement = (
            select(LearnerSession)
            .where(
                LearnerSession.user_profile_id == user_profile_id,
                LearnerSession.course_id == course_id
            )
            .order_by(LearnerSession.last_active.desc())
        )
        return self.session.exec(statement).first()
    
    def update_session(self, learner_state: LearnerState) -> LearnerSession:
        """
        Update an existing session with new learner state.
        
        Args:
            learner_state: Updated learner state
        
        Returns:
            Updated database session
        
        Raises:
            ValueError: If session not found
        """
        db_session = self.get_session_by_id(learner_state.session_id)
        
        if not db_session:
            raise ValueError(f"Session {learner_state.session_id} not found")
        
        # Update fields
        db_session.current_lesson_index = learner_state.current_lesson_index
        db_session.completed_lessons = learner_state.completed_lessons
        db_session.current_difficulty = learner_state.current_difficulty
        db_session.lesson_difficulty_history = learner_state.lesson_difficulty_history
        db_session.quiz_scores = learner_state.quiz_scores
        db_session.adaptation_count = learner_state.adaptation_count
        db_session.updated_at = datetime.utcnow()
        db_session.last_active = datetime.utcnow()
        
        self.session.add(db_session)
        self.session.commit()
        self.session.refresh(db_session)
        
        return db_session
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session from the database.
        
        Args:
            session_id: Session to delete
        
        Returns:
            True if deleted, False if not found
        """
        db_session = self.get_session_by_id(session_id)
        
        if not db_session:
            return False
        
        self.session.delete(db_session)
        self.session.commit()
        
        return True
    
    def to_learner_state(self, db_session: LearnerSession) -> LearnerState:
        """
        Convert database session to Pydantic LearnerState.
        
        Args:
            db_session: Database session
        
        Returns:
            LearnerState Pydantic model
        """
        return LearnerState(
            session_id=db_session.session_id,
            user_profile_id=db_session.user_profile_id,
            course_id=db_session.course_id,
            current_lesson_index=db_session.current_lesson_index,
            completed_lessons=db_session.completed_lessons,
            current_difficulty=db_session.current_difficulty,
            lesson_difficulty_history=db_session.lesson_difficulty_history,
            quiz_scores=db_session.quiz_scores,
            adaptation_count=db_session.adaptation_count,
            created_at=db_session.created_at,
            updated_at=db_session.updated_at
        )
