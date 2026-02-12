
import sys
from pathlib import Path
from typing import Optional
from sqlmodel import Session, select, create_engine

# Setup paths
START_DIR = Path(__file__).parent.parent
sys.path.append(str(START_DIR / "src"))

from vina_backend.core.config import get_settings
from vina_backend.services.lesson_cache import LessonCache, LessonCacheService
from vina_backend.integrations.db.models.user import UserProfile
from vina_backend.domain.schemas.profile import UserProfileData

def check_video_served(
    lesson_id: str,
    profession: str,
    difficulty: int = 3,
    adaptation: Optional[str] = None,
    industry: str = "Tech Company", # Default for HR Manager
    experience_level: str = "Intermediate" # Default
):
    print(f"\n🔍 Checking Video Cache for:")
    print(f"   Lesson: {lesson_id}")
    print(f"   Profile: {profession} / {industry} / {experience_level}")
    print(f"   Difficulty: {difficulty}")
    print(f"   Adaptation: {adaptation}")

    settings = get_settings()
    engine = create_engine(settings.database_url)

    with Session(engine) as db:
        # 1. Create Profile Data (to generate hash)
        profile_data = UserProfileData(
            profession=profession,
            industry=industry,
            experience_level=experience_level,
            daily_responsibilities=[],
            pain_points=[],
            typical_outputs=[],
            technical_comfort_level="Medium",
            learning_style_notes="",
            professional_goals=[],
            safety_priorities=[],
            high_stakes_areas=[]
        )
        
        profile_hash = LessonCacheService.generate_profile_hash(profile_data)
        print(f"   Profile Hash: {profile_hash}")

        # 2. Query Cache (Same logic as lessons.py)
        statement = select(LessonCache).where(
            LessonCache.course_id == "c_llm_foundations",
            LessonCache.lesson_id == lesson_id,
            LessonCache.difficulty_level == difficulty,
            LessonCache.profile_hash == profile_hash,
            LessonCache.adaptation_context == adaptation
        ).order_by(LessonCache.created_at.desc())
        
        entry = db.exec(statement).first()

        print("\n🏁 Use Case Result:")
        if entry and entry.video_url:
            print(f"   ✅ CACHE HIT!")
            print(f"   Video URL: {entry.video_url}")
            print(f"   Created At: {entry.created_at}")
            print(f"   Model: {entry.llm_model}")
            print(f"   Adaptation Context: {entry.adaptation_context}")
        else:
            print(f"   ❌ CACHE MISS")
            print("   Checking Manifest fallback...")
            
            # --- MANIFEST FALLBACK LOGIC ---
            import json
            manifest_path = START_DIR / "src/vina_backend/domain/constants/video_manifest.json"
            if manifest_path.exists():
                with open(manifest_path, "r") as f:
                    manifest = json.load(f)
                
                # Normalize lookups
                prof_str = profession.lower().replace(" ", "_").replace("/", "_")
                diff_str = f"d{difficulty}"
                
                candidates = []
                for key, url in manifest.items():
                    if lesson_id in key:
                        score = 0
                        if prof_str and prof_str in key.lower():
                            score += 3
                        if diff_str in key:
                            score += 2
                        candidates.append((score, url, key))
                
                candidates.sort(key=lambda x: x[0], reverse=True)
                
                if candidates:
                    print(f"   ✅ MANIFEST MATCH: {candidates[0][2]}")
                    print(f"   Fallback URL: {candidates[0][1]}")
                else:
                    # Final fallback: ANY video for this lesson
                    fallback = [u for k, u in manifest.items() if lesson_id in k]
                    if fallback:
                        print(f"   ⚠️ GENERIC MANIFEST MATCH (No profile match)")
                        print(f"   Fallback URL: {fallback[0]}")
                    else:
                        print("   ❌ NO MANIFEST MATCH")
            else:
                print("   ❌ Manifest file not found")

if __name__ == "__main__":
    print("--- 1. Checking ORIGINAL (No Adaptation) ---")
    check_video_served(
        lesson_id="l01_what_llms_are",
        profession="HR Manager",
        difficulty=3,
        adaptation=None, # DEFAULT
        industry="Tech Company" 
    )

    print("\n--- 2. Checking ADAPTED (More Examples) ---")
    check_video_served(
        lesson_id="l01_what_llms_are",
        profession="HR Manager",
        difficulty=3,
        adaptation="examples", # NEW
        industry="Tech Company" 
    )
