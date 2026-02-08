import sys
from pathlib import Path
import asyncio

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from vina_backend.integrations.db.models.user import UserProfile
from vina_backend.services.practice.practice_service import PracticeService
from vina_backend.domain.schemas.practice_quiz import PracticeSubmission

async def main():
    service = PracticeService()
    
    # mock user
    user = UserProfile(
        id="test_user",
        email="test@example.com",
        name="Test User",
        profession="HR Manager", # Should trigger HR questions if available
        onboarding_completed=True
    )
    
    print("--- Testing Get Daily Session ---")
    session = await service.get_daily_session(user)
    print(f"Date: {session.date}")
    print(f"Questions: {len(session.questions)}")
    for q in session.questions:
        print(f" - [{q.id}] {q.text[:50]}...")
        
    if not session.questions:
        print("No questions found. Please run generation script first.")
        # We can simulate generation here or just warn.
        # Ensure we have at least some dummy questions in the JSON file for this to work
        return

    print("\n--- Testing Submission ---")
    # cheat: answer correctly
    answers = []
    for q in session.questions:
        answers.append({
            "questionId": q.id,
            "selectedAnswer": q.correctAnswer
        })
        
    sub = PracticeSubmission(
        userId=user.id,
        date=session.date,
        answers=answers
    )
    
    result = await service.process_submission(user, sub)
    print(f"Score: {result.score}/{result.total}")
    print(f"Points: {result.pointsEarned}")
    print(f"Streak Extended: {result.streakExtended}")
    print(f"Patterns: {result.checkmarkPattern}")

    print("\n--- Testing Lesson Filtering ---")
    # Test valid filter
    # Assuming we have l01 questions. If we ask for max l01, we should get them.
    session_filtered = await service.get_daily_session(user, max_lesson_id="l01")
    print(f"Questions (Max l01): {len(session_filtered.questions)}")

    # Test restrictive filter (l00 should yield 0 if all questions are l01+)
    session_empty = await service.get_daily_session(user, max_lesson_id="l00")
    print(f"Questions (Max l00): {len(session_empty.questions)}")
    
if __name__ == "__main__":
    asyncio.run(main())
