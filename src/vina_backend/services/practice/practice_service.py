import json
import random
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional
from pathlib import Path

from vina_backend.domain.schemas.practice_quiz import (
    PracticeQuestion, 
    DailyPracticeSession, 
    PracticeSubmission, 
    PracticeResult
)
from vina_backend.integrations.db.models.user import User

# Constants
QUESTIONS_FILE = Path(__file__).parent.parent.parent / "domain" / "constants" / "practice_questions.json"
DAILY_QUESTION_COUNT = 10
POINTS_PER_QUESTION = 10

class PracticeService:
    def __init__(self):
        self._questions = self._load_questions()
        # In a real app, submissions would be in DB. 
        # For hackathon, we might store in a simple JSON or assume frontend tracks state via UserProfile 'lastPracticeDate'.
        # We'll use a simple in-memory store or file-based store for submissions if needed, 
        # but for now let's rely on UserProfile updates.

    def _load_questions(self) -> List[Dict]:
        if not QUESTIONS_FILE.exists():
            return []
        try:
            with open(QUESTIONS_FILE, "r") as f:
                data = json.load(f)
                return data.get("questions", [])
        except Exception:
            return []

    async def get_daily_session(self, user: User, max_lesson_id: Optional[str] = None) -> DailyPracticeSession:
        """
        Get specific questions for today based on user's profession.
        Optionally filter up to a specific lesson (inclusive).
        """
        today_iso = datetime.now(timezone.utc).date().isoformat()
        
        seed_str = f"{user.id}_{today_iso}"
        random.seed(seed_str)
        
        # Parse max lesson number if provided
        max_lesson_num = 999
        if max_lesson_id:
            try:
                # expected format l01_...
                # split l01 -> 01 -> int
                max_lesson_num = int(max_lesson_id.split('_')[0][1:])
            except (ValueError, IndexError):
                pass
        
        # Filter questions by profession AND max_lesson_id
        # Question IDs are: pq_{lesson}_{profession}_{index}
        # e.g., pq_l01_hr_manager_01
        
        profession = user.profile.profession if user.profile else ""
        user_prof_safe = profession.lower().replace(" ", "_") if profession else ""
        
        safe_available = []
        fallback_available = []
        
        for q in self._questions:
            # Check Max Lesson Constraint
            try:
                # q['lessonId'] format l01_what_llms_are
                q_lesson_id = q.get("lessonId", "")
                q_lesson_num = int(q_lesson_id.split('_')[0][1:])
                
                if q_lesson_num > max_lesson_num:
                    continue
            except (ValueError, IndexError):
                # If we fail to parse lesson ID, include it only if valid otherwise?
                # Safer to exclude if we are strict about filtering.
                continue

            # Check ID for profession match
            if user_prof_safe and f"_{user_prof_safe}_" in q["id"]:
                safe_available.append(q)
            else:
                fallback_available.append(q)
                
        # Prefer specific inputs, fall back to general if not enough
        pool = safe_available if len(safe_available) >= DAILY_QUESTION_COUNT else (safe_available + fallback_available)
        
        if not pool:
            return DailyPracticeSession(
                userId=user.id,
                date=today_iso,
                questions=[]
            )
            
        selected_data = random.sample(pool, min(len(pool), DAILY_QUESTION_COUNT))
        
        questions = []
        for q_data in selected_data:
            try:
                questions.append(PracticeQuestion(**q_data))
            except Exception:
                continue
                
        return DailyPracticeSession(
            userId=user.id,
            date=today_iso,
            questions=questions
        )

    async def process_submission(self, user: User, submission: PracticeSubmission) -> PracticeResult:
        """
        Grade submission and update user stats.
        """
        # Load questions to verify answers
        session = await self.get_daily_session(user)
        today_questions = session.questions
        question_map = {q.id: q for q in today_questions}
        
        score = 0
        total = len(today_questions)
        checks = []
        
        for ans in submission.answers:
            q_id = ans.get("questionId")
            selected = ans.get("selectedAnswer") # "A", "B", etc.
            
            if q_id in question_map:
                correct = question_map[q_id].correctAnswer
                is_right = (selected == correct)
                if is_right:
                    score += 1
                checks.append("✓" if is_right else "✗")
            else:
                checks.append("-") # Unknown question?

        points = score * POINTS_PER_QUESTION
        
        # Update User Profile (Streak logic)
        # usage: user_service.update_streak(...)
        # For now, we return the result calculation.
        
        # Calculate next reset (Midnight UTC)
        now = datetime.now(timezone.utc)
        tomorrow = now.date() + timedelta(days=1)
        next_reset = datetime(
            year=tomorrow.year, 
            month=tomorrow.month, 
            day=tomorrow.day, 
            tzinfo=timezone.utc
        )
        
        return PracticeResult(
            score=score,
            total=total,
            pointsEarned=points,
            checkmarkPattern="".join(checks),
            streakExtended=True, # deeper logic needed if we had full persistence
            nextResetTime=next_reset.isoformat()
        )
