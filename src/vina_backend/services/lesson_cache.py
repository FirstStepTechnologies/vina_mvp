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
    difficulty_level: int
    profile_hash: str
    lesson_json: str  # JSON string of LessonContent
    created_at: datetime = Field(default_factory=datetime.utcnow)
    accessed_at: datetime = Field(default_factory=datetime.utcnow)
    access_count: int = Field(default=0)


class LessonCacheService:
    """Service for caching generated lessons."""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
    
    @staticmethod
    def generate_profile_hash(user_profile: UserProfileData) -> str:
        """
        Generate a hash from user profile for cache key.
        
        Args:
            user_profile: User profile data
        
        Returns:
            7-character hash
        """
        profile_string = f"{user_profile.profession}:{user_profile.industry}:{user_profile.experience_level}"
        return hashlib.md5(profile_string.encode()).hexdigest()[:7]
    
    @staticmethod
    def generate_cache_key(
        course_id: str,
        lesson_id: str,
        difficulty_level: int,
        profile_hash: str
    ) -> str:
        """
        Generate cache key for a lesson.
        
        Args:
            course_id: Course identifier
            lesson_id: Lesson identifier
            difficulty_level: Difficulty level (1, 3, or 5)
            profile_hash: Hash of user profile
        
        Returns:
            Cache key string
        """
        return f"{course_id}:{lesson_id}:d{difficulty_level}:{profile_hash}"
    
    def get(
        self,
        course_id: str,
        lesson_id: str,
        difficulty_level: int,
        user_profile: UserProfileData
    ) -> Optional[Dict]:
        """
        Retrieve cached lesson if it exists.
        
        Args:
            course_id: Course identifier
            lesson_id: Lesson identifier
            difficulty_level: Difficulty level
            user_profile: User profile
        
        Returns:
            Lesson content dict if cached, None otherwise
        """
        profile_hash = self.generate_profile_hash(user_profile)
        cache_key = self.generate_cache_key(course_id, lesson_id, difficulty_level, profile_hash)
        
        statement = select(LessonCache).where(LessonCache.cache_key == cache_key)
        cached_entry = self.db_session.exec(statement).first()
        
        if cached_entry:
            # Update access metadata
            cached_entry.accessed_at = datetime.utcnow()
            cached_entry.access_count += 1
            self.db_session.add(cached_entry)
            self.db_session.commit()
            
            logger.info(
                f"Cache HIT for {cache_key} (accessed {cached_entry.access_count} times)"
            )
            
            return json.loads(cached_entry.lesson_json)
        
        logger.info(f"Cache MISS for {cache_key}")
        return None
    
    def set(
        self,
        course_id: str,
        lesson_id: str,
        difficulty_level: int,
        user_profile: UserProfileData,
        lesson_content: Dict
    ) -> None:
        """
        Cache a generated lesson.
        
        Args:
            course_id: Course identifier
            lesson_id: Lesson identifier
            difficulty_level: Difficulty level
            user_profile: User profile
            lesson_content: Lesson content to cache
        """
        profile_hash = self.generate_profile_hash(user_profile)
        cache_key = self.generate_cache_key(course_id, lesson_id, difficulty_level, profile_hash)
        
        # Check if already exists
        statement = select(LessonCache).where(LessonCache.cache_key == cache_key)
        existing = self.db_session.exec(statement).first()
        
        if existing:
            # Update existing entry
            existing.lesson_json = json.dumps(lesson_content)
            existing.created_at = datetime.utcnow()
            existing.accessed_at = datetime.utcnow()
            existing.access_count = 0
            self.db_session.add(existing)
            logger.info(f"Updated cache entry for {cache_key}")
        else:
            # Create new entry
            cache_entry = LessonCache(
                cache_key=cache_key,
                course_id=course_id,
                lesson_id=lesson_id,
                difficulty_level=difficulty_level,
                profile_hash=profile_hash,
                lesson_json=json.dumps(lesson_content)
            )
            self.db_session.add(cache_entry)
            logger.info(f"Created cache entry for {cache_key}")
        
        self.db_session.commit()
    
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
