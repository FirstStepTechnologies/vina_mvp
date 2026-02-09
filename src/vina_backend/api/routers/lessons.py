import json
from pathlib import Path
from typing import Optional, List, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from pydantic import BaseModel
from sqlmodel import Session, select
from vina_backend.integrations.db.models.user import User
from vina_backend.api.dependencies import get_current_user, get_db

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
    profession: Optional[str] = Query(None, description="User profession for video personalization"),  # NEW: For unauthenticated users
    current_user: Optional[User] = None,  # Made optional for hackathon demo
    db: Session = Depends(get_db)
):
    """
    Get lesson details including video URL. 
    1. Checks LessonCache for dynamic/Cloudinary URL.
    2. Fallback: Lookups up video in manifest using fuzzy matching against profile.
    """
    # 1. Check Dynamic Cache
    video_url = None
    captions_url = None
    cached = False
    title = lesson_id.replace("_", " ").title()
    
    if current_user and current_user.profile:
        cache_service = LessonCacheService(db)
        # Try to find cached entry
        # Note: We need the model name to query specific cache, but here we query by profile/lesson
        # effectively we want *any* valid video for this user/lesson/difficulty
        # The cache structure requires LLM model name.
        # Strict retrieval might be hard without knowing the model.
        # However, we can use a simpler query or just iterate reasonable defaults if needed.
        # OR: We can add a method to CacheService to get *any* entry for this lesson/profile/diff.
        
        # Let's try to query directly:
        # We need to import LessonCache model to query
        from vina_backend.services.lesson_cache import LessonCache, LessonCacheService
        
        profile_hash = LessonCacheService.generate_profile_hash(current_user.profile)
        # Query for any model
        statement = select(LessonCache).where(
            LessonCache.course_id == "c_llm_foundations", # Defaulting for now
            LessonCache.lesson_id == lesson_id,
            LessonCache.difficulty_level == difficulty,
            LessonCache.profile_hash == profile_hash
        ).order_by(LessonCache.created_at.desc())
        
        entry = db.exec(statement).first()
        if entry and entry.video_url:
            video_url = entry.video_url
            cached = True
            try:
                content = json.loads(entry.lesson_json)
                title = content.get("lesson_title", title)
            except:
                pass

    # 2. Fallback to Manifest
    if not video_url:
        manifest = _load_manifest()
        
        # Normalize profile values - use query param if no authenticated user
        prof = current_user.profile if current_user else None
        profession_str = ""
        if prof and prof.profession:
            profession_str = prof.profession.lower().replace(" ", "_").replace("/", "_")
        elif profession:  # Use query parameter
            profession_str = profession.lower().replace(" ", "_").replace("/", "_")
        
        target_diff = f"d{difficulty}"
        
        candidates = []
        
        # Keys might be "hash" or "descriptive_name"
        for key, url in manifest.items():
            # Only check descriptive keys that match the lesson ID
            # (Hashes won't match, which is fine, we want personalized ones)
            if lesson_id in key:
                score = 0
                # Higher score for matching profession
                if profession_str and profession_str in key.lower():
                    score += 3
                # Higher score for matching difficulty
                if target_diff in key:
                    score += 2
                
                candidates.append((score, url, key))
        
        # Sort by score descending
        candidates.sort(key=lambda x: x[0], reverse=True)
        
        if candidates:
            video_url = candidates[0][1]
            cached = True
    
    if video_url:
        # Optimistic assumption for VTT
        if video_url.endswith(".mp4"):
            captions_url = video_url.replace(".mp4", ".vtt")
        else:
             captions_url = video_url + ".vtt"

    if not video_url:
         # Fallback logic or 404
         # For Hackathon, if we can't find the exact video, check if there's *any* video for this lesson?
         # Retry without profession/difficulty strictness?
         manifest = _load_manifest() # reload if needed
         fallback_candidates = [u for k, u in manifest.items() if lesson_id in k]
         if fallback_candidates:
             video_url = fallback_candidates[0]
             cached = True

    return LessonDetail(
        lessonId=lesson_id,
        videoUrl=video_url, # Can be null if really not found
        duration=180, # Placeholder info
        captionsUrl=captions_url,
        difficulty=difficulty,
        cached=cached,
        title=title,
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
