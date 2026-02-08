Let's Practice Feature - Product Requirements Document
Version: 1.0
Last Updated: February 7, 2026
Status: Ready for Implementation
Target: Vina Backend - Daily Practice Quiz System

Table of Contents

Executive Summary
Feature Overview
User Experience Flow
Practice Question Specifications
Data Models
Multi-Agent Generation Pipeline
API Endpoints
Frontend Integration Points
Edge Cases & Error Handling
Implementation Checklist


1. Executive Summary
1.1 Purpose
Let's Practice is a daily active recall quiz that provides spaced repetition across all completed lessons. Unlike post-lesson quizzes (which test one specific lesson immediately after learning), this feature combats the forgetting curve by revisiting concepts days or weeks after initial learning. It serves as both a retention tool (pedagogical) and an engagement hook (product) to bring users back daily.
1.2 Core Behavior
AspectSpecificationAvailabilityOnce per day (resets at midnight user's local time)Unlock ConditionAfter completing first lessonQuestion CountUp to 10 questions (adaptive to completed lessons)Question SourceRandom selection from practice question poolScoring10 points per correct answer (max 100 points/day)Streak ImpactCompleting practice extends daily streakRetry PolicyOne attempt per day (no retries)
1.3 Success Metrics

Daily Active Users: 40%+ of users complete daily practice
Retention: Users who practice daily have 2x higher 7-day retention
Streak Maintenance: Practice prevents 30%+ of streak breaks
Knowledge Retention: Users who practice score 15%+ higher on later lessons

1.4 Scope
In Scope:

Generate 680 practice questions (17 lessons × 4 professions × 10 questions)
Random question selection from completed lessons
Daily reset logic (midnight user's local time)
Points system (10 pts per correct, proportional if <10 questions available)
Streak extension on completion
Simple results summary (score + checkmark pattern)

Out of Scope (Future Enhancements):

Spaced repetition algorithm (weighted by forgetting curve)
Adaptive difficulty (questions get harder as user improves)
Lesson-specific review (choose which lessons to practice)
Question explanations during quiz (only in summary)
Leaderboards (daily/weekly top scores)
Practice streaks (separate from main streak)


2. Feature Overview
2.1 User Journey
Day 1:
- User completes L01 (first lesson)
- "Let's Practice" tab unlocks
- Badge appears on tab (red dot indicator)

Day 2:
- User opens app, sees badge on Practice tab
- Taps "Let's Practice" → Quiz screen
- Answers 3 questions (only L01 completed, so 3 available from 10-question pool)
- Gets 2/3 correct → Earns 20 points
- Streak extends to Day 2
- "Next challenge in 22h 15m" countdown appears

Day 3:
- User completes L02 and L03
- Now has 3 lessons completed
- Practice pool: 30 questions available (3 lessons × 10 questions)
- Daily practice resets at midnight
- User takes practice: Gets 10 random questions from pool
- Gets 8/10 correct → Earns 80 points
- Streak extends to Day 3

Day 4:
- User busy, doesn't complete new lessons
- BUT completes daily practice → Streak maintained (doesn't break)
- This is the key retention mechanic
2.2 Why Separate from Lesson Quizzes?
Pedagogical Reasons:

Spaced Repetition: Questions appear days after initial learning (better retention)
Interleaved Practice: Mix questions from different lessons (improves recall)
Low Stakes: No unlocking requirements, just reinforcement

Product Reasons:

Daily Engagement: Users return even on days they don't complete lessons
Streak Safety Net: Prevents streak breaks during busy periods
Variety: New questions keep it fresh (not just repeating lesson quizzes)

Hackathon Demo Reasons:

Judge Experience: If judge only completes 1 lesson, they won't see repeated questions
Quality Showcase: Demonstrates ability to generate large question pools (680 questions)
System Design: Shows separate concerns (learning vs. retention)


3. User Experience Flow
3.1 First Time Experience (Locked State)
┌─────────────────────────────────────────────────────────────┐
│ Let's Practice Tab (LOCKED)                                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                     🔒                                      │
│              Locked                                         │
│                                                             │
│  Complete your first lesson to unlock                       │
│  daily practice!                                            │
│                                                             │
│  Daily practice helps you retain what                       │
│  you've learned through spaced repetition.                  │
│                                                             │
│  [Go to Lessons →]                                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
Trigger: User has 0 completed lessons
Action: Tap "Go to Lessons" → Navigate to /course-map

3.2 Daily Practice Available
┌─────────────────────────────────────────────────────────────┐
│ Let's Practice 🔔                                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Daily Challenge                                            │
│  Test your knowledge!                                       │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ 🎯 Up to 10 Questions                                 │ │
│  │ 💎 10 pts each                                        │ │
│  │ 🔥 Keep your streak                                   │ │
│  │                                                       │ │
│  │ [Start Practice →]                                    │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  From lessons:                                              │
│  • L01, L02, L03 (3 completed)                              │
│                                                             │
│  Note: Complete more lessons to                             │
│  increase variety!                                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
Trigger:

User has ≥1 completed lesson
User has NOT completed practice today
Current time < midnight reset

Interactions:

Tap "Start Practice" → Navigate to practice quiz screen
Shows number of completed lessons (context)
If <5 lessons completed, show encouragement to complete more


3.3 Practice Quiz In Progress
┌─────────────────────────────────────────────────────────────┐
│ Daily Practice                                              │
│ Question 3 of 10                  ●●●○○○○○○○                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ You're using an LLM to draft a clinical trial protocol.     │
│ Which scenario is MOST likely to produce a hallucination?   │
│                                                             │
│ ○ A) Summarizing a 2020 published study                    │
│                                                             │
│ ○ B) Describing standard industry practices                │
│                                                             │
│ ○ C) Citing a specific 2024 regulation that doesn't exist  │
│                                                             │
│ ○ D) Paraphrasing your previous protocol                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
Flow:

User selects answer (e.g., taps "C")
No immediate feedback (unlike lesson quizzes)
Auto-advance to next question after 0.5s delay
Repeat for all questions (up to 10)
Navigate to results screen

Key Differences from Lesson Quiz:

No explanations during quiz (keeps it fast)
No visual feedback per question (no green/red borders)
All feedback shown at end (summary view)

Rationale:

Faster completion (~2-3 minutes vs. 5 minutes for lesson quiz)
Reduces cognitive load (focus on recall, not learning new info)
Encourages daily habit (quick and easy)


3.4 Practice Completed
┌─────────────────────────────────────────────────────────────┐
│ Daily Practice                                              │
├─────────────────────────────────────────────────────────────┤
│                     ✅                                      │
│          Completed Today!                                   │
│                                                             │
│  Great work! You earned                                     │
│  80/100 points                                              │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ Your Answers:                                         │ │
│  │ ✓✓✓✓✓✓✗✓✗✓                                            │ │
│  │                                                       │ │
│  │ 8/10 correct                                          │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  🔥 Streak extended!                                        │
│                                                             │
│  ⏰ Next challenge in                                       │
│  14h 32m                                                    │
│                                                             │
│  [Back to Home]                                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
Display Logic:

Score: X/Y correct (where Y = number of questions shown, not always 10)
Points: (X/Y) × 100 rounded to nearest 10 (e.g., 8/10 = 80 points)
Checkmarks: Visual pattern (✓ = correct, ✗ = incorrect)
Streak: "Streak extended!" message
Countdown: Time until next practice available (midnight local time)

Edge Case - Few Questions Available:
If user completed 1 lesson (10 questions in pool):
- Show all 10 questions
- Score: 7/10 correct
- Points: 70 points

If user completed 2 lessons (20 questions in pool):
- Show 10 random questions
- Score: 9/10 correct
- Points: 90 points

3.5 Already Completed Today
┌─────────────────────────────────────────────────────────────┐
│ Let's Practice 🔔                                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ✅ Completed Today                                         │
│                                                             │
│  Great work! You earned                                     │
│  80/100 points                                              │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ Your Answers:                                         │ │
│  │ ✓✓✓✓✓✓✗✓✗✓                                            │ │
│  │                                                       │ │
│  │ 8/10 correct                                          │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  ⏰ Next challenge in                                       │
│  14h 32m                                                    │
│                                                             │
│  💡 Tip: Complete more lessons to unlock                    │
│  new practice questions!                                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
Trigger: User already completed practice today
Behavior:

Show completed summary (persistent until midnight reset)
No retry button (one attempt per day)
Countdown to next reset
Encourage completing more lessons (grows practice pool)


4. Practice Question Specifications
4.1 Question Pool Structure
Total Questions: 680

17 lessons × 4 professions × 10 questions per lesson

Storage: src/vina_backend/domain/constants/practice_questions.json
Structure:
json{
  "l01_what_llms_are": {
    "Clinical Researcher": [
      {
        "id": "pq_l01_clinical_01",
        "text": "Question text...",
        "options": [...],
        "correctAnswer": "B",
        "explanation": "...",
        "conceptTested": "llm_definition"
      },
      // ... 9 more questions
    ],
    "HR Manager": [
      // ... 10 questions
    ],
    "Project Manager": [
      // ... 10 questions
    ],
    "Marketing Manager": [
      // ... 10 questions
    ]
  },
  "l02_tokens_context": {
    // ... same structure for all 17 lessons
  }
}
```

### 4.2 Question Design Requirements

**Same as Lesson Quizzes, But Different Questions:**

| Aspect | Specification |
|--------|---------------|
| **Format** | Multiple choice, single answer (A/B/C/D) |
| **Options** | Exactly 4 per question |
| **Profession Context** | Tailored to user's profession |
| **Scenario-Based** | Realistic work situations |
| **Concept Coverage** | Same concepts as lesson quizzes (but different phrasing) |
| **Difficulty** | Same as lesson quiz base difficulty |
| **Explanation** | 2-3 sentences (shown only in future feature) |

**Key Difference from Lesson Quizzes:**
- **Broader Concept Testing:** Practice questions can test ANY concept from the lesson (not limited to the 3 concepts tested in lesson quiz)
- **Variety:** 10 questions gives more angles on the same material
- **Phrasing:** Different scenarios, examples, and distractors than lesson quiz

**Example - Lesson Quiz Question:**
```
Q: You're drafting a clinical trial protocol using an LLM. The model 
   confidently cites a 2023 study that doesn't exist. This is an example of:
   
   A) Context window limitation
   B) Hallucination ✓
   C) Token prediction error
   D) Training data bias
```

**Example - Practice Question (Same Concept, Different Phrasing):**
```
Q: In clinical research, which scenario is MOST likely to produce an 
   LLM hallucination?
   
   A) Summarizing a published 2020 study
   B) Describing standard industry practices
   C) Citing a specific 2024 regulation that doesn't exist ✓
   D) Paraphrasing your previous protocol
4.3 Question Selection Algorithm
Daily Practice Session Logic:
pythondef select_practice_questions(user_id: str) -> List[Question]:
    """
    Select up to 10 random questions from completed lessons.
    
    Algorithm:
    1. Get user's completed lessons (e.g., [l01, l02, l03])
    2. Get user's profession (e.g., "Clinical Researcher")
    3. Build question pool: All practice questions from completed lessons
    4. Randomly shuffle pool
    5. Select first min(10, pool_size) questions
    6. Return questions
    """
    
    # Get user data
    completed_lessons = get_completed_lessons(user_id)
    profession = get_user_profession(user_id)
    
    # Build pool
    question_pool = []
    for lesson_id in completed_lessons:
        lesson_questions = practice_questions[lesson_id][profession]
        question_pool.extend(lesson_questions)
    
    # Random selection
    random.shuffle(question_pool)
    selected = question_pool[:min(10, len(question_pool))]
    
    return selected
Example Scenarios:
Completed LessonsQuestions AvailableQuestions ShownNotes1 (L01)1010All questions from L012 (L01, L02)2010Random 10 from pool of 205 (L01-L05)5010Random 10 from pool of 5017 (All)17010Random 10 from pool of 170
No Balancing: Pure random means one session might have 7 questions from L01 and 3 from L05. This is pedagogically acceptable (random interleaving).

5. Data Models
5.1 Pydantic Schemas
python# src/vina_backend/domain/schemas/practice_quiz.py

from typing import List, Optional
from pydantic import BaseModel, Field, validator

class PracticeQuizOption(BaseModel):
    """Single answer option for a practice question."""
    text: str = Field(
        ..., 
        description="Option text WITHOUT letter prefix"
    )
    is_correct: bool = Field(
        ..., 
        description="Whether this is the correct answer"
    )


class PracticeQuestion(BaseModel):
    """Single question in the practice pool."""
    
    id: str = Field(
        ..., 
        description="Unique question ID (e.g., 'pq_l01_clinical_01')",
        regex="^pq_l\\d{2}_[a-z]+_\\d{2}$"
    )
    
    lessonId: str = Field(
        ..., 
        description="Source lesson ID (e.g., 'l01_what_llms_are')"
    )
    
    text: str = Field(
        ..., 
        description="Question text (scenario-based, profession-specific)",
        min_length=20
    )
    
    options: List[PracticeQuizOption] = Field(
        ..., 
        min_items=4, 
        max_items=4,
        description="Exactly 4 answer options"
    )
    
    correctAnswer: str = Field(
        ..., 
        description="Correct answer letter (A/B/C/D)",
        regex="^[ABCD]$"
    )
    
    explanation: str = Field(
        ..., 
        description="Explanation of correct answer (2-3 sentences)",
        min_length=50
    )
    
    conceptTested: str = Field(
        ..., 
        description="Core concept tested from the lesson"
    )
    
    @validator('options')
    def validate_exactly_one_correct(cls, v):
        """Ensure exactly one option is marked correct."""
        correct_count = sum(1 for opt in v if opt.is_correct)
        if correct_count != 1:
            raise ValueError(f"Expected exactly 1 correct answer, found {correct_count}")
        return v


class DailyPracticeSession(BaseModel):
    """Practice session data."""
    
    userId: str
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    questions: List[PracticeQuestion] = Field(
        ...,
        min_items=1,
        max_items=10,
        description="Questions for this session (1-10)"
    )


class PracticeSubmission(BaseModel):
    """User's practice quiz submission."""
    
    userId: str
    date: str = Field(..., description="Date of practice (YYYY-MM-DD)")
    answers: List[dict] = Field(
        ...,
        description="List of {questionId, selectedAnswer, isCorrect}"
    )


class PracticeResult(BaseModel):
    """Result after practice submission."""
    
    score: int = Field(..., ge=0, le=10, description="Number correct")
    total: int = Field(..., ge=1, le=10, description="Total questions")
    pointsEarned: int = Field(..., description="Points awarded (score × 10)")
    checkmarkPattern: str = Field(..., description="Visual pattern (e.g., '✓✓✗✓✓✓✗✓✓✓')")
    streakExtended: bool = Field(..., description="Whether streak was extended")
    nextResetTime: str = Field(..., description="ISO timestamp of next midnight reset")
```

---

## 6. Multi-Agent Generation Pipeline

### 6.1 Reusing Existing Agent Code

**Good News:** We can reuse the exact same agent classes from lesson quiz generation:

- `LessonQuizGeneratorAgent` → Rename to `PracticeQuestionGeneratorAgent` (or keep generic)
- `LessonQuizReviewerAgent` → Reuse as-is
- `LessonQuizRewriterAgent` → Reuse as-is

**Only Changes:**
1. **Prompt templates** (emphasize variety, different phrasing)
2. **Output schema** (10 questions instead of 3)
3. **Storage location** (`practice_questions.json` instead of `lesson_quizzes.json`)

### 6.2 Generator Agent Prompt (Practice Questions)

**File:** `src/vina_backend/services/agents/practice_question_generator.py`

**Prompt Template:**
```
You are a **Master Quiz Designer** creating practice questions for spaced repetition.

Your task: Create 10 practice questions for Lesson {lesson_id} tailored to a **{profession}**.

**Context:**
- These questions are for DAILY PRACTICE (not the lesson quiz)
- Users will see these questions DAYS/WEEKS after completing the lesson
- Goal: Reinforce retention through varied phrasing and scenarios

**Lesson Objectives:**
{lesson_objectives}

**Learner Profile:**
{user_profile_summary}

**CRITICAL: Avoid Overlap with Lesson Quiz**
The lesson quiz already tests 3 concepts from this lesson. Your practice questions should:
- Test the SAME concepts (reinforcement)
- Use DIFFERENT scenarios, examples, and phrasing
- Provide MORE angles on the material (10 questions vs. 3)

**Question Design Requirements:**

1. **Variety (CRITICAL):**
   - Each question must test the same concept from a DIFFERENT angle
   - Vary the scenario types (e.g., if Q1 is about drafting protocols, Q2 should be about reviewing reports)
   - Vary the question stems (e.g., "Which scenario...", "What causes...", "Best practice...")

2. **Profession-Specific Context:**
   - Every question references {profession}'s actual work
   - Use domain terminology consistently
   - Scenarios should feel authentic (not generic)

3. **Spaced Repetition Optimization:**
   - Questions should trigger recall, not teach new concepts
   - Assume user learned this weeks ago (test retention, not fresh memory)
   - Focus on practical application (not just definitions)

4. **Distractor Quality:**
   - Wrong answers should be plausible (common mistakes)
   - Avoid obvious throwaways
   - Mix difficulty across the 10 questions (some easy recall, some harder application)

5. **Concept Coverage:**
   - Test all major concepts from the lesson
   - Ensure diversity (no 5 questions all testing the same thing)
   - Balance breadth (cover all concepts) with depth (multiple angles on key concepts)

**Output Format:**
Return JSON array of 10 questions:

{
  "lessonId": "{lesson_id}",
  "profession": "{profession}",
  "questions": [
    {
      "id": "pq_{lesson_id}_{profession_slug}_01",
      "lessonId": "{lesson_id}",
      "text": "Scenario-based question...",
      "options": [
        {"text": "Option A", "is_correct": false},
        {"text": "Correct option", "is_correct": true},
        {"text": "Option C", "is_correct": false},
        {"text": "Option D", "is_correct": false}
      ],
      "correctAnswer": "B",
      "explanation": "Educational explanation...",
      "conceptTested": "hallucination_recognition"
    },
    // ... 9 more questions
  ]
}

**CRITICAL:**
- Exactly 10 questions
- Each question has exactly 4 options
- Exactly 1 option marked correct per question
- Concepts tested should cover the full lesson scope

6.3 Reviewer Agent Modifications
No changes to agent code, but update rubric slightly:
Additional Review Criteria for Practice Questions:

✓ 10 questions (not 3)
✓ Questions vary in scenario/phrasing (not repetitive)
✓ Concepts cover full lesson scope (not just 3 concepts)
✓ Questions feel like "recall from weeks ago" (not "just learned this")


6.4 Orchestration Script
File: scripts/generate_practice_questions.py
Key Features:

Command-line arguments for flexibility
Can generate for specific lesson range
Can generate for specific profession
Parallel generation for speed (optional)

Implementation:
python# scripts/generate_practice_questions.py

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import List

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from vina_backend.services.agents.practice_question_generator import PracticeQuestionGeneratorAgent
from vina_backend.services.agents.lesson_quiz_reviewer import LessonQuizReviewerAgent
from vina_backend.services.agents.lesson_quiz_rewriter import LessonQuizRewriterAgent
from vina_backend.services.course_loader import load_course_config
from vina_backend.services.profile_builder import get_or_create_profile
from vina_backend.domain.schemas.practice_quiz import PracticeQuestion
from vina_backend.domain.constants.enums import Profession
from vina_backend.utils.logging import setup_logging

# Opik integration
try:
    from opik import track
    OPIK_AVAILABLE = True
except ImportError:
    OPIK_AVAILABLE = False
    def track(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

setup_logging("INFO")
logger = logging.getLogger("PRACTICE_QUIZ_PIPELINE")

COURSE_ID = "c_llm_foundations"
OUTPUT_FILE = Path(__file__).parent.parent / "src/vina_backend/domain/constants/practice_questions.json"
QUESTIONS_PER_LESSON = 10


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate practice questions for daily practice feature"
    )
    
    parser.add_argument(
        "--lessons",
        type=str,
        help="Comma-separated lesson IDs (e.g., 'l01_what_llms_are,l02_tokens_context'). "
             "If omitted, generates for all 17 lessons."
    )
    
    parser.add_argument(
        "--profession",
        type=str,
        choices=[p.value for p in Profession],
        help="Single profession to generate for. If omitted, generates for all 4 professions."
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default=str(OUTPUT_FILE),
        help=f"Output file path (default: {OUTPUT_FILE})"
    )
    
    parser.add_argument(
        "--questions-per-lesson",
        type=int,
        default=QUESTIONS_PER_LESSON,
        help=f"Number of questions to generate per lesson (default: {QUESTIONS_PER_LESSON})"
    )
    
    return parser.parse_args()


@track(name="generate_practice_questions_for_lesson")
def generate_practice_questions(
    lesson_id: str,
    profession: str,
    lesson_data: dict,
    user_profile: dict,
    generator: PracticeQuestionGeneratorAgent,
    reviewer: LessonQuizReviewerAgent,
    rewriter: LessonQuizRewriterAgent,
    questions_per_lesson: int = 10,
    max_rewrites: int = 2
) -> List[PracticeQuestion]:
    """
    Multi-agent pipeline to generate practice questions.
    
    Flow: Generator → Reviewer → [Rewriter if needed] → Validation
    
    Returns:
        List of validated PracticeQuestion objects
    """
    logger.info(f"\n{'='*70}")
    logger.info(f"🎯 Pipeline: {lesson_id} × {profession} ({questions_per_lesson} questions)")
    logger.info(f"{'='*70}")
    
    lesson_objectives = lesson_data.get('what_learners_will_understand', [])
    
    # STAGE 1: Generator
    draft_questions = generator.generate(
        lesson_id=lesson_id,
        profession=profession,
        lesson_objectives=lesson_objectives,
        user_profile=user_profile,
        questions_per_lesson=questions_per_lesson
    )
    
    # STAGE 2: Review Loop
    for attempt in range(max_rewrites + 1):
        logger.info(f"\n📋 Review Cycle {attempt + 1}/{max_rewrites + 1}")
        
        review = reviewer.evaluate(
            quiz_json=draft_questions,
            lesson_id=lesson_id,
            profession=profession,
            lesson_objectives=lesson_objectives,
            expected_question_count=questions_per_lesson
        )
        
        if review.passed:
            logger.info("✅ Questions passed all quality checks!")
            break
        
        if attempt < max_rewrites:
            # STAGE 3: Rewrite
            logger.info(f"🔄 Triggering rewrite (attempt {attempt + 1}/{max_rewrites})")
            draft_questions = rewriter.fix(
                quiz_json=draft_questions,
                issues=review.issues,
                lesson_id=lesson_id,
                profession=profession,
                lesson_objectives=lesson_objectives
            )
        else:
            logger.warning(f"⚠️  Questions did not pass after {max_rewrites} rewrites")
            logger.warning("   Using best attempt (manual review recommended)")
    
    # STAGE 4: Validation
    try:
        validated_questions = [
            PracticeQuestion(**q) 
            for q in draft_questions.get('questions', [])
        ]
        logger.info(f"✅ Validated {len(validated_questions)} questions")
        return validated_questions
    except Exception as e:
        logger.error(f"❌ Validation failed: {e}")
        raise


@track(name="generate_all_practice_questions")
def main():
    """Main execution: Generate practice questions based on arguments."""
    args = parse_args()
    
    logger.info("🎓 Vina Practice Question Generator - Multi-Agent Pipeline")
    logger.info(f"📦 Opik Integration: {'✅ Enabled' if OPIK_AVAILABLE else '❌ Disabled'}")
    logger.info(f"📝 Questions per lesson: {args.questions_per_lesson}\n")
    
    # 1. Load Course Structure
    try:
        config = load_course_config(COURSE_ID)
        all_lessons = config["lessons"]
        
        # Filter lessons if specified
        if args.lessons:
            lesson_ids = [l.strip() for l in args.lessons.split(',')]
            lessons = [l for l in all_lessons if l["lesson_id"] in lesson_ids]
            logger.info(f"✅ Filtered to {len(lessons)} lessons: {lesson_ids}\n")
        else:
            lessons = all_lessons
            logger.info(f"✅ Loaded all {len(lessons)} lessons\n")
            
    except Exception as e:
        logger.error(f"❌ Failed to load course config: {e}")
        return
    
    # 2. Determine Professions
    if args.profession:
        professions = [args.profession]
        logger.info(f"✅ Generating for profession: {args.profession}\n")
    else:
        professions = [p.value for p in Profession]
        logger.info(f"✅ Generating for all {len(professions)} professions\n")
    
    # 3. Load User Profiles
    user_profiles = {}
    for profession in professions:
        try:
            profile = get_or_create_profile(profession)
            user_profiles[profession] = profile
            logger.info(f"✅ Loaded profile: {profession}")
        except Exception as e:
            logger.error(f"❌ Failed to load profile for {profession}: {e}")
            return
    
    logger.info("")
    
    # 4. Initialize Agents
    generator = PracticeQuestionGeneratorAgent()
    reviewer = LessonQuizReviewerAgent()
    rewriter = LessonQuizRewriterAgent()
    
    # 5. Load existing output (if appending)
    output_path = Path(args.output)
    if output_path.exists():
        with open(output_path, 'r') as f:
            final_output = json.load(f)
        logger.info(f"📂 Loaded existing output from {output_path}\n")
    else:
        final_output = {}
        logger.info(f"📂 Creating new output file: {output_path}\n")
    
    # 6. Generate Practice Questions
    total_combinations = len(lessons) * len(professions)
    current = 0
    
    for lesson in lessons:
        lesson_id = lesson["lesson_id"]
        
        if lesson_id not in final_output:
            final_output[lesson_id] = {}
        
        for profession in professions:
            current += 1
            logger.info(f"\n{'#'*70}")
            logger.info(f"# Progress: {current}/{total_combinations}")
            logger.info(f"{'#'*70}")
            
            # Skip if already generated
            if profession in final_output[lesson_id]:
                logger.info(f"⏭️  SKIPPED: {lesson_id} × {profession} (already exists)\n")
                continue
            
            try:
                questions = generate_practice_questions(
                    lesson_id=lesson_id,
                    profession=profession,
                    lesson_data=lesson,
                    user_profile=user_profiles[profession],
                    generator=generator,
                    reviewer=reviewer,
                    rewriter=rewriter,
                    questions_per_lesson=args.questions_per_lesson
                )
                
                final_output[lesson_id][profession] = [q.dict() for q in questions]
                logger.info(f"✅ SUCCESS: {lesson_id} × {profession} ({len(questions)} questions)\n")
                
                # Save incrementally (in case of crashes)
                with open(output_path, 'w') as f:
                    json.dump(final_output, f, indent=2)
                
            except Exception as e:
                logger.error(f"❌ FAILED: {lesson_id} × {profession} - {e}\n")
                continue
    
    # 7. Final Summary
    total_expected = total_combinations * args.questions_per_lesson
    total_generated = sum(
        len(questions)
        for lesson_data in final_output.values()
        for questions in lesson_data.values()
    )
    success_rate = (total_generated / total_expected) * 100 if total_expected > 0 else 0
    
    logger.info(f"\n{'='*70}")
    logger.info(f"🎉 Generation Complete!")
    logger.info(f"{'='*70}")
    logger.info(f"📁 Output: {output_path}")
    logger.info(f"✅ Generated: {total_generated}/{total_expected} questions ({success_rate:.1f}%)")
    logger.info(f"{'='*70}\n")


if __name__ == "__main__":
    main()

Usage Examples:
bash# Generate all 680 questions (17 lessons × 4 professions × 10)
python scripts/generate_practice_questions.py

# Generate for specific lessons only
python scripts/generate_practice_questions.py \
  --lessons "l01_what_llms_are,l02_tokens_context,l03_why_outputs_vary"

# Generate for one profession only
python scripts/generate_practice_questions.py \
  --profession "Clinical Researcher"

# Generate for specific lessons + profession
python scripts/generate_practice_questions.py \
  --lessons "l01_what_llms_are,l02_tokens_context" \
  --profession "HR Manager"

# Custom output location
python scripts/generate_practice_questions.py \
  --output "./custom_practice_questions.json"

# Generate 5 questions per lesson (instead of default 10)
python scripts/generate_practice_questions.py \
  --questions-per-lesson 5

7. API Endpoints
7.1 Get Daily Practice
Endpoint: GET /api/v1/practice/daily
Purpose: Get practice questions for today (or check if already completed)
Request:
httpGET /api/v1/practice/daily?userId=550e8400-e29b-41d4-a716-446655440000
Response (200 OK - Available):
json{
  "status": "available",
  "practiceDate": "2026-02-07",
  "questions": [
    {
      "id": "pq_l01_clinical_01",
      "text": "You're using an LLM to summarize patient adverse events...",
      "options": [
        "A) Context window limitation",
        "B) Hallucination",
        "C) Token prediction error",
        "D) Training data bias"
      ]
    },
    // ... up to 10 questions (no correctAnswer or explanation in response)
  ],
  "maxPoints": 100,
  "pointsPerQuestion": 10
}
Response (200 OK - Already Completed):
json{
  "status": "completed",
  "practiceDate": "2026-02-07",
  "result": {
    "score": 8,
    "total": 10,
    "pointsEarned": 80,
    "checkmarkPattern": "✓✓✓✓✓✓✗✓✗✓"
  },
  "nextResetTime": "2026-02-08T00:00:00Z"
}
Response (403 Forbidden - Locked):
json{
  "status": "locked",
  "reason": "No completed lessons. Complete your first lesson to unlock practice.",
  "completedLessonsCount": 0
}
Backend Logic:
python# src/vina_backend/api/v1/endpoints/practice.py

from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timezone
import random

router = APIRouter()

@router.get("/practice/daily")
async def get_daily_practice(userId: str):
    """
    Get daily practice quiz or status.
    
    Flow:
    1. Get user's completed lessons
    2. Check if practice completed today
    3. If completed: Return results
    4. If available: Generate random questions
    5. If locked: Return locked status
    """
    try:
        # Get user data
        user = await get_user(userId)
        completed_lessons = user.get("completedLessons", [])
        profession = user.get("profession")
        
        # Check if locked (no completed lessons)
        if len(completed_lessons) == 0:
            return {
                "status": "locked",
                "reason": "No completed lessons. Complete your first lesson to unlock practice.",
                "completedLessonsCount": 0
            }
        
        # Get user's local date (timezone-aware)
        user_timezone = user.get("timezone", "UTC")
        user_date = get_current_date_in_timezone(user_timezone)  # e.g., "2026-02-07"
        
        # Check if already completed today
        practice_history = user.get("practiceHistory", {})
        if user_date in practice_history:
            return {
                "status": "completed",
                "practiceDate": user_date,
                "result": practice_history[user_date],
                "nextResetTime": get_next_midnight_utc(user_timezone)
            }
        
        # Generate practice questions
        questions = generate_practice_questions(completed_lessons, profession)
        
        # Remove correctAnswer and explanation (don't send to frontend yet)
        questions_for_frontend = [
            {
                "id": q["id"],
                "text": q["text"],
                "options": [f"{chr(65+i)}) {opt['text']}" for i, opt in enumerate(q["options"])]
            }
            for q in questions
        ]
        
        return {
            "status": "available",
            "practiceDate": user_date,
            "questions": questions_for_frontend,
            "maxPoints": len(questions) * 10,
            "pointsPerQuestion": 10
        }
        
    except Exception as e:
        logger.error(f"Failed to get daily practice: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch practice")


def generate_practice_questions(completed_lessons: List[str], profession: str) -> List[dict]:
    """
    Select random practice questions from completed lessons.
    
    Args:
        completed_lessons: List of lesson IDs user has completed
        profession: User's profession
        
    Returns:
        List of up to 10 random questions
    """
    # Load practice questions
    with open(PRACTICE_QUESTIONS_FILE, 'r') as f:
        practice_questions = json.load(f)
    
    # Build pool
    question_pool = []
    for lesson_id in completed_lessons:
        if lesson_id in practice_questions:
            lesson_questions = practice_questions[lesson_id].get(profession, [])
            question_pool.extend(lesson_questions)
    
    # Random selection
    random.shuffle(question_pool)
    selected = question_pool[:min(10, len(question_pool))]
    
    return selected


def get_current_date_in_timezone(timezone_str: str) -> str:
    """
    Get current date in user's timezone (YYYY-MM-DD format).
    
    Args:
        timezone_str: IANA timezone (e.g., "America/New_York", "Europe/London")
        
    Returns:
        Date string in YYYY-MM-DD format
    """
    from zoneinfo import ZoneInfo
    
    user_tz = ZoneInfo(timezone_str)
    now = datetime.now(user_tz)
    return now.strftime("%Y-%m-%d")


def get_next_midnight_utc(timezone_str: str) -> str:
    """
    Get next midnight in user's timezone as UTC ISO timestamp.
    
    Args:
        timezone_str: IANA timezone
        
    Returns:
        ISO timestamp of next midnight
    """
    from zoneinfo import ZoneInfo
    
    user_tz = ZoneInfo(timezone_str)
    now = datetime.now(user_tz)
    
    # Get tomorrow at midnight in user's timezone
    tomorrow = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    
    # Convert to UTC
    tomorrow_utc = tomorrow.astimezone(timezone.utc)
    
    return tomorrow_utc.isoformat()

7.2 Submit Daily Practice
Endpoint: POST /api/v1/practice/submit
Purpose: Submit practice answers and get results
Request:
json{
  "userId": "550e8400-e29b-41d4-a716-446655440000",
  "practiceDate": "2026-02-07",
  "answers": [
    {
      "questionId": "pq_l01_clinical_01",
      "selectedAnswer": "B",
      "isCorrect": true
    },
    {
      "questionId": "pq_l02_clinical_05",
      "selectedAnswer": "A",
      "isCorrect": false
    }
    // ... up to 10 answers
  ]
}
Response (200 OK):
json{
  "score": 8,
  "total": 10,
  "pointsEarned": 80,
  "checkmarkPattern": "✓✓✓✓✓✓✗✓✗✓",
  "streakExtended": true,
  "nextResetTime": "2026-02-08T00:00:00Z"
}
Backend Logic:
python@router.post("/practice/submit")
async def submit_daily_practice(submission: PracticeSubmission):
    """
    Process practice submission and calculate results.
    
    Flow:
    1. Validate submission
    2. Calculate score
    3. Award points (proportional if <10 questions)
    4. Extend streak
    5. Save to user history
    6. Return results
    """
    try:
        # Calculate score
        score = sum(1 for ans in submission.answers if ans["isCorrect"])
        total = len(submission.answers)
        
        # Award points (proportional)
        points_earned = (score / total) * 100 if total > 0 else 0
        points_earned = round(points_earned / 10) * 10  # Round to nearest 10
        
        # Generate checkmark pattern
        checkmark_pattern = "".join(
            "✓" if ans["isCorrect"] else "✗"
            for ans in submission.answers
        )
        
        # Update user data
        user = await get_user(submission.userId)
        
        # Extend streak
        await update_streak(submission.userId)
        
        # Save practice result
        await save_practice_result(
            user_id=submission.userId,
            date=submission.date,
            result={
                "score": score,
                "total": total,
                "pointsEarned": points_earned,
                "checkmarkPattern": checkmark_pattern
            }
        )
        
        # Award points
        await increment_user_points(submission.userId, points_earned)
        
        # Get next reset time
        user_timezone = user.get("timezone", "UTC")
        next_reset = get_next_midnight_utc(user_timezone)
        
        return PracticeResult(
            score=score,
            total=total,
            pointsEarned=points_earned,
            checkmarkPattern=checkmark_pattern,
            streakExtended=True,
            nextResetTime=next_reset
        )
        
    except Exception as e:
        logger.error(f"Failed to submit practice: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit practice")

8. Frontend Integration Points
8.1 Practice Tab Component
Route: /practice
Component: app/practice/page.tsx
Key States:
typescript// app/practice/page.tsx

'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useProgress } from '@/contexts/ProgressContext';

type PracticeStatus = 'locked' | 'available' | 'in-progress' | 'completed';

export default function PracticePage() {
  const router = useRouter();
  const { progress } = useProgress();
  
  const [status, setStatus] = useState<PracticeStatus>('locked');
  const [questions, setQuestions] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [userAnswers, setUserAnswers] = useState<any[]>([]);
  const [result, setResult] = useState(null);
  const [nextResetTime, setNextResetTime] = useState('');
  
  useEffect(() => {
    checkPracticeStatus();
  }, []);
  
  const checkPracticeStatus = async () => {
    const { userId } = getUserFromLocalStorage();
    const response = await fetch(`/api/v1/practice/daily?userId=${userId}`);
    const data = await response.json();
    
    if (data.status === 'locked') {
      setStatus('locked');
    } else if (data.status === 'completed') {
      setStatus('completed');
      setResult(data.result);
      setNextResetTime(data.nextResetTime);
    } else if (data.status === 'available') {
      setStatus('available');
      setQuestions(data.questions);
    }
  };
  
  const startPractice = () => {
    setStatus('in-progress');
  };
  
  const handleSelectAnswer = (answer: string) => {
    setSelectedAnswer(answer);
    
    // Record answer (we'll validate on backend)
    const newAnswer = {
      questionId: questions[currentQuestionIndex].id,
      selectedAnswer: answer,
      isCorrect: null  // Backend will validate
    };
    setUserAnswers([...userAnswers, newAnswer]);
    
    // Auto-advance after 0.5s
    setTimeout(() => {
      if (currentQuestionIndex < questions.length - 1) {
        setCurrentQuestionIndex(prev => prev + 1);
        setSelectedAnswer(null);
      } else {
        submitPractice();
      }
    }, 500);
  };
  
  const submitPractice = async () => {
    const { userId } = getUserFromLocalStorage();
    const practiceDate = new Date().toISOString().split('T')[0];
    
    // First, validate answers on backend
    const response = await fetch('/api/v1/practice/submit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        userId,
        practiceDate,
        answers: userAnswers
      })
    });
    
    const result = await response.json();
    
    // Update local state
    setResult(result);
    setNextResetTime(result.nextResetTime);
    setStatus('completed');
    
    // Update progress context
    await updateProgress({
      totalPoints: progress.totalPoints + result.pointsEarned,
      lastActiveDate: practiceDate
    });
  };
  
  // Render based on status
  if (status === 'locked') {
    return <LockedState />;
  }
  
  if (status === 'available') {
    return <AvailableState onStart={startPractice} />;
  }
  
  if (status === 'in-progress') {
    return (
      <QuizState
        question={questions[currentQuestionIndex]}
        questionIndex={currentQuestionIndex}
        totalQuestions={questions.length}
        selectedAnswer={selectedAnswer}
        onSelectAnswer={handleSelectAnswer}
      />
    );
  }
  
  if (status === 'completed') {
    return <CompletedState result={result} nextResetTime={nextResetTime} />;
  }
}

8.2 Timezone Detection
Store in LocalStorage on First Visit:
typescript// utils/timezone.ts

export function detectAndStoreTimezone() {
  // Check if already stored
  const stored = localStorage.getItem('vina_timezone');
  if (stored) return stored;
  
  // Detect timezone
  const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
  
  // Store for future use
  localStorage.setItem('vina_timezone', timezone);
  
  // Also send to backend (update user profile)
  updateUserTimezone(timezone);
  
  return timezone;
}

async function updateUserTimezone(timezone: string) {
  const { userId } = getUserFromLocalStorage();
  
  await fetch('/api/v1/user/timezone', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ userId, timezone })
  });
}

// Call on app mount
useEffect(() => {
  detectAndStoreTimezone();
}, []);

8.3 Countdown Timer
Display Time Until Next Reset:
typescript// components/PracticeCountdown.tsx

import { useState, useEffect } from 'react';

export function PracticeCountdown({ nextResetTime }: { nextResetTime: string }) {
  const [timeLeft, setTimeLeft] = useState('');
  
  useEffect(() => {
    const updateCountdown = () => {
      const now = new Date();
      const reset = new Date(nextResetTime);
      const diff = reset.getTime() - now.getTime();
      
      if (diff <= 0) {
        setTimeLeft('Available now!');
        return;
      }
      
      const hours = Math.floor(diff / (1000 * 60 * 60));
      const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
      
      setTimeLeft(`${hours}h ${minutes}m`);
    };
    
    updateCountdown();
    const interval = setInterval(updateCountdown, 60000); // Update every minute
    
    return () => clearInterval(interval);
  }, [nextResetTime]);
  
  return (
    <div className="text-sm text-gray-600">
      ⏰ Next challenge in {timeLeft}
    </div>
  );
}

9. Edge Cases & Error Handling
9.1 User Changes Timezone Mid-Day
Scenario: User completes practice in New York (10am EST), then travels to Los Angeles (7am PST same day)
Behavior:

Practice date is based on UTC date stored when completed
Timezone only affects display of countdown timer
User cannot retake practice until next UTC day (prevents gaming)

Implementation:
python# Backend: Always use UTC date for practice tracking
practice_date_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d")

# Check if practiced today (UTC)
if practice_date_utc in user.practiceHistory:
    return {"status": "completed"}

9.2 User Completes Lessons During Practice
Scenario: User starts practice with 5 completed lessons, then mid-quiz completes lesson 6
Behavior:

Practice quiz continues with original 5-lesson question pool
Next day's practice will include questions from lesson 6

Rationale: Simpler logic, prevents edge cases with question pool changing mid-session

9.3 Practice Fetch Fails
Scenario: Backend returns 500 or timeout
Behavior:

Show error message: "Couldn't load practice. Please try again."
Provide "Retry" button
Don't count as "attempted" (user can retry)

Implementation:
typescriptif (error) {
  return (
    <div className="text-center p-6">
      <p className="text-xl font-semibold mb-2">Oops!</p>
      <p className="text-gray-600 mb-4">Couldn't load practice. Please try again.</p>
      <button onClick={checkPracticeStatus} className="btn-primary">Retry</button>
    </div>
  );
}

9.4 Practice Submit Fails
Scenario: Network error when submitting answers
Behavior:

Show error toast: "Couldn't submit practice. Check your connection."
Preserve answers in component state
Retry button attempts resubmission
Don't lose user's progress

Implementation:
typescriptconst submitPractice = async () => {
  try {
    const response = await fetch('/api/v1/practice/submit', {
      method: 'POST',
      body: JSON.stringify({ userId, answers: userAnswers })
    });
    
    if (!response.ok) throw new Error('Submit failed');
    
    const result = await response.json();
    setResult(result);
    setStatus('completed');
    
  } catch (error) {
    setError('Couldn't submit practice. Check your connection.');
    // userAnswers preserved - can retry
  }
};

9.5 Clock Manipulation
Scenario: User changes device clock to bypass daily limit
Prevention:

Backend uses server time (not client-submitted time)
Practice date calculated server-side
Client timezone only used for display

Backend Validation:
python# Don't trust client-submitted date
practice_date = get_current_date_utc()  # Server-side only

# Check against server-side history
if practice_date in user.practiceHistory:
    return {"status": "completed"}

10. Implementation Checklist
10.1 Backend Tasks
Phase 1: Question Generation (Day 1-2)

 Update PracticeQuestionGeneratorAgent with new prompt template
 Ensure 10 questions per lesson (not 3)
 Create generate_practice_questions.py script with CLI arguments
 Test on 1 lesson × 1 profession (validate quality)
 Run full generation: 680 questions (17 × 4 × 10)
 Save to practice_questions.json
 Manual review of 10-15 sample questions

Phase 2: API Development (Day 2)

 Create GET /api/v1/practice/daily endpoint
 Create POST /api/v1/practice/submit endpoint
 Implement question selection algorithm (random from completed lessons)
 Implement timezone detection and storage
 Implement daily reset logic (midnight user's local time)
 Add scoring logic (proportional points)
 Add streak extension logic
 Test endpoints with Postman

Phase 3: Database/Storage (Day 2-3)

 Add timezone field to user profile
 Add practiceHistory field to user data: {date: {score, total, points, checkmarks}}
 Add practice result saving logic
 Test data persistence


10.2 Frontend Tasks
Phase 1: Practice Tab (Day 2-3)

 Create /practice/page.tsx
 Implement locked state UI
 Implement available state UI (with start button)
 Implement quiz UI (no feedback during quiz)
 Implement completed state UI (with checkmark pattern)
 Add timezone detection on app mount
 Store timezone in LocalStorage

Phase 2: Quiz Flow (Day 3)

 Fetch practice questions from API
 Display questions one at a time
 Handle answer selection (no visual feedback)
 Auto-advance after 0.5s
 Submit answers to backend
 Navigate to results

Phase 3: Results & Polish (Day 3)

 Display score and checkmark pattern
 Display points earned
 Display countdown timer to next reset
 Update ProgressContext (points, streak)
 Add error handling (fetch fails, submit fails)
 Mobile responsive testing

Phase 4: Bottom Nav Integration (Day 3)

 Add badge indicator on Practice tab when available
 Remove badge after completion
 Test tab switching behavior


10.3 Testing Checklist
Unit Tests:

 Question selection returns correct count (up to 10)
 Proportional scoring works correctly (8/10 = 80 pts)
 Timezone conversion accurate
 Daily reset logic correct

Integration Tests:

 Practice unlocks after first lesson completion
 Questions come from completed lessons only
 Can't retake practice on same day
 Streak extends on practice completion
 Points awarded correctly

End-to-End Tests:

 User completes lesson → Practice unlocks
 User takes practice → Sees results
 User returns next day → Practice available again
 User with 0 lessons → Locked state shown
 User with 1 lesson → Gets ≤10 questions

Edge Cases:

 Browser close during practice → Can retry
 Practice fetch fails → Error shown
 Practice submit fails → Retry works
 User changes timezone → Countdown accurate


10.4 Deployment Checklist
Pre-Deploy:

 All 680 practice questions generated and committed
 Backend API tested and working
 Frontend UI tested on mobile + desktop
 Timezone detection working
 Error handling verified

Deploy:

 Push backend to Railway
 Push frontend to Vercel
 Test production API endpoints
 Verify practice unlocking in production
 Monitor logs for errors

Post-Deploy:

 Test full user flow in production
 Monitor daily reset timing
 Check error rates
 Collect user feedback