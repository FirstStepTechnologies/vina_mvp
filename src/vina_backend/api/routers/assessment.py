from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel
from sqlmodel import Session
from vina_backend.integrations.db.session import get_session
from vina_backend.integrations.db.models.user import User
from vina_backend.api.dependencies import get_current_user

router = APIRouter(prefix="/assessment", tags=["assessment"])

# Hardcoded questions for Hackathon
# Source: Vina-FrontEnd-PRD.md
PRE_ASSESSMENT_QUESTIONS = [
    {
        "id": "aq_001",
        "questionText": "What does LLM stand for?",
        "options": [
            "A) Large Language Model",
            "B) Linear Learning Machine",
            "C) Logical Language Module",
            "D) Limited Language Memory"
        ],
        "correctAnswer": "A",
        "associatedLesson": "l01_what_llms_are",
        "difficultyLevel": 1
    },
    {
        "id": "aq_002",
        "questionText": "Which of these is a key limitation of LLMs?",
        "options": [
            "A) They cannot process text",
            "B) They define their own goals",
            "C) Hallucinations (making up facts)",
            "D) They are always correct"
        ],
        "correctAnswer": "C",
        "associatedLesson": "l05_hallucinations",
        "difficultyLevel": 1
    },
    {
        "id": "aq_003",
        "questionText": "What is a 'token' in the context of LLMs?",
        "options": [
            "A) A cryptocurrency used to pay for API calls",
            "B) A unit of text (part of a word) processed by the model",
            "C) An authentication key",
            "D) A specific prompt template"
        ],
        "correctAnswer": "B",
        "associatedLesson": "l02_tokens_context",
        "difficultyLevel": 2
    },
    {
        "id": "aq_004",
        "questionText": "Prompt Engineering refers to:",
        "options": [
            "A) Building physical servers for AI",
            "B) Writing code in Python",
            "C) Crafting inputs to guide LLM outputs effectively",
            "D) Training a model from scratch"
        ],
        "correctAnswer": "C",
        "associatedLesson": "l03_prompting_basics",
        "difficultyLevel": 2
    },
    {
        "id": "aq_005",
        "questionText": "When an LLM validation set has bias, the model will likely:",
        "options": [
            "A) Automatically correct it during inference",
            "B) Refuse to answer questions",
            "C) Reflect that bias in its outputs",
            "D) Crash"
        ],
        "correctAnswer": "C",
        "associatedLesson": "l06_bias_issues",
        "difficultyLevel": 3
    }
]

class AssessmentAnswer(BaseModel):
    questionId: str
    selected: str

class AssessmentSubmission(BaseModel):
    answers: List[AssessmentAnswer]

@router.get("/pre-quiz")
def get_pre_assessment(current_user: User = Depends(get_current_user)):
    """Get placement quiz questions."""
    return {"questions": PRE_ASSESSMENT_QUESTIONS}

@router.post("/submit")
def submit_assessment(
    submission: AssessmentSubmission,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Submit assessment answers. Calculates score and assigns starting lesson.
    Marks skipped lessons as completed to unlock the map.
    """
    score = 0
    # Map ID to correct answer
    key_map = {q["id"]: q["correctAnswer"] for q in PRE_ASSESSMENT_QUESTIONS}
    
    for ans in submission.answers:
        if key_map.get(ans.questionId) == ans.selected:
            score += 1
    
    # Logic based on 5 questions (scaled down from PRD's 10)
    # 0-1 Correct -> Beginner (L01)
    # 2-3 Correct -> Intermediate (L03/L04)
    # 4-5 Correct -> Advanced (L06)
    
    starting_lesson = "l01_what_llms_are"
    placement = "Beginner"
    lessons_to_skip = []
    
    if score >= 4:
        starting_lesson = "l06_bias_issues"
        placement = "Advanced"
        lessons_to_skip = [
            "l01_what_llms_are", 
            "l02_tokens_context", 
            "l03_prompting_basics", 
            "l04_where_llms_excel", 
            "l05_hallucinations"
        ]
    elif score >= 2:
        starting_lesson = "l04_where_llms_excel"
        placement = "Intermediate"
        lessons_to_skip = [
            "l01_what_llms_are", 
            "l02_tokens_context", 
            "l03_prompting_basics"
        ]
        
    # Update User Progress
    if current_user.progress:
        # Avoid duplicates
        current_completed = set(current_user.progress.completed_lessons or [])
        new_completed = list(current_completed.union(set(lessons_to_skip)))
        
        current_user.progress.completed_lessons = new_completed
        current_user.progress.diamonds += 50 # Initial bonus
        
        session.add(current_user.progress)
        session.commit()
        
    return {
        "startingLesson": starting_lesson,
        "score": score,
        "placement": placement,
        "skippedLessons": lessons_to_skip
    }
