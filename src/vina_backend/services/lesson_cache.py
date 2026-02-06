"""
Lesson caching service to avoid regenerating identical lessons.
"""
import hashlib
import json
import logging
from typing import Optional, Dict
from datetime import datetime
from sqlmodel import Session, select, SQLModel, Field

from vina_backend.domain.schemas.profile import UserProfileData
from vina_backend.domain.schemas.lesson import LessonContent

logger = logging.getLogger(__name__)


class LessonCache(SQLModel, table=True):
    """Database model for cached lessons."""
    
    __tablename__ = "lesson_cache"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    cache_key: str = Field(unique=True, index=True)
    course_id: str = Field(index=True)
    lesson_id: str = Field(index=True)
    llm_model: str = Field(index=True)  # Added to compare models
    difficulty_level: int
    profile_hash: str
    
    # Traceability for QA - Snapshots
    initial_lesson_json: Optional[str] = None  # Snapshot after Agent 1
    review_json: Optional[str] = None         # Snapshot after Agent 2
    lesson_json: str                           # Final JSON string
    
    # Traceability for QA - Prompts
    gen_prompt: Optional[str] = None
    rev_prompt: Optional[str] = None
    rew_prompt: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    accessed_at: datetime = Field(default_factory=datetime.utcnow)
    access_count: int = Field(default=0)


class LessonCacheService:
    """Service for caching generated lessons."""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
    
    @staticmethod
    def generate_profile_hash(user_profile: UserProfileData) -> str:
        """7-character hash of profile."""
        profile_string = f"{user_profile.profession}:{user_profile.industry}:{user_profile.experience_level}"
        return hashlib.md5(profile_string.encode()).hexdigest()[:7]
    
    @staticmethod
    def generate_cache_key(
        course_id: str,
        lesson_id: str,
        difficulty_level: int,
        profile_hash: str,
        llm_model: str
    ) -> str:
        """Cache key including model for QA comparison."""
        return f"{course_id}:{lesson_id}:d{difficulty_level}:{llm_model}:{profile_hash}"
    
    def get(
        self,
        course_id: str,
        lesson_id: str,
        difficulty_level: int,
        user_profile: UserProfileData,
        llm_model: str
    ) -> Optional[Dict]:
        """Retrieve cached lesson for a specific model."""
        profile_hash = self.generate_profile_hash(user_profile)
        cache_key = self.generate_cache_key(course_id, lesson_id, difficulty_level, profile_hash, llm_model)
        
        statement = select(LessonCache).where(LessonCache.cache_key == cache_key)
        cached_entry = self.db_session.exec(statement).first()
        
        if cached_entry:
            cached_entry.accessed_at = datetime.utcnow()
            cached_entry.access_count += 1
            self.db_session.add(cached_entry)
            self.db_session.commit()
            
            return {
                "lesson_content": json.loads(cached_entry.lesson_json),
                "audit_trail": {
                    "gen_prompt": cached_entry.gen_prompt,
                    "gen_output": json.loads(cached_entry.initial_lesson_json) if cached_entry.initial_lesson_json else None,
                    "rev_prompt": cached_entry.rev_prompt,
                    "rev_output": json.loads(cached_entry.review_json) if cached_entry.review_json else None,
                    "rew_prompt": cached_entry.rew_prompt,
                    "rew_output": json.loads(cached_entry.lesson_json) if cached_entry.rew_prompt else None
                }
            }
        
        return None
    
    def set(
        self,
        course_id: str,
        lesson_id: str,
        difficulty_level: int,
        user_profile: UserProfileData,
        llm_model: str,
        lesson_content: Dict,
        initial_lesson: Optional[Dict] = None,
        review_result: Optional[Dict] = None,
        gen_prompt: Optional[str] = None,
        rev_prompt: Optional[str] = None,
        rew_prompt: Optional[str] = None
    ) -> None:
        """Cache a lesson with intermediate snapshots for QA."""
        profile_hash = self.generate_profile_hash(user_profile)
        cache_key = self.generate_cache_key(course_id, lesson_id, difficulty_level, profile_hash, llm_model)
        
        statement = select(LessonCache).where(LessonCache.cache_key == cache_key)
        existing = self.db_session.exec(statement).first()
        
        lesson_json = json.dumps(lesson_content)
        initial_json = json.dumps(initial_lesson) if initial_lesson else None
        rev_json = json.dumps(review_result) if review_result else None
        
        if existing:
            existing.lesson_json = lesson_json
            existing.initial_lesson_json = initial_json
            existing.review_json = rev_json
            existing.gen_prompt = gen_prompt
            existing.rev_prompt = rev_prompt
            existing.rew_prompt = rew_prompt
            existing.accessed_at = datetime.utcnow()
            self.db_session.add(existing)
        else:
            cache_entry = LessonCache(
                cache_key=cache_key,
                course_id=course_id,
                lesson_id=lesson_id,
                llm_model=llm_model,
                difficulty_level=difficulty_level,
                profile_hash=profile_hash,
                lesson_json=lesson_json,
                initial_lesson_json=initial_json,
                review_json=rev_json,
                gen_prompt=gen_prompt,
                rev_prompt=rev_prompt,
                rew_prompt=rew_prompt
            )
            self.db_session.add(cache_entry)
        
        self.db_session.commit()
        
        # Ensure it's persisted for immediate subsequent reads
        if existing:
            self.db_session.refresh(existing)
        else:
            # We don't strictly need to refresh cache_entry here but it's good practice
            pass
    
    def invalidate(
        self,
        course_id: Optional[str] = None,
        lesson_id: Optional[str] = None
    ) -> int:
        """
        Invalidate cached lessons.
        
        Args:
            course_id: If provided, invalidate all lessons for this course
            lesson_id: If provided (with course_id), invalidate specific lesson
        
        Returns:
            Number of entries deleted
        """
        if course_id and lesson_id:
            statement = select(LessonCache).where(
                LessonCache.course_id == course_id,
                LessonCache.lesson_id == lesson_id
            )
        elif course_id:
            statement = select(LessonCache).where(LessonCache.course_id == course_id)
        else:
            # Invalidate all
            statement = select(LessonCache)
        
        entries = self.db_session.exec(statement).all()
        count = len(entries)
        
        for entry in entries:
            self.db_session.delete(entry)
        
        self.db_session.commit()
        
        logger.info(f"Invalidated {count} cache entries")
        return count
    
    def get_cache_stats(self, course_id: Optional[str] = None) -> Dict:
        """
        Get cache statistics.
        
        Args:
            course_id: Optional course to filter by
        
        Returns:
            Dictionary with cache statistics
        """
        if course_id:
            statement = select(LessonCache).where(LessonCache.course_id == course_id)
        else:
            statement = select(LessonCache)
        
        entries = self.db_session.exec(statement).all()
        
        if not entries:
            return {
                "total_entries": 0,
                "total_accesses": 0,
                "avg_accesses_per_entry": 0,
                "most_accessed_lesson": None
            }
        
        total_accesses = sum(entry.access_count for entry in entries)
        most_accessed = max(entries, key=lambda e: e.access_count)
        
        return {
            "total_entries": len(entries),
            "total_accesses": total_accesses,
            "avg_accesses_per_entry": round(total_accesses / len(entries), 2),
            "most_accessed_lesson": {
                "lesson_id": most_accessed.lesson_id,
                "difficulty": most_accessed.difficulty_level,
                "access_count": most_accessed.access_count
            }
        }
