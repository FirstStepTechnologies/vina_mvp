"""
Test script for Learner State Management.
Tests session creation, lesson completion, difficulty adjustments, and adaptation tracking.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from vina_backend.utils.logging import setup_logging
from vina_backend.integrations.db.engine import init_db, engine
from vina_backend.integrations.db.repositories.session_repository import SessionRepository
from vina_backend.integrations.db.repositories.profile_repository import ProfileRepository
from vina_backend.services.learner_state_manager import LearnerStateManager
from vina_backend.services.profile_builder import get_or_create_user_profile
from vina_backend.integrations.db.engine import get_session

import logging
logger = logging.getLogger(__name__)


def test_session_creation():
    """Test creating a new learning session."""
    print("\n" + "="*80)
    print("🧪 Test 1: Session Creation")
    print("="*80)
    
    session_gen = get_session()
    db_session = next(session_gen)
    
    try:
        # Create a user profile first
        profile = get_or_create_user_profile(
            "Clinical Researcher",
            "Pharma/Biotech",
            "Intermediate"
        )
        
        # Get user profile ID from database
        profile_repo = ProfileRepository(db_session)
        db_profile = profile_repo.get_profile(
            profile.profession,
            profile.industry,
            profile.experience_level
        )
        
        if not db_profile:
            print("  ❌ Failed to find user profile in database")
            return False
        
        # Create session
        session_repo = SessionRepository(db_session)
        manager = LearnerStateManager(session_repo)
        
        learner_state = manager.create_session(
            user_profile_id=db_profile.id,
            course_id="c_llm_foundations",
            initial_difficulty=3
        )
        
        print(f"  ✅ Session created: {learner_state.session_id}")
        print(f"     User Profile ID: {learner_state.user_profile_id}")
        print(f"     Course: {learner_state.course_id}")
        print(f"     Initial Difficulty: {learner_state.current_difficulty}")
        print(f"     Current Lesson Index: {learner_state.current_lesson_index}")
        
        # Get next lesson
        next_lesson = manager.get_next_lesson(learner_state.session_id)
        print(f"     Next Lesson: {next_lesson}")
        
        return learner_state.session_id
        
    finally:
        db_session.close()


def test_lesson_completion(session_id: str):
    """Test completing lessons with different quiz scores."""
    print("\n" + "="*80)
    print("🧪 Test 2: Lesson Completion & Difficulty Adjustment")
    print("="*80)
    
    session_gen = get_session()
    db_session = next(session_gen)
    
    try:
        session_repo = SessionRepository(db_session)
        manager = LearnerStateManager(session_repo)
        
        # Test scenarios: (lesson_id, quiz_score, expected_difficulty_change)
        test_cases = [
            ("l01_what_llms_are", 3, "increase"),  # Perfect score
            ("l02_tokens_context", 2, "maintain"),  # Passing score
            ("l03_why_outputs_vary", 3, "increase"),  # Perfect score again
        ]
        
        for lesson_id, quiz_score, expected_change in test_cases:
            # Get current state
            state_before = manager.get_session(session_id)
            difficulty_before = state_before.current_difficulty
            
            # Complete lesson
            state_after = manager.mark_lesson_complete(
                session_id,
                lesson_id,
                quiz_score
            )
            
            difficulty_after = state_after.current_difficulty
            
            # Verify difficulty change
            if expected_change == "increase":
                expected_diff = min(5, difficulty_before + 1)
            elif expected_change == "decrease":
                expected_diff = max(1, difficulty_before - 1)
            else:  # maintain
                expected_diff = difficulty_before
            
            success = difficulty_after == expected_diff
            status = "✅" if success else "❌"
            
            print(f"\n  {status} Lesson: {lesson_id}")
            print(f"     Quiz Score: {quiz_score}/3")
            print(f"     Difficulty: {difficulty_before} → {difficulty_after} (expected: {expected_diff})")
            print(f"     Completed Lessons: {len(state_after.completed_lessons)}")
            print(f"     Next Lesson: {manager.get_next_lesson(session_id)}")
            
            if not success:
                return False
        
        # Verify final state
        final_state = manager.get_session(session_id)
        print(f"\n  📊 Final State:")
        print(f"     Completed: {len(final_state.completed_lessons)}/17 lessons")
        print(f"     Progress: {manager.get_progress_percentage(session_id)}%")
        print(f"     Current Difficulty: {final_state.current_difficulty}")
        print(f"     Quiz Scores: {final_state.quiz_scores}")
        
        return True
        
    finally:
        db_session.close()


def test_adaptation_tracking(session_id: str):
    """Test recording adaptations."""
    print("\n" + "="*80)
    print("🧪 Test 3: Adaptation Tracking")
    print("="*80)
    
    session_gen = get_session()
    db_session = next(session_gen)
    
    try:
        session_repo = SessionRepository(db_session)
        manager = LearnerStateManager(session_repo)
        
        # Get initial state
        state_before = manager.get_session(session_id)
        adaptations_before = state_before.adaptation_count
        
        # Record some adaptations
        manager.record_adaptation(session_id, "l04_where_llms_excel", "simplify_this")
        manager.record_adaptation(session_id, "l04_where_llms_excel", "more_examples")
        
        # Get updated state
        state_after = manager.get_session(session_id)
        adaptations_after = state_after.adaptation_count
        
        success = adaptations_after == adaptations_before + 2
        status = "✅" if success else "❌"
        
        print(f"  {status} Adaptations recorded")
        print(f"     Before: {adaptations_before}")
        print(f"     After: {adaptations_after}")
        print(f"     Expected: {adaptations_before + 2}")
        
        return success
        
    finally:
        db_session.close()


def test_difficulty_edge_cases(session_id: str):
    """Test difficulty adjustment edge cases (min/max bounds)."""
    print("\n" + "="*80)
    print("🧪 Test 4: Difficulty Edge Cases")
    print("="*80)
    
    session_gen = get_session()
    db_session = next(session_gen)
    
    try:
        session_repo = SessionRepository(db_session)
        manager = LearnerStateManager(session_repo)
        
        # Test max difficulty (should not go above 5)
        manager.update_difficulty(session_id, 5)
        state = manager.mark_lesson_complete(session_id, "l04_where_llms_excel", 3)
        
        max_test = state.current_difficulty == 5
        print(f"  {'✅' if max_test else '❌'} Max difficulty capped at 5: {state.current_difficulty}")
        
        # Test min difficulty (should not go below 1)
        manager.update_difficulty(session_id, 1)
        state = manager.mark_lesson_complete(session_id, "l05_hallucinations", 0)
        
        min_test = state.current_difficulty == 1
        print(f"  {'✅' if min_test else '❌'} Min difficulty capped at 1: {state.current_difficulty}")
        
        return max_test and min_test
        
    finally:
        db_session.close()


if __name__ == "__main__":
    setup_logging()
    
    print("="*80)
    print("🧪 Learner State Management Tests")
    print("="*80)
    
    # Initialize database
    init_db()
    
    # Run tests
    session_id = test_session_creation()
    
    if session_id:
        test_2_passed = test_lesson_completion(session_id)
        test_3_passed = test_adaptation_tracking(session_id)
        test_4_passed = test_difficulty_edge_cases(session_id)
        
        print("\n" + "="*80)
        print("📊 Test Summary")
        print("="*80)
        print(f"  {'✅' if session_id else '❌'} Test 1: Session Creation")
        print(f"  {'✅' if test_2_passed else '❌'} Test 2: Lesson Completion & Difficulty Adjustment")
        print(f"  {'✅' if test_3_passed else '❌'} Test 3: Adaptation Tracking")
        print(f"  {'✅' if test_4_passed else '❌'} Test 4: Difficulty Edge Cases")
        
        all_passed = session_id and test_2_passed and test_3_passed and test_4_passed
        
        print("\n" + "="*80)
        if all_passed:
            print("✅ All tests passed! Learner State Management is working correctly.")
        else:
            print("❌ Some tests failed. Review the output above.")
        print("="*80)
    else:
        print("\n❌ Session creation failed. Cannot proceed with other tests.")
