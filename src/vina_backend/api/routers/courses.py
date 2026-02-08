from typing import List, Optional
from fastapi import APIRouter, Depends
from vina_backend.domain.schemas.course import LessonSummary
from vina_backend.integrations.db.models.user import User
from vina_backend.api.dependencies import get_current_user

router = APIRouter(prefix="/course", tags=["course"])

# Static lesson list for Hackathon MVP
# Source: Vina-FrontEnd-PRD.md
STATIC_LESSONS = [
    {
        "lessonId": "l01_what_llms_are",
        "lessonNumber": 1,
        "lessonName": "What LLMs Are",
        "shortTitle": "What are LLMs?",
        "topicGroup": "The Foundations",
        "estimatedDuration": 3,
        "prerequisites": []
    },
    {
        "lessonId": "l02_tokens_context",
        "lessonNumber": 2,
        "lessonName": "Tokens & Context Windows",
        "shortTitle": "Tokens & Context",
        "topicGroup": "The Foundations",
        "estimatedDuration": 3,
        "prerequisites": ["l01_what_llms_are"]
    },
    {
        "lessonId": "l03_prompting_basics",
        "lessonNumber": 3,
        "lessonName": "Prompting Basics",
        "shortTitle": "Prompting 101",
        "topicGroup": "The Foundations",
        "estimatedDuration": 4,
        "prerequisites": ["l02_tokens_context"]
    },
    {
        "lessonId": "l04_where_llms_excel",
        "lessonNumber": 4,
        "lessonName": "Where LLMs Excel & Fail",
        "shortTitle": "LLM Capability",
        "topicGroup": "The Foundations",
        "estimatedDuration": 4,
        "prerequisites": ["l03_prompting_basics"]
    },
    {
        "lessonId": "l05_hallucinations",
        "lessonNumber": 5,
        "lessonName": "Understanding Hallucinations",
        "shortTitle": "Hallucinations",
        "topicGroup": "Risks & Reliability",
        "estimatedDuration": 5,
        "prerequisites": ["l04_where_llms_excel"]
    },
    {
        "lessonId": "l06_bias_issues",
        "lessonNumber": 6,
        "lessonName": "Bias & Safety Issues",
        "shortTitle": "Bias & Safety",
        "topicGroup": "Risks & Reliability",
        "estimatedDuration": 4,
        "prerequisites": ["l05_hallucinations"]
    },
    {
        "lessonId": "l07_data_privacy",
        "lessonNumber": 7,
        "lessonName": "Data Privacy & Security",
        "shortTitle": "Data Privacy",
        "topicGroup": "Risks & Reliability",
        "estimatedDuration": 3,
        "prerequisites": ["l06_bias_issues"]
    }
]

@router.get("/map", response_model=List[LessonSummary])
def get_course_map(current_user: User = Depends(get_current_user)):
    """
    Get the lesson map. Calculates status (locked/active/completed) 
    based on the user's progress.
    """
    progress = current_user.progress
    completed_ids = set()
    
    if progress and progress.completed_lessons:
        completed_ids = set(progress.completed_lessons)
        
    result = []
    
    for lesson_data in STATIC_LESSONS:
        lid = lesson_data["lessonId"]
        prereqs = lesson_data.get("prerequisites", [])
        
        # Default verified status
        status = "locked"
        
        # 1. Check if completed
        if lid in completed_ids:
            status = "completed"
            
        # 2. Check unlock condition (if not completed)
        elif not prereqs:
            # No prereqs -> always unlocked
            status = "active"
        else:
            # Has prereqs -> check if ALL are completed
            all_prereqs_met = all(p in completed_ids for p in prereqs)
            if all_prereqs_met:
                status = "active"
                
        # Create summary object
        # Note: LessonSummary alias="lessonId" handles the mapping
        summary = LessonSummary(
            lessonId=lid,
            lessonNumber=lesson_data["lessonNumber"],
            lessonName=lesson_data["lessonName"],
            shortTitle=lesson_data["shortTitle"],
            topicGroup=lesson_data["topicGroup"],
            estimatedDuration=lesson_data["estimatedDuration"],
            prerequisites=prereqs,
            status=status
        )
        result.append(summary)
        
    return result
