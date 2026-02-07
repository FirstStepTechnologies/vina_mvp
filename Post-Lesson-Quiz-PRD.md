Post-Lesson Quiz Feature - Product Requirements Document
Version: 1.0
Last Updated: February 7, 2026
Status: Ready for Implementation
Target: Vina Backend - Lesson Quiz Generation System

Table of Contents

Executive Summary
Feature Overview
User Experience Flow
Quiz Specifications
Data Models
Multi-Agent Generation Pipeline
API Endpoints
Frontend Integration Points
Edge Cases & Error Handling
Implementation Checklist


1. Executive Summary
1.1 Purpose
The post-lesson quiz feature validates learner comprehension after each video lesson and provides adaptive pathways based on performance. Quizzes are:

Educational: Reinforce concepts through active recall with immediate feedback
Optional: Users can skip to maintain engagement flexibility
Adaptive: Failed quizzes offer pathways to review, simplify, or continue
Profession-specific: Questions tailored to each learner's professional context

1.2 Success Metrics

Engagement: 70%+ of users attempt quiz (vs. skip)
Quality: 90%+ quiz pass rate (indicates appropriate difficulty)
Completion: Quiz completion adds 5-10% to lesson completion rates
Adaptation: 20%+ of users who fail choose "Try Simpler Version"

1.3 Scope
In Scope:

Generate 68 quizzes (17 lessons × 4 professions) using multi-agent pipeline
Store quizzes in database for instant retrieval
Frontend quiz UI with immediate feedback
Pass/fail logic with adaptive options
Skip quiz functionality

Out of Scope (Future Enhancements):

Cumulative knowledge questions (saved for Daily Practice)
Multi-select question types
Timed quizzes
Quiz leaderboards
Question randomization (always same 3 questions per lesson/profession)


2. Feature Overview
2.1 When Quiz Appears
User Journey:
1. User watches lesson video (L05: Hallucinations)
2. Video ends (onEnded event)
3. Frontend navigates to /quiz/{lessonId}
4. Quiz screen loads with 2 options:
   - [Take Quiz] (primary button)
   - [Skip Quiz] (small text link, less prominent)
2.2 Core Behavior
ActionOutcomePointsStreakNext LessonSkip QuizLesson marked "Completed (Unverified)"+10MaintainedUnlockedPass Quiz (2/3 or 3/3)Lesson marked "Completed"+20 or +30Maintained/IncrementedUnlockedFail Quiz (0/3 or 1/3)Lesson remains "Active"+0MaintainedLockedFail → Skip to NextLesson marked "Completed (Unverified)"+10MaintainedUnlocked
2.3 Design Philosophy

Low Stakes: Users can skip or proceed even on failure (no hard gating)
High Support: Immediate feedback with explanations reinforces learning
Adaptive Pathways: Failure offers 3 clear options (review, simplify, or continue)
Profession-First: Questions reference learner's actual work context


3. User Experience Flow
3.1 Happy Path: User Passes Quiz
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: Video Ends                                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ✅ Lesson complete!                                        │
│                                                             │
│  Ready to test your knowledge?                              │
│                                                             │
│  [Take Quiz →]     (primary button, teal)                   │
│                                                             │
│  Skip Quiz         (small text link, gray)                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘

User taps "Take Quiz" ↓

┌─────────────────────────────────────────────────────────────┐
│ STEP 2: Question 1                                          │
├─────────────────────────────────────────────────────────────┤
│  Quiz: L05 Hallucinations                                   │
│  Question 1 of 3                    ●○○                     │
│                                                             │
│  In clinical research, which scenario poses the highest     │
│  risk when using LLMs?                                      │
│                                                             │
│  ○ A) Summarizing published literature for a review         │
│                                                             │
│  ○ B) Generating adverse event reports from raw data        │
│                                                             │
│  ○ C) Drafting initial protocol outlines                    │
│                                                             │
│  ○ D) Creating meeting agendas for team discussions         │
│                                                             │
└─────────────────────────────────────────────────────────────┘

User selects Option B ↓

┌─────────────────────────────────────────────────────────────┐
│ STEP 3: Immediate Feedback (Correct)                        │
├─────────────────────────────────────────────────────────────┤
│  ✅ Correct!                                                │
│                                                             │
│  ● B) Generating adverse event reports from raw data        │
│    [Green border, green background tint]                    │
│                                                             │
│  Explanation:                                               │
│  Adverse event reports directly impact patient safety and   │
│  regulatory compliance. Hallucinations in this context      │
│  could lead to serious harm or incorrect filings.           │
│                                                             │
│  [Next Question →]    (appears after 1 second)              │
│                                                             │
└─────────────────────────────────────────────────────────────┘

[Repeat for Q2, Q3 with same instant feedback pattern]

User completes all 3 questions (gets 3/3 correct) ↓

┌─────────────────────────────────────────────────────────────┐
│ STEP 4: Results Screen (Pass)                               │
├─────────────────────────────────────────────────────────────┤
│                     🎉                                      │
│              Lesson Complete!                               │
│                                                             │
│           You got 3/3 correct                               │
│                                                             │
│           +30 points 💎                                     │
│           🔥 5 day streak                                   │
│                                                             │
│                                                             │
│           [Continue Learning →]                             │
│                                                             │
│           [Review Lesson]                                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘

User taps "Continue Learning" ↓
→ Navigate to /course-map
→ Lesson 05 shows checkmark (completed)
→ Lesson 06 is now active (unlocked)
→ LocalStorage updated with score, points, streak

3.2 Alternative Path: User Fails Quiz
[Same Q1-Q3 flow, but user gets 1/3 correct]

┌─────────────────────────────────────────────────────────────┐
│ STEP 4: Results Screen (Fail)                               │
├─────────────────────────────────────────────────────────────┤
│                     📚                                      │
│              Let's Review                                   │
│                                                             │
│           You got 1/3 correct                               │
│                                                             │
│           No worries! Learning takes time.                  │
│           Choose how you'd like to proceed:                 │
│                                                             │
│           [Re-watch Lesson]                                 │
│                                                             │
│           [Try Simpler Version]                             │
│                                                             │
│           [Skip to Next Lesson]                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘

Option 1: User taps "Re-watch Lesson"
→ Navigate to /lesson/{lessonId}
→ Video plays at same difficulty
→ After video: Quiz appears again (fresh attempt)

Option 2: User taps "Try Simpler Version"
→ Trigger adaptation: POST /api/v1/lessons/adapt
   { lessonId, adaptationType: "simplify_this", userId }
→ Load simplified video (difficulty 1)
→ After video: Quiz appears (same questions, standard difficulty)

Option 3: User taps "Skip to Next Lesson"
→ Mark lesson "Completed (Unverified)" in LocalStorage
→ Award +10 points (participation credit)
→ Streak maintained
→ Next lesson unlocks
→ Navigate to /course-map

3.3 Alternative Path: User Skips Quiz
[Video ends, quiz screen appears]

User taps "Skip Quiz" (small text link) ↓

┌─────────────────────────────────────────────────────────────┐
│ Confirmation Dialog (Optional)                              │
├─────────────────────────────────────────────────────────────┤
│  Skip the quiz?                                             │
│                                                             │
│  You'll earn 10 points and the next lesson will unlock,     │
│  but you won't verify your understanding.                   │
│                                                             │
│  [Yes, Skip]        [No, Take Quiz]                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘

User confirms "Yes, Skip" ↓
→ Mark lesson "Completed (Unverified)" in LocalStorage
→ Award +10 points
→ Streak maintained (video completion counts)
→ Next lesson unlocks
→ Navigate to /course-map
→ Lesson 05 shows checkmark (completed, but no quiz badge)

4. Quiz Specifications
4.1 Question Structure
Fixed Parameters:

Number of questions: Exactly 3 per lesson
Question type: Multiple choice, single answer
Options per question: Exactly 4 (A, B, C, D)
Retry policy: No retries on individual questions (answer locked after selection)
Time limit: None (take as long as needed)

Difficulty:

Quiz difficulty: Always at lesson's base difficulty (not tied to video difficulty variant)
Rationale: Lesson objectives remain constant; simplified/advanced videos teach same concepts differently
Example: User watches "simplified" version of L05 → Takes standard L05 quiz (not an easier quiz)

Content Scope:

Concept coverage: Only content taught in THIS lesson (no cumulative questions)
Profession-specific: Questions reference learner's profession in scenarios
Example: Clinical Researcher sees different questions than Marketing Manager for same lesson

4.2 Passing Criteria
ScoreResultPoints AwardedFeedback3/3 correctPass (Perfect)+30 points"Excellent! You got 3/3 correct"2/3 correctPass (Good)+20 points"Well done! You got 2/3 correct"1/3 correctFail+0 points"You got 1/3 correct. Let's review."0/3 correctFail+0 points"You got 0/3 correct. Let's review."
Pass Threshold: 2/3 (67%) or higher
4.3 Feedback Mechanism
Timing: Immediate feedback after each question (not at end)
Feedback Components:

Visual Indicator:

Correct: Green border + light green background on selected option
Incorrect: Red border + light red background on selected option
Icon: ✅ "Correct!" or ❌ "Not quite"


Explanation Text:

Always shown (for both correct and incorrect answers)
Length: 2-3 sentences
Tone: Educational, not judgmental
Content: Explains WHY the correct answer is right (not just restating it)


Auto-Advance:

Wait 1 second after answer selection
"Next Question" button appears
User taps to proceed to next question



Example Feedback (Correct):
✅ Correct!

● B) Generating adverse event reports from raw data
  [Green border]

Explanation:
Adverse event reports directly impact patient safety and regulatory 
compliance. Hallucinations in this context could lead to serious harm 
or incorrect filings.

[Next Question →]
Example Feedback (Incorrect):
❌ Not quite

● A) Summarizing published literature for a review
  [Red border]

Explanation:
While accuracy matters in literature reviews, the highest risk scenario 
is generating adverse event reports (Option B), where hallucinations 
could directly harm patient safety.

[Next Question →]
4.4 Question Quality Requirements
Each question must meet these criteria (enforced by Reviewer Agent):

Scenario-based: Questions pose realistic work situations, not abstract definitions
Profession-specific context: Reference learner's actual job tasks
Single concept: Each question tests ONE core LLM concept from the lesson
Plausible distractors: Wrong answers are common misconceptions (not obvious throwaways)
Unambiguous correct answer: Only ONE option is clearly correct
Educational explanation: Explanation teaches, not just confirms

Bad Question (Abstract):
What is a hallucination in LLMs?
A) When the model generates incorrect information
B) When the model refuses to answer
C) When the model is too slow
D) When the model uses too many tokens
Good Question (Scenario-based, Profession-specific):
You're drafting a clinical trial protocol using an LLM. The model 
confidently cites a 2023 study that doesn't exist. This is an example of:

A) Context window limitation
B) Hallucination
C) Token prediction error
D) Bias in training data

5. Data Models
5.1 Pydantic Schemas
python# src/vina_backend/domain/schemas/lesson_quiz.py

from typing import List, Optional
from pydantic import BaseModel, Field, validator

class QuizOption(BaseModel):
    """Single answer option for a quiz question."""
    text: str = Field(
        ..., 
        description="Option text WITHOUT letter prefix (frontend adds A/B/C/D)"
    )
    is_correct: bool = Field(
        ..., 
        description="Whether this is the correct answer"
    )

class LessonQuizQuestion(BaseModel):
    """Single question in a post-lesson quiz."""
    
    id: str = Field(
        ..., 
        description="Question ID (e.g., 'q1', 'q2', 'q3')"
    )
    
    text: str = Field(
        ..., 
        description="Question text (scenario-based, profession-specific)",
        min_length=20
    )
    
    options: List[QuizOption] = Field(
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
        description="User-facing explanation (2-3 sentences) of why correct answer is right",
        min_length=50
    )
    
    conceptTested: str = Field(
        ..., 
        description="Core LLM concept tested (e.g., 'hallucinations', 'context_windows')"
    )
    
    rationale: str = Field(
        ..., 
        description="Internal note on pedagogical intent (for reviewers/developers)"
    )
    
    @validator('options')
    def validate_exactly_one_correct(cls, v):
        """Ensure exactly one option is marked correct."""
        correct_count = sum(1 for opt in v if opt.is_correct)
        if correct_count != 1:
            raise ValueError(f"Expected exactly 1 correct answer, found {correct_count}")
        return v
    
    @validator('correctAnswer')
    def validate_correct_answer_matches(cls, v, values):
        """Ensure correctAnswer letter matches the is_correct option."""
        if 'options' not in values:
            return v
        
        letter_map = {0: 'A', 1: 'B', 2: 'C', 3: 'D'}
        correct_index = next(
            (i for i, opt in enumerate(values['options']) if opt.is_correct), 
            None
        )
        
        if correct_index is None:
            raise ValueError("No option marked as correct")
        
        expected_letter = letter_map[correct_index]
        if v != expected_letter:
            raise ValueError(
                f"correctAnswer is '{v}' but option at index {correct_index} "
                f"is marked correct (expected '{expected_letter}')"
            )
        
        return v


class LessonQuiz(BaseModel):
    """Complete quiz for a lesson (profession-specific)."""
    
    lessonId: str = Field(
        ..., 
        description="Lesson ID (e.g., 'l05_hallucinations')",
        regex="^l\\d{2}_[a-z_]+$"
    )
    
    profession: str = Field(
        ..., 
        description="Target profession (e.g., 'Clinical Researcher')"
    )
    
    questions: List[LessonQuizQuestion] = Field(
        ..., 
        min_items=3, 
        max_items=3,
        description="Exactly 3 questions"
    )
    
    passThreshold: int = Field(
        default=2, 
        description="Number of correct answers required to pass (2/3)"
    )
    
    @validator('questions')
    def validate_unique_concepts(cls, v):
        """Ensure each question tests a different concept."""
        concepts = [q.conceptTested for q in v]
        if len(concepts) != len(set(concepts)):
            duplicates = [c for c in concepts if concepts.count(c) > 1]
            raise ValueError(f"Questions test duplicate concepts: {duplicates}")
        return v


class QuizSubmission(BaseModel):
    """User's quiz submission."""
    
    lessonId: str
    userId: str
    answers: List[dict] = Field(
        ...,
        description="List of {questionId, selectedAnswer, isCorrect}"
    )
    
    @validator('answers')
    def validate_answer_count(cls, v):
        """Ensure exactly 3 answers submitted."""
        if len(v) != 3:
            raise ValueError(f"Expected 3 answers, got {len(v)}")
        return v


class QuizResult(BaseModel):
    """Result after quiz submission."""
    
    score: int = Field(..., ge=0, le=3, description="Number of correct answers")
    total: int = Field(default=3, description="Total questions")
    passed: bool = Field(..., description="Whether user passed (score >= 2)")
    pointsEarned: int = Field(..., description="Points awarded (0, 20, or 30)")
    feedback: str = Field(..., description="Encouragement message")
    
    # Optional: Next lesson info (if passed)
    nextLessonId: Optional[str] = Field(None, description="Next lesson to unlock")


class ReviewResult(BaseModel):
    """Result of Reviewer Agent evaluation."""
    
    passed: bool = Field(
        ..., 
        description="True if quiz meets all quality standards"
    )
    
    issues: List[str] = Field(
        default_factory=list, 
        description="Specific problems found (empty if passed)"
    )
    
    score_breakdown: dict = Field(
        default_factory=dict, 
        description="Scores for each quality dimension"
    )
```

---

## 6. Multi-Agent Generation Pipeline

### 6.1 Architecture Overview
```
┌─────────────────────────────────────────────────────────────┐
│         LESSON QUIZ GENERATION PIPELINE                     │
│                                                             │
│  Input: Lesson ID + Profession                             │
│  Output: Validated LessonQuiz (3 questions)                │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ STAGE 1: GENERATOR AGENT                              │ │
│  │                                                        │ │
│  │ • Reads lesson learning objectives from course config │ │
│  │ • Reads user profile (profession, responsibilities)   │ │
│  │ • Generates 3 profession-specific questions           │ │
│  │ • Each question tests unique concept from lesson      │ │
│  │                                                        │ │
│  │ Output: Draft quiz (raw JSON)                         │ │
│  └───────────────────────────────────────────────────────┘ │
│                           ↓                                 │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ STAGE 2: REVIEWER AGENT                               │ │
│  │                                                        │ │
│  │ Quality Rubric:                                       │ │
│  │ ✓ Scenario-based questions (not abstract)            │ │
│  │ ✓ Profession-specific context used correctly         │ │
│  │ ✓ Each question tests different concept              │ │
│  │ ✓ Exactly 1 correct answer per question              │ │
│  │ ✓ Distractors are plausible (not obvious)            │ │
│  │ ✓ Explanations are educational (not just restatement)│ │
│  │ ✓ Questions align with lesson objectives             │ │
│  │                                                        │ │
│  │ Output: Pass/Fail + Issues list                       │ │
│  └───────────────────────────────────────────────────────┘ │
│                           ↓                                 │
│              ┌─────────────────────┐                        │
│              │   Passed?           │                        │
│              └─────────────────────┘                        │
│                 Yes ↓         ↓ No (up to 2 retries)        │
│                     │         │                             │
│  ┌──────────────────┘         └────────────────────────┐   │
│  │                                                      │   │
│  │                  ┌───────────────────────────────┐  │   │
│  │                  │ STAGE 3: REWRITER AGENT       │  │   │
│  │                  │                               │  │   │
│  │                  │ • Receives specific issues    │  │   │
│  │                  │ • Fixes problems minimally    │  │   │
│  │                  │ • Preserves good questions    │  │   │
│  │                  │                               │  │   │
│  │                  │ Output: Revised quiz          │  │   │
│  │                  └───────────────────────────────┘  │   │
│  │                           ↓                          │   │
│  │                  (Return to Reviewer)                │   │
│  │                                                      │   │
│  └──────────────────────────────────────────────────────┘   │
│                           ↓                                 │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ STAGE 4: FINAL VALIDATION                            │ │
│  │                                                        │ │
│  │ • Pydantic schema validation                          │ │
│  │ • Store in database: lesson_quizzes table            │ │
│  │ • Cache key: (lessonId, profession)                  │ │
│  │                                                        │ │
│  │ Output: Validated LessonQuiz ready for API           │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
6.2 Generator Agent
File: src/vina_backend/services/agents/lesson_quiz_generator.py
Responsibilities:

Generate initial quiz questions based on lesson content
Ensure profession-specific context in scenarios
Create plausible distractors (wrong answers)
Write educational explanations

Inputs:
python{
  "lessonId": "l05_hallucinations",
  "profession": "Clinical Researcher",
  "lessonObjectives": [
    "Understand what hallucinations are in LLMs",
    "Identify high-risk scenarios in clinical research",
    "Learn mitigation strategies"
  ],
  "userProfile": {
    "dailyResponsibilities": [...],
    "typicalOutputs": [...],
    "painPoints": [...]
  }
}
```

**Prompt Template:**
```
You are a **Master Quiz Designer** for professional education.

Your task: Create a 3-question quiz for Lesson 05 (Hallucinations) 
tailored to a **Clinical Researcher**.

**Lesson Objectives (The Truth):**
{lesson_objectives}

**Learner Profile:**
{user_profile_summary}

**Quiz Design Requirements:**

1. **Question Structure:**
   - Q1: Tests basic understanding (Can identify what a hallucination is)
   - Q2: Tests application (Can recognize hallucination in work scenario)
   - Q3: Tests strategy (Can choose appropriate mitigation)

2. **Profession-Specific Context:**
   - Every question must reference Clinical Researcher's actual work
   - Use terminology from their domain (protocols, adverse events, regulatory compliance)
   - Scenarios should feel like real situations they'd encounter

3. **Distractor Design:**
   - Wrong answers should be common misconceptions (not random nonsense)
   - Make distractors plausible enough that someone who half-understands would pick them
   - Example: "Hallucinations happen because LLMs access outdated databases" 
     (plausible but wrong - LLMs don't access databases)

4. **Explanation Quality:**
   - Don't just restate the correct answer
   - Explain WHY it's correct AND why it matters to Clinical Researchers
   - 2-3 sentences, educational tone

5. **Concept Coverage:**
   - Each question must test a DIFFERENT concept from the lesson
   - Q1: Definition/recognition
   - Q2: Application/risk awareness
   - Q3: Mitigation/strategy

**Output Format:**
Return valid JSON matching this schema:
{
  "lessonId": "l05_hallucinations",
  "profession": "Clinical Researcher",
  "questions": [
    {
      "id": "q1",
      "text": "You're using an LLM to summarize patient records...",
      "options": [
        {"text": "Option A text", "is_correct": false},
        {"text": "Correct option", "is_correct": true},
        {"text": "Option C text", "is_correct": false},
        {"text": "Option D text", "is_correct": false}
      ],
      "correctAnswer": "B",
      "explanation": "Educational explanation...",
      "conceptTested": "hallucination_definition",
      "rationale": "Tests if learner can identify hallucinations in clinical context"
    },
    // Q2, Q3...
  ],
  "passThreshold": 2
}

**CRITICAL:** 
- Ensure exactly 3 questions
- Ensure each question has exactly 4 options
- Ensure exactly 1 option has is_correct: true
- Ensure correctAnswer letter matches the correct option's position
Implementation:
python# src/vina_backend/services/agents/lesson_quiz_generator.py

import logging
from typing import Dict, Any
from vina_backend.integrations.llm.client import get_llm_client
from vina_backend.services.course_loader import load_course_config

logger = logging.getLogger(__name__)

GENERATOR_PROMPT = """
[Full prompt template from above]
"""

class LessonQuizGeneratorAgent:
    """Agent responsible for generating initial lesson quiz drafts."""
    
    def __init__(self):
        self.llm = get_llm_client()
    
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
        
        prompt = GENERATOR_PROMPT.format(
            lesson_id=lesson_id,
            profession=profession,
            lesson_objectives=objectives_str,
            user_profile_summary=profile_str
        )
        
        try:
            quiz_json = self.llm.generate_json(
                prompt,
                temperature=0.7,  # Creative scenarios
                max_tokens=2500
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
```

---

### 6.3 Reviewer Agent

**File:** `src/vina_backend/services/agents/lesson_quiz_reviewer.py`

**Responsibilities:**
- Evaluate quiz quality against rubric
- Flag specific issues (not just pass/fail)
- Ensure questions align with lesson objectives
- Validate profession-specific context usage

**Quality Rubric:**

| Dimension | Pass Criteria | Common Issues |
|-----------|---------------|---------------|
| **Scenario-Based** | All questions pose realistic work scenarios | Abstract "What is X?" questions |
| **Profession Context** | Questions reference learner's actual job tasks | Generic examples not tied to profession |
| **Concept Diversity** | Each question tests different concept | Q2 and Q3 both test same thing |
| **Answer Quality** | Exactly 1 correct answer, 3 plausible distractors | Obvious wrong answers, multiple correct answers |
| **Explanation Quality** | Explanations teach, not just restate | "The answer is B because B is correct" |
| **Alignment** | Questions test concepts from THIS lesson only | Questions test previous lesson or unrelated topics |

**Prompt Template:**
```
You are a **Quality Assurance Expert** for educational assessments.

Evaluate this lesson quiz against professional standards.

**Quiz Being Reviewed:**
```json
{quiz_json}
```

**Lesson Context:**
- Lesson ID: {lesson_id}
- Profession: {profession}
- Learning Objectives: {lesson_objectives}

**Quality Rubric:**

1. **Scenario-Based Questions (CRITICAL)**
   - Questions must pose realistic work scenarios, not abstract definitions
   - Check: Do questions feel like real situations the learner would encounter?
   - FAIL if: Any question is "What is...?" or "Define..." format

2. **Profession-Specific Context**
   - Questions must reference {profession}'s actual job tasks
   - Check: Do scenarios use domain terminology? (e.g., "protocols", "adverse events")
   - FAIL if: Questions could apply to any profession (too generic)

3. **Concept Diversity**
   - Each question must test a DIFFERENT concept from the lesson
   - Check: Are conceptTested values unique across all 3 questions?
   - FAIL if: Two questions test the same thing

4. **Answer Quality**
   - Exactly 1 correct answer per question
   - Wrong answers (distractors) must be plausible misconceptions
   - Check: Would someone who half-understands the lesson pick a wrong answer?
   - FAIL if: Wrong answers are obviously silly, or multiple answers seem correct

5. **Explanation Quality**
   - Explanations must TEACH, not just restate the answer
   - Must be 2-3 sentences with reasoning
   - Check: Does explanation explain WHY the answer is correct?
   - FAIL if: Explanation is circular ("B is correct because it's the right answer")

6. **Lesson Alignment**
   - Questions must only test concepts taught in THIS lesson
   - Check: Do questions match the learning objectives?
   - FAIL if: Questions test unrelated topics or assume prior knowledge not covered

**Your Task:**
Evaluate the quiz. Return JSON:

{
  "passed": true/false,
  "issues": [
    "Q2: Not scenario-based - asks 'What is a hallucination?' instead of posing a work scenario",
    "Q3: Explanation just restates answer without explaining WHY"
  ],
  "score_breakdown": {
    "scenario_based": "pass/fail",
    "profession_context": "pass/fail",
    "concept_diversity": "pass/fail",
    "answer_quality": "pass/fail",
    "explanation_quality": "pass/fail",
    "lesson_alignment": "pass/fail"
  }
}

**Decision Logic:**
- If ALL dimensions pass → "passed": true, "issues": []
- If ANY dimension fails → "passed": false, "issues": [specific problems]

Be rigorous. Focus on issues that would confuse learners or break the learning experience.
Implementation:
python# src/vina_backend/services/agents/lesson_quiz_reviewer.py

import logging
from typing import Dict, Any
from vina_backend.integrations.llm.client import get_llm_client
from vina_backend.domain.schemas.lesson_quiz import ReviewResult

logger = logging.getLogger(__name__)

REVIEWER_PROMPT = """
[Full prompt template from above]
"""

class LessonQuizReviewerAgent:
    """Agent responsible for evaluating lesson quiz quality."""
    
    def __init__(self):
        self.llm = get_llm_client()
    
    def evaluate(
        self, 
        quiz_json: Dict[str, Any],
        lesson_id: str,
        profession: str,
        lesson_objectives: list
    ) -> ReviewResult:
        """
        Evaluate quiz quality against rubric.
        
        Args:
            quiz_json: Raw quiz JSON to evaluate
            lesson_id: Lesson ID for context
            profession: Target profession
            lesson_objectives: Learning objectives for alignment check
            
        Returns:
            ReviewResult with pass/fail and issues
        """
        logger.info(f"🔍 Reviewer: Evaluating {lesson_id} ({profession})")
        
        import json
        quiz_str = json.dumps(quiz_json, indent=2)
        objectives_str = "\n".join(f"- {obj}" for obj in lesson_objectives)
        
        prompt = REVIEWER_PROMPT.format(
            quiz_json=quiz_str,
            lesson_id=lesson_id,
            profession=profession,
            lesson_objectives=objectives_str
        )
        
        try:
            review_json = self.llm.generate_json(
                prompt,
                temperature=0.2,  # Low temp for consistent evaluation
                max_tokens=1000
            )
            
            result = ReviewResult(**review_json)
            
            if result.passed:
                logger.info("   ✅ Quiz PASSED review")
            else:
                logger.warning(f"   ❌ Quiz FAILED - Issues: {len(result.issues)}")
                for issue in result.issues:
                    logger.warning(f"      • {issue}")
            
            return result
            
        except Exception as e:
            logger.error(f"   ❌ Review failed: {e}")
            raise
```

---

### 6.4 Rewriter Agent

**File:** `src/vina_backend/services/agents/lesson_quiz_rewriter.py`

**Responsibilities:**
- Fix specific issues flagged by Reviewer
- Preserve questions that are already good
- Make minimal changes (surgical fixes, not complete rewrites)

**Prompt Template:**
```
You are a **Quiz Improvement Specialist**.

A quiz has failed quality review. Your job is to FIX the specific issues.

**Original Quiz:**
```json
{quiz_json}
```

**Issues Identified:**
{issues}

**Context:**
- Lesson: {lesson_id}
- Profession: {profession}
- Learning Objectives: {lesson_objectives}

**Your Task:**
Fix ALL the issues listed above while preserving:
- Questions that weren't flagged (keep them unchanged)
- The 3-question structure
- The profession-specific context
- The lesson alignment

**Instructions:**
1. For each issue, make the MINIMAL change needed to fix it
2. Don't rewrite questions that passed review
3. If a question is "not scenario-based", convert it to a realistic work scenario
4. If an explanation is weak, enhance it with educational reasoning
5. If distractors are obvious, replace them with plausible misconceptions

Return the COMPLETE revised quiz in the same JSON format.
Implementation:
python# src/vina_backend/services/agents/lesson_quiz_rewriter.py

import logging
from typing import Dict, Any, List
from vina_backend.integrations.llm.client import get_llm_client

logger = logging.getLogger(__name__)

REWRITER_PROMPT = """
[Full prompt template from above]
"""

class LessonQuizRewriterAgent:
    """Agent responsible for fixing lesson quiz issues."""
    
    def __init__(self):
        self.llm = get_llm_client()
    
    def fix(
        self, 
        quiz_json: Dict[str, Any],
        issues: List[str],
        lesson_id: str,
        profession: str,
        lesson_objectives: list
    ) -> Dict[str, Any]:
        """
        Fix issues in a quiz that failed review.
        
        Args:
            quiz_json: Original quiz JSON
            issues: List of specific problems to fix
            lesson_id: Lesson ID for context
            profession: Target profession
            lesson_objectives: Learning objectives for alignment
            
        Returns:
            Revised quiz JSON
        """
        logger.info(f"🔧 Rewriter: Fixing {len(issues)} issues")
        
        import json
        quiz_str = json.dumps(quiz_json, indent=2)
        issues_str = "\n".join(f"- {issue}" for issue in issues)
        objectives_str = "\n".join(f"- {obj}" for obj in lesson_objectives)
        
        prompt = REWRITER_PROMPT.format(
            quiz_json=quiz_str,
            issues=issues_str,
            lesson_id=lesson_id,
            profession=profession,
            lesson_objectives=objectives_str
        )
        
        try:
            fixed_quiz = self.llm.generate_json(
                prompt,
                temperature=0.5,  # Moderate creativity for fixes
                max_tokens=2500
            )
            
            logger.info("   ✅ Quiz rewritten")
            return fixed_quiz
            
        except Exception as e:
            logger.error(f"   ❌ Rewrite failed: {e}")
            raise
```

---

### 6.5 Main Orchestration Script

**File:** `scripts/generate_lesson_quizzes.py`

**Purpose:** Pre-generate all 68 lesson quizzes (17 lessons × 4 professions)

**Execution Flow:**
```
1. Load course config (get all 17 lessons + objectives)
2. Load user profiles (4 professions)
3. For each (lesson, profession) combination:
   a. Generator creates quiz
   b. Reviewer evaluates (up to 2 retries)
   c. Rewriter fixes if needed
   d. Validate with Pydantic
   e. Store in database
4. Generate report (success rate, common issues)
Implementation:
python# scripts/generate_lesson_quizzes.py

import json
import logging
import sys
from pathlib import Path
from typing import Dict, Any, List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from vina_backend.services.agents.lesson_quiz_generator import LessonQuizGeneratorAgent
from vina_backend.services.agents.lesson_quiz_reviewer import LessonQuizReviewerAgent
from vina_backend.services.agents.lesson_quiz_rewriter import LessonQuizRewriterAgent
from vina_backend.services.course_loader import load_course_config
from vina_backend.services.profile_builder import get_or_create_profile
from vina_backend.domain.schemas.lesson_quiz import LessonQuiz
from vina_backend.domain.constants.enums import Profession
from vina_backend.utils.logging import setup_logging

# Optional: Opik integration
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
logger = logging.getLogger("LESSON_QUIZ_PIPELINE")

COURSE_ID = "c_llm_foundations"
OUTPUT_FILE = Path(__file__).parent.parent / "src/vina_backend/domain/constants/lesson_quizzes.json"

# Get professions from enums
TARGET_PROFESSIONS = [p.value for p in Profession]


@track(name="generate_quiz_for_lesson")
def generate_quiz_for_lesson(
    lesson_id: str,
    profession: str,
    lesson_data: dict,
    user_profile: dict,
    generator: LessonQuizGeneratorAgent,
    reviewer: LessonQuizReviewerAgent,
    rewriter: LessonQuizRewriterAgent,
    max_rewrites: int = 2
) -> LessonQuiz:
    """
    Multi-agent pipeline to generate high-quality lesson quiz.
    
    Flow: Generator → Reviewer → [Rewriter if needed] → Validation
    
    Args:
        lesson_id: Lesson ID (e.g., "l05_hallucinations")
        profession: Target profession
        lesson_data: Lesson metadata from course config
        user_profile: User profile data for contextualization
        generator: Generator agent instance
        reviewer: Reviewer agent instance
        rewriter: Rewriter agent instance
        max_rewrites: Maximum rewrite attempts (default: 2)
        
    Returns:
        Validated LessonQuiz
    """
    logger.info(f"\n{'='*70}")
    logger.info(f"🎯 Pipeline: {lesson_id} × {profession}")
    logger.info(f"{'='*70}")
    
    # Extract lesson objectives
    lesson_objectives = lesson_data.get('what_learners_will_understand', [])
    
    # STAGE 1: Generator
    draft_quiz = generator.generate(
        lesson_id=lesson_id,
        profession=profession,
        lesson_objectives=lesson_objectives,
        user_profile=user_profile
    )
    
    # STAGE 2: Review Loop
    for attempt in range(max_rewrites + 1):
        logger.info(f"\n📋 Review Cycle {attempt + 1}/{max_rewrites + 1}")
        
        review = reviewer.evaluate(
            quiz_json=draft_quiz,
            lesson_id=lesson_id,
            profession=profession,
            lesson_objectives=lesson_objectives
        )
        
        if review.passed:
            logger.info("✅ Quiz passed all quality checks!")
            break
        
        if attempt < max_rewrites:
            # STAGE 3: Rewrite
            logger.info(f"🔄 Triggering rewrite (attempt {attempt + 1}/{max_rewrites})")
            draft_quiz = rewriter.fix(
                quiz_json=draft_quiz,
                issues=review.issues,
                lesson_id=lesson_id,
                profession=profession,
                lesson_objectives=lesson_objectives
            )
        else:
            # Max attempts reached
            logger.warning(f"⚠️  Quiz did not pass after {max_rewrites} rewrites")
            logger.warning("   Using best attempt (manual review recommended)")
    
    # STAGE 4: Final Validation
    try:
        validated_quiz = LessonQuiz(**draft_quiz)
        logger.info("✅ Pydantic validation passed")
        return validated_quiz
    except Exception as e:
        logger.error(f"❌ Final validation failed: {e}")
        logger.error(f"   Quiz JSON: {json.dumps(draft_quiz, indent=2)}")
        raise


@track(name="generate_all_lesson_quizzes")
def main():
    """Main execution: Generate quizzes for all lesson × profession combinations."""
    logger.info("🎓 Vina Lesson Quiz Generator - Multi-Agent Pipeline")
    logger.info(f"📦 Opik Integration: {'✅ Enabled' if OPIK_AVAILABLE else '❌ Disabled'}\n")
    
    # 1. Load Course Structure
    try:
        config = load_course_config(COURSE_ID)
        lessons = config["lessons"]
        logger.info(f"✅ Loaded {len(lessons)} lessons from course config\n")
    except Exception as e:
        logger.error(f"❌ Failed to load course config: {e}")
        return
    
    # 2. Load User Profiles
    user_profiles = {}
    for profession in TARGET_PROFESSIONS:
        try:
            profile = get_or_create_profile(profession)
            user_profiles[profession] = profile
            logger.info(f"✅ Loaded profile: {profession}")
        except Exception as e:
            logger.error(f"❌ Failed to load profile for {profession}: {e}")
            return
    
    logger.info("")
    
    # 3. Initialize Agents
    generator = LessonQuizGeneratorAgent()
    reviewer = LessonQuizReviewerAgent()
    rewriter = LessonQuizRewriterAgent()
    
    # 4. Generate All Quizzes
    final_output = {}
    total_combinations = len(lessons) * len(TARGET_PROFESSIONS)
    current = 0
    
    for lesson in lessons:
        lesson_id = lesson["lesson_id"]
        final_output[lesson_id] = {}
        
        for profession in TARGET_PROFESSIONS:
            current += 1
            logger.info(f"\n{'#'*70}")
            logger.info(f"# Progress: {current}/{total_combinations}")
            logger.info(f"{'#'*70}")
            
            try:
                quiz = generate_quiz_for_lesson(
                    lesson_id=lesson_id,
                    profession=profession,
                    lesson_data=lesson,
                    user_profile=user_profiles[profession],
                    generator=generator,
                    reviewer=reviewer,
                    rewriter=rewriter
                )
                
                final_output[lesson_id][profession] = quiz.dict()
                logger.info(f"✅ SUCCESS: {lesson_id} × {profession}\n")
                
            except Exception as e:
                logger.error(f"❌ FAILED: {lesson_id} × {profession} - {e}\n")
                continue
    
    # 5. Save Output
    if not final_output:
        logger.error("❌ No quizzes generated successfully. Aborting save.")
        return
    
    try:
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        with open(OUTPUT_FILE, "w") as f:
            json.dump(final_output, f, indent=2)
        
        # Calculate success stats
        total_expected = total_combinations
        total_generated = sum(
            len(professions) 
            for professions in final_output.values()
        )
        success_rate = (total_generated / total_expected) * 100
        
        logger.info(f"\n{'='*70}")
        logger.info(f"🎉 Generation Complete!")
        logger.info(f"{'='*70}")
        logger.info(f"📁 Output: {OUTPUT_FILE}")
        logger.info(f"✅ Success Rate: {total_generated}/{total_expected} ({success_rate:.1f}%)")
        logger.info(f"{'='*70}\n")
        
    except Exception as e:
        logger.error(f"❌ Failed to save output: {e}")


if __name__ == "__main__":
    main()

7. API Endpoints
7.1 Get Lesson Quiz
Endpoint: GET /api/v1/quizzes/{lessonId}
Purpose: Retrieve quiz questions for a completed lesson
Request:
httpGET /api/v1/quizzes/l05_hallucinations?userId=550e8400-e29b-41d4-a716-446655440000
Query Parameters:

userId (required): User ID to determine profession

Response (200 OK):
json{
  "lessonId": "l05_hallucinations",
  "questions": [
    {
      "id": "q1",
      "text": "You're using an LLM to summarize patient adverse events for a safety report. The model confidently cites a 2023 study on drug interactions that you cannot find. This is an example of:",
      "options": [
        "A) Context window limitation",
        "B) Hallucination",
        "C) Token prediction error",
        "D) Training data bias"
      ],
      "correctAnswer": "B",
      "explanation": "This is a hallucination—the LLM generated a plausible-sounding but nonexistent citation. Hallucinations occur when LLMs prioritize pattern completion over factual accuracy, which is especially dangerous in clinical contexts where false information could impact patient safety."
    },
    {
      "id": "q2",
      "text": "In clinical research, hallucinations are MOST dangerous when:",
      "options": [
        "A) Summarizing published literature for a review",
        "B) Generating adverse event reports from raw data",
        "C) Drafting initial protocol outlines",
        "D) Creating meeting agendas for team discussions"
      ],
      "correctAnswer": "B",
      "explanation": "Adverse event reports directly impact patient safety and regulatory compliance. Hallucinations here could lead to serious harm or incorrect filings. While accuracy matters in all contexts, this scenario has the highest stakes."
    },
    {
      "id": "q3",
      "text": "Best practice to prevent hallucinations when using LLMs in your work:",
      "options": [
        "A) Only use open-source LLMs",
        "B) Always verify outputs against authoritative sources",
        "C) Avoid using LLMs for any safety-critical tasks",
        "D) Use only the most expensive commercial models"
      ],
      "correctAnswer": "B",
      "explanation": "Human-in-the-loop verification is essential. Always cross-check LLM outputs against authoritative sources, especially for clinical data. While expensive models may hallucinate less, verification remains critical regardless of model quality."
    }
  ],
  "passThreshold": 2
}
Backend Logic:
python# src/vina_backend/api/v1/endpoints/quizzes.py

from fastapi import APIRouter, Depends, HTTPException
from vina_backend.domain.schemas.lesson_quiz import LessonQuiz
from vina_backend.services.quiz_service import get_lesson_quiz
from vina_backend.services.user_service import get_user_profile

router = APIRouter()

@router.get("/quizzes/{lesson_id}")
async def get_quiz(lesson_id: str, userId: str):
    """
    Get quiz for a lesson based on user's profession.
    
    Flow:
    1. Get user profile to determine profession
    2. Fetch pre-generated quiz from database/cache
    3. Format for frontend consumption
    """
    try:
        # Get user's profession
        user_profile = await get_user_profile(userId)
        profession = user_profile.get("profession")
        
        if not profession:
            raise HTTPException(
                status_code=400, 
                detail="User profession not set. Complete onboarding first."
            )
        
        # Fetch quiz (from database or JSON file)
        quiz = await get_lesson_quiz(lesson_id, profession)
        
        if not quiz:
            raise HTTPException(
                status_code=404,
                detail=f"Quiz not found for lesson {lesson_id}"
            )
        
        return quiz
        
    except Exception as e:
        logger.error(f"Failed to fetch quiz: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch quiz")

7.2 Submit Quiz Answers
Endpoint: POST /api/v1/quizzes/submit
Purpose: Submit quiz answers and get results
Request:
json{
  "lessonId": "l05_hallucinations",
  "userId": "550e8400-e29b-41d4-a716-446655440000",
  "answers": [
    {
      "questionId": "q1",
      "selectedAnswer": "B",
      "isCorrect": true
    },
    {
      "questionId": "q2",
      "selectedAnswer": "B",
      "isCorrect": true
    },
    {
      "questionId": "q3",
      "selectedAnswer": "A",
      "isCorrect": false
    }
  ]
}
Response (200 OK):
json{
  "score": 2,
  "total": 3,
  "passed": true,
  "pointsEarned": 20,
  "feedback": "Well done! You got 2/3 correct.",
  "nextLessonId": "l06_bias_issues"
}
Backend Logic:
python# src/vina_backend/api/v1/endpoints/quizzes.py

@router.post("/quizzes/submit")
async def submit_quiz(submission: QuizSubmission):
    """
    Process quiz submission and calculate results.
    
    Flow:
    1. Validate submission (3 answers)
    2. Calculate score
    3. Determine pass/fail (2/3 threshold)
    4. Award points
    5. Return results
    """
    try:
        # Calculate score
        score = sum(1 for ans in submission.answers if ans["isCorrect"])
        total = 3
        
        # Determine pass/fail
        passed = score >= 2
        
        # Award points
        points_map = {3: 30, 2: 20, 1: 10, 0: 0}
        points_earned = points_map.get(score, 0)
        
        # Generate feedback
        if score == 3:
            feedback = "Excellent! You got 3/3 correct."
        elif score == 2:
            feedback = "Well done! You got 2/3 correct."
        elif score == 1:
            feedback = "You got 1/3 correct. Let's review the concepts."
        else:
            feedback = "You got 0/3 correct. Let's review the concepts."
        
        # Get next lesson (if passed)
        next_lesson_id = None
        if passed:
            next_lesson_id = await get_next_lesson(submission.lessonId)
        
        return QuizResult(
            score=score,
            total=total,
            passed=passed,
            pointsEarned=points_earned,
            feedback=feedback,
            nextLessonId=next_lesson_id
        )
        
    except Exception as e:
        logger.error(f"Failed to submit quiz: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit quiz")

8. Frontend Integration Points
8.1 Quiz Screen Component
Route: /quiz/{lessonId}
Component: app/quiz/[lessonId]/page.tsx
Key Behaviors:

On Mount:

Fetch quiz: GET /api/v1/quizzes/{lessonId}?userId={userId}
Display "Take Quiz" + "Skip Quiz" buttons
If user clicks "Skip Quiz", show confirmation dialog


During Quiz:

Show questions one at a time
Lock answer after selection (no retry)
Show immediate feedback (green/red + explanation)
Wait 1 second, then show "Next Question" button


After Last Question:

Submit answers: POST /api/v1/quizzes/submit
Navigate to /quiz/{lessonId}/results



State Management:
typescript// app/quiz/[lessonId]/page.tsx

'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useProgress } from '@/contexts/ProgressContext';

interface QuizQuestion {
  id: string;
  text: string;
  options: string[];
  correctAnswer: string;
  explanation: string;
}

export default function QuizPage({ params }: { params: { lessonId: string } }) {
  const router = useRouter();
  const { progress, markLessonComplete } = useProgress();
  
  const [questions, setQuestions] = useState<QuizQuestion[]>([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [showFeedback, setShowFeedback] = useState(false);
  const [userAnswers, setUserAnswers] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  
  // Fetch quiz on mount
  useEffect(() => {
    fetchQuiz();
  }, []);
  
  const fetchQuiz = async () => {
    const { userId } = getUserFromLocalStorage();
    const response = await fetch(`/api/v1/quizzes/${params.lessonId}?userId=${userId}`);
    const data = await response.json();
    setQuestions(data.questions);
    setIsLoading(false);
  };
  
  const handleSelectAnswer = (answer: string) => {
    if (showFeedback) return; // Answer already locked
    
    setSelectedAnswer(answer);
    
    // Check if correct
    const currentQuestion = questions[currentQuestionIndex];
    const isCorrect = answer === currentQuestion.correctAnswer;
    
    // Record answer
    setUserAnswers([
      ...userAnswers,
      {
        questionId: currentQuestion.id,
        selectedAnswer: answer,
        isCorrect
      }
    ]);
    
    // Show feedback
    setShowFeedback(true);
  };
  
  const handleNext = () => {
    if (currentQuestionIndex < questions.length - 1) {
      // Next question
      setCurrentQuestionIndex(prev => prev + 1);
      setSelectedAnswer(null);
      setShowFeedback(false);
    } else {
      // Quiz complete - submit answers
      submitQuiz();
    }
  };
  
  const submitQuiz = async () => {
    const { userId } = getUserFromLocalStorage();
    
    const response = await fetch('/api/v1/quizzes/submit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        lessonId: params.lessonId,
        userId,
        answers: userAnswers
      })
    });
    
    const result = await response.json();
    
    // Navigate to results page with result data
    router.push(`/quiz/${params.lessonId}/results?score=${result.score}&passed=${result.passed}`);
  };
  
  const handleSkipQuiz = () => {
    // Show confirmation dialog
    const confirmed = confirm(
      "Skip the quiz?\n\n" +
      "You'll earn 10 points and the next lesson will unlock, " +
      "but you won't verify your understanding."
    );
    
    if (confirmed) {
      // Mark lesson as completed (unverified)
      markLessonComplete(params.lessonId, 0, 10); // score=0, points=10
      router.push('/course-map');
    }
  };
  
  if (isLoading) {
    return <LoadingSpinner />;
  }
  
  const currentQuestion = questions[currentQuestionIndex];
  
  return (
    <div className="min-h-screen bg-gray-50 p-4">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-xl font-semibold">Quiz: {params.lessonId}</h1>
        <p className="text-sm text-gray-600">
          Question {currentQuestionIndex + 1} of {questions.length}
        </p>
        <div className="flex gap-1 mt-2">
          {questions.map((_, idx) => (
            <div
              key={idx}
              className={`h-2 flex-1 rounded-full ${
                idx === currentQuestionIndex ? 'bg-teal-600' :
                idx < currentQuestionIndex ? 'bg-teal-300' :
                'bg-gray-300'
              }`}
            />
          ))}
        </div>
      </div>
      
      {/* Question */}
      <div className="bg-white rounded-lg p-6 shadow-sm mb-4">
        <h2 className="text-lg font-medium mb-4">{currentQuestion.text}</h2>
        
        {/* Options */}
        <div className="space-y-3">
          {currentQuestion.options.map((option, idx) => {
            const letter = String.fromCharCode(65 + idx); // A, B, C, D
            const isSelected = selectedAnswer === letter;
            const isCorrect = letter === currentQuestion.correctAnswer;
            
            return (
              <button
                key={idx}
                onClick={() => handleSelectAnswer(letter)}
                disabled={showFeedback}
                className={`
                  w-full text-left p-4 rounded-lg border-2 transition-all
                  ${!showFeedback && 'hover:border-teal-300'}
                  ${isSelected && !showFeedback && 'border-teal-500 bg-teal-50'}
                  ${isSelected && showFeedback && isCorrect && 'border-green-500 bg-green-50'}
                  ${isSelected && showFeedback && !isCorrect && 'border-red-500 bg-red-50'}
                  ${!isSelected && 'border-gray-300'}
                  ${showFeedback && 'cursor-not-allowed'}
                `}
              >
                <span className="font-medium">{letter})</span> {option}
              </button>
            );
          })}
        </div>
        
        {/* Feedback */}
        {showFeedback && (
          <div className={`mt-4 p-4 rounded-lg ${
            selectedAnswer === currentQuestion.correctAnswer
              ? 'bg-green-100 border-2 border-green-500'
              : 'bg-red-100 border-2 border-red-500'
          }`}>
            <p className="font-semibold mb-2">
              {selectedAnswer === currentQuestion.correctAnswer ? '✅ Correct!' : '❌ Not quite'}
            </p>
            <p className="text-sm">{currentQuestion.explanation}</p>
          </div>
        )}
      </div>
      
      {/* Action Buttons */}
      {showFeedback && (
        <button
          onClick={handleNext}
          className="w-full bg-teal-600 text-white py-3 rounded-lg font-semibold hover:bg-teal-700"
        >
          {currentQuestionIndex < questions.length - 1 ? 'Next Question →' : 'See Results →'}
        </button>
      )}
      
      {/* Skip Quiz (always visible, small text) */}
      <button
        onClick={handleSkipQuiz}
        className="w-full mt-2 text-sm text-gray-500 hover:text-gray-700"
      >
        Skip Quiz
      </button>
    </div>
  );
}

8.2 Quiz Results Screen
Route: /quiz/{lessonId}/results
Component: app/quiz/[lessonId]/results/page.tsx
Key Behaviors:

Display Results:

Show score (X/3 correct)
Show points earned
Show pass/fail status
Show streak update


Action Buttons (Pass):

"Continue Learning" → Navigate to /course-map
"Review Lesson" → Navigate to /lesson/{lessonId}?mode=review


Action Buttons (Fail):

"Re-watch Lesson" → Navigate to /lesson/{lessonId}
"Try Simpler Version" → Navigate to /lesson/{lessonId}?adapt=simplify
"Skip to Next Lesson" → Mark complete (unverified), navigate to /course-map



Implementation:
typescript// app/quiz/[lessonId]/results/page.tsx

'use client';

import { useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useProgress } from '@/contexts/ProgressContext';

export default function QuizResultsPage({ params }: { params: { lessonId: string } }) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { markLessonComplete, incrementPoints, updateStreak } = useProgress();
  
  const score = parseInt(searchParams.get('score') || '0');
  const passed = searchParams.get('passed') === 'true';
  
  const pointsMap = { 3: 30, 2: 20, 1: 10, 0: 0 };
  const pointsEarned = pointsMap[score as keyof typeof pointsMap] || 0;
  
  useEffect(() => {
    if (passed) {
      // Update progress
      markLessonComplete(params.lessonId, score, pointsEarned);
      updateStreak();
    }
  }, []);
  
  if (passed) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl p-8 max-w-md w-full text-center shadow-lg">
          <div className="text-6xl mb-4">🎉</div>
          <h1 className="text-2xl font-bold mb-2">Lesson Complete!</h1>
          <p className="text-lg mb-6">You got {score}/3 correct</p>
          
          <div className="bg-teal-50 rounded-lg p-4 mb-6">
            <p className="text-sm text-gray-600">Points Earned</p>
            <p className="text-3xl font-bold text-teal-600">+{pointsEarned} 💎</p>
          </div>
          
          <button
            onClick={() => router.push('/course-map')}
            className="w-full bg-teal-600 text-white py-3 rounded-lg font-semibold mb-3 hover:bg-teal-700"
          >
            Continue Learning →
          </button>
          
          <button
            onClick={() => router.push(`/lesson/${params.lessonId}?mode=review`)}
            className="w-full text-teal-600 py-2 text-sm hover:text-teal-700"
          >
            Review Lesson
          </button>
        </div>
      </div>
    );
  } else {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl p-8 max-w-md w-full text-center shadow-lg">
          <div className="text-6xl mb-4">📚</div>
          <h1 className="text-2xl font-bold mb-2">Let's Review</h1>
          <p className="text-lg mb-2">You got {score}/3 correct</p>
          <p className="text-sm text-gray-600 mb-6">
            No worries! Learning takes time. Choose how you'd like to proceed:
          </p>
          
          <div className="space-y-3">
            <button
              onClick={() => router.push(`/lesson/${params.lessonId}`)}
              className="w-full bg-teal-600 text-white py-3 rounded-lg font-semibold hover:bg-teal-700"
            >
              Re-watch Lesson
            </button>
            
            <button
              onClick={() => router.push(`/lesson/${params.lessonId}?adapt=simplify`)}
              className="w-full bg-white border-2 border-teal-600 text-teal-600 py-3 rounded-lg font-semibold hover:bg-teal-50"
            >
              Try Simpler Version
            </button>
            
            <button
              onClick={() => {
                markLessonComplete(params.lessonId, score, 10); // Unverified completion
                router.push('/course-map');
              }}
              className="w-full text-gray-600 py-2 text-sm hover:text-gray-800"
            >
              Skip to Next Lesson
            </button>
          </div>
        </div>
      </div>
    );
  }
}

9. Edge Cases & Error Handling
9.1 Browser Close During Quiz
Scenario: User closes browser after answering Q1, reopens later
Behavior:

Quiz state is NOT saved (no mid-quiz persistence)
When user returns: Lesson shows as "Active" (not completed)
User can retake quiz from Q1

Rationale:

Simpler implementation (no partial state management)
Low impact (quiz is only 3 questions, ~90 seconds)

Implementation:
typescript// No sessionStorage persistence for quiz state
// User must complete quiz in one session

9.2 Quiz Fetch Fails
Scenario: Backend returns 500 or quiz not found
Behavior:

Show error message: "Couldn't load quiz. Please try again."
Provide "Retry" button
Provide "Go Back" button (return to lesson)

Implementation:
typescriptif (error) {
  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="text-center">
        <p className="text-xl font-semibold text-gray-800 mb-2">Oops!</p>
        <p className="text-gray-600 mb-6">Couldn't load quiz. Please try again.</p>
        <button onClick={fetchQuiz} className="btn-primary mr-2">Retry</button>
        <button onClick={() => router.back()} className="btn-secondary">Go Back</button>
      </div>
    </div>
  );
}

9.3 Quiz Submit Fails
Scenario: Network error when submitting answers
Behavior:

Show error toast: "Couldn't submit quiz. Check your connection."
Preserve answers in component state
Retry button attempts resubmission
Don't lose user's progress

Implementation:
typescriptconst submitQuiz = async () => {
  try {
    const response = await fetch('/api/v1/quizzes/submit', {
      method: 'POST',
      body: JSON.stringify({ lessonId, userId, answers: userAnswers })
    });
    
    if (!response.ok) throw new Error('Submit failed');
    
    const result = await response.json();
    router.push(`/quiz/${lessonId}/results?score=${result.score}&passed=${result.passed}`);
    
  } catch (error) {
    // Show error, don't navigate
    setError('Couldn't submit quiz. Check your connection.');
    // Answers preserved in userAnswers state - can retry
  }
};

9.4 User Profession Not Set
Scenario: User accesses quiz before completing onboarding
Behavior:

Backend returns 400: "User profession not set"
Frontend redirects to /profession-select with message
After profession selection, redirect back to quiz

Implementation:
typescript// Backend
if (!user_profile.get("profession")):
    raise HTTPException(
        status_code=400,
        detail="User profession not set. Complete onboarding first."
    )

// Frontend
if (response.status === 400) {
  router.push('/profession-select?redirect=/quiz/' + lessonId);
}

9.5 Quiz Already Completed (Review Mode)
Scenario: User replays completed lesson and retakes quiz
Behavior:

Quiz appears normally (can retake)
Results screen shows "New Best Score" if improved
Points awarded: Difference between old and new score
Lesson completion status: Already complete (no change)

Example:

First attempt: 2/3 (20 pts)
Second attempt: 3/3 (30 pts)
Award: +10 pts (difference)

Implementation:
typescript// Backend
const previous_score = await get_previous_quiz_score(userId, lessonId);

if (previous_score !== null) {
  // User retaking quiz
  const points_earned = Math.max(0, new_score_points - previous_score_points);
  return {
    score: new_score,
    passed: new_score >= 2,
    pointsEarned: points_earned,
    feedback: `New best score! +${points_earned} points`,
    isRetake: true
  };
}

10. Implementation Checklist
10.1 Backend Tasks
Phase 1: Agent Development (Day 1)

 Create lesson_quiz_generator.py with Generator Agent
 Create lesson_quiz_reviewer.py with Reviewer Agent
 Create lesson_quiz_rewriter.py with Rewriter Agent
 Test agents individually (manual prompts)
 Integrate with Opik for tracking (optional)

Phase 2: Pipeline Integration (Day 1-2)

 Create generate_lesson_quizzes.py orchestration script
 Load course config (17 lessons + objectives)
 Load user profiles (4 professions)
 Implement multi-agent loop (Generator → Reviewer → Rewriter)
 Add Pydantic validation
 Test on 1 lesson × 1 profession (validate output quality)

Phase 3: Batch Generation (Day 2)

 Run full generation: 68 quizzes (17 lessons × 4 professions)
 Save to lesson_quizzes.json
 Manual review of 5-10 sample quizzes
 Fix any systemic issues (update prompts, rerun)
 Commit final quizzes to repo

Phase 4: API Development (Day 2-3)

 Create /api/v1/quizzes/{lessonId} endpoint (GET)
 Create /api/v1/quizzes/submit endpoint (POST)
 Add quiz loading from JSON file (or database)
 Add scoring logic
 Add next lesson lookup logic
 Test endpoints with Postman/curl

Phase 5: Database Integration (Optional, Day 3)

 Create lesson_quizzes table (if using DB instead of JSON)
 Add quiz seeding script
 Update API to query database
 Test performance


10.2 Frontend Tasks
Phase 1: Quiz Screen (Day 2)

 Create /quiz/[lessonId]/page.tsx
 Add quiz fetching logic
 Implement question display (1 at a time)
 Add answer selection with immediate feedback
 Add "Skip Quiz" button with confirmation
 Test on multiple browsers (Chrome, Safari, mobile)

Phase 2: Results Screen (Day 2-3)

 Create /quiz/[lessonId]/results/page.tsx
 Display score, points, pass/fail
 Add action buttons (Continue, Review, Re-watch, Simplify, Skip)
 Integrate with ProgressContext (mark lesson complete, award points)
 Test all result scenarios (pass, fail, skip)

Phase 3: Integration (Day 3)

 Update Lesson Player to navigate to quiz after video
 Update Course Map to show quiz completion status (optional badge)
 Add error handling (fetch fails, submit fails)
 Test full flow: Watch video → Take quiz → See results → Next lesson

Phase 4: Polish (Day 3)

 Add loading states (skeleton, spinner)
 Add animations (fade-in, slide-up)
 Mobile responsive testing
 Accessibility audit (keyboard nav, screen reader)


10.3 Testing Checklist
Unit Tests:

 Generator Agent produces valid JSON
 Reviewer Agent correctly flags issues
 Rewriter Agent fixes flagged issues
 Pydantic validation catches malformed quizzes

Integration Tests:

 Full pipeline generates valid quiz (1 lesson × 1 profession)
 API endpoints return correct data
 Quiz submission calculates score correctly

End-to-End Tests:

 User completes lesson → Quiz appears
 User passes quiz → Next lesson unlocks
 User fails quiz → Options appear correctly
 User skips quiz → Lesson marked unverified
 User retakes quiz → Score updates

Edge Case Tests:

 Browser close during quiz → State resets
 Quiz fetch fails → Error message shown
 Quiz submit fails → Retry works
 User without profession → Redirects to onboarding


10.4 Deployment Checklist
Pre-Deploy:

 All 68 quizzes generated and committed
 Backend API tested and working
 Frontend UI tested on mobile + desktop
 Error handling verified
 Opik integration configured (if using)

Deploy:

 Push backend to Railway
 Push frontend to Vercel
 Test production API endpoints
 Verify quiz loading in production
 Monitor logs for errors

Post-Deploy:

 Test full user flow in production
 Check Opik dashboard (if enabled)
 Monitor error rates
 Collect user feedback


Summary
This PRD provides complete specifications for implementing the post-lesson quiz feature using a multi-agent generation pipeline. Key highlights:
✅ 68 quizzes pre-generated (17 lessons × 4 professions)
✅ Multi-agent quality control (Generator → Reviewer → Rewriter)
✅ Profession-specific questions tailored to each learner's work context
✅ Flexible progression (skip quiz, fail → 3 options)
✅ Immediate feedback with educational explanations
✅ Complete API spec for backend integration
✅ Full frontend flows with code examples
✅ Edge case handling and error recovery
