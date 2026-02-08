import json
from pathlib import Path
from typing import Optional, List, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from pydantic import BaseModel
from vina_backend.integrations.db.models.user import User
from vina_backend.api.dependencies import get_current_user

router = APIRouter()

MANIFEST_PATH = Path("src/vina_backend/domain/constants/video_manifest.json")

class LessonDetail(BaseModel):
    lessonId: str
    videoUrl: Optional[str] = None
    duration: int = 180
    captionsUrl: Optional[str] = None
    difficulty: int
    cached: bool
    title: str = "Lesson Content"
    resources: List[Any] = []

def _load_manifest() -> dict:
    if not MANIFEST_PATH.exists():
        return {}
    try:
        with open(MANIFEST_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return {}

@router.get("/{lesson_id}", response_model=LessonDetail)
def get_lesson_detail(
    lesson_id: str,
    difficulty: int = Query(3, ge=1, le=5),
    current_user: User = Depends(get_current_user)
):
    """
    Get lesson details including video URL. 
    Lookups up video in manifest using fuzzy matching against profile.
    """
    manifest = _load_manifest()
    
    # Normalize profile values
    prof = current_user.profile
    profession = ""
    if prof and prof.profession:
        profession = prof.profession.lower().replace(" ", "_").replace("/", "_")
    
    target_diff = f"d{difficulty}"
    
    candidates = []
    
    # Keys might be "hash" or "descriptive_name"
    for key, url in manifest.items():
        # Only check descriptive keys that match the lesson ID
        # (Hashes won't match, which is fine, we want personalized ones)
        if lesson_id in key:
            score = 0
            # Higher score for matching profession
            if profession and profession in key.lower():
                score += 3
            # Higher score for matching difficulty
            if target_diff in key:
                score += 2
            
            candidates.append((score, url, key))
    
    # Sort by score descending
    candidates.sort(key=lambda x: x[0], reverse=True)
    
    video_url = None
    captions_url = None
    cached = False
    
    if candidates:
        video_url = candidates[0][1]
        cached = True
        # Optimistic assumption for VTT
        if video_url.endswith(".mp4"):
            captions_url = video_url.replace(".mp4", ".vtt")
        else:
             captions_url = video_url + ".vtt"

    if not video_url:
         # Fallback logic or 404
         # For Hackathon, if we can't find the exact video, check if there's *any* video for this lesson?
         # Retry without profession/difficulty strictness?
         fallback_candidates = [u for k, u in manifest.items() if lesson_id in k]
         if fallback_candidates:
             video_url = fallback_candidates[0]
             cached = True
         else:
             # Real 404
             raise HTTPException(status_code=404, detail="Video content not found for this lesson")

    return LessonDetail(
        lessonId=lesson_id,
        videoUrl=video_url,
        duration=180, # Placeholder info
        captionsUrl=captions_url,
        difficulty=difficulty,
        cached=cached,
        title=lesson_id.replace("_", " ").title(), # Simple title generation
        resources=[]
    )

@router.post("/adapt")
def adapt_lesson(
    lessonId: str = Body(...),
    adaptationType: str = Body(...),
    currentDifficulty: int = Body(...),
    current_user: User = Depends(get_current_user)
):
    """
    Stub for AI Adaptation. 
    In the future, this triggers the LLM pipeline to rewrite the script and generate a new video.
    For now, it returns a simulated 'Generating' or switches difficulty.
    """
    # Logic from PRD:
    # simplify_this -> D1
    # get_to_the_point -> D5
    # more_examples -> Keep difficulty but use 'more_examples' context (needs regeneration)
    
    new_diff = currentDifficulty
    if adaptationType == "simplify_this":
        new_diff = 1
    elif adaptationType == "get_to_the_point":
        new_diff = 5
        
    return {
        "status": "generating",
        "message": f"Adapting lesson to '{adaptationType}'...",
        "estimatedSeconds": 5,
        "newDifficulty": new_diff
        # Frontend polls /lessons/{id} with new difficulty
    }
