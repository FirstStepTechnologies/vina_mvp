"""
Test script for Lesson Generation Pipeline.
Tests the 3-agent system (Generator → Reviewer → Rewriter) with caching.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import json
from vina_backend.utils.logging import setup_logging
from vina_backend.integrations.db.engine import init_db, get_session
from vina_backend.services.profile_builder import get_or_create_user_profile
from vina_backend.integrations.db.repositories.profile_repository import ProfileRepository
from vina_backend.services.lesson_cache import LessonCacheService
from vina_backend.services.lesson_generator import LessonGenerator

import logging
logger = logging.getLogger(__name__)


def test_lesson_generation():
    """Test generating a lesson for a specific user profile."""
    print("\n" + "="*80)
    print("🧪 Test 1: Lesson Generation (First Time - No Cache)")
    print("="*80)
    
    session_gen = get_session()
    db_session = next(session_gen)
    
    try:
        # 1. Get or create user profile
        profile = get_or_create_user_profile(
            "Clinical Researcher",
            "Pharma/Biotech",
            "Intermediate"
        )
        
        print(f"\n  📋 User Profile:")
        print(f"     Profession: {profile.profession}")
        print(f"     Industry: {profile.industry}")
        print(f"     Experience: {profile.experience_level}")
        print(f"     Safety Priorities: {', '.join(profile.safety_priorities[:2])}...")
        
        # 2. Initialize services
        cache_service = LessonCacheService(db_session)
        generator = LessonGenerator(cache_service)
        
        # 3. Generate lesson
        print(f"\n  🎬 Generating Lesson: l01_what_llms_are (Difficulty 3)")
        
        generated_lesson = generator.generate_lesson(
            lesson_id="l01_what_llms_are",
            course_id="c_llm_foundations",
            user_profile=profile,
            difficulty_level=3
        )
        
        # 4. Display results
        print(f"\n  ✅ Lesson Generated Successfully!")
        print(f"\n  📊 Generation Metadata:")
        print(f"     Cache Hit: {generated_lesson.generation_metadata.cache_hit}")
        print(f"     LLM Model: {generated_lesson.generation_metadata.llm_model}")
        print(f"     Generation Time: {generated_lesson.generation_metadata.generation_time_seconds}s")
        print(f"     Review Passed First Time: {generated_lesson.generation_metadata.review_passed_first_time}")
        print(f"     Rewrite Count: {generated_lesson.generation_metadata.rewrite_count}")
        print(f"     Quality Score: {generated_lesson.generation_metadata.quality_score}/10")
        
        print(f"\n  📝 Lesson Content:")
        print(f"     Title: {generated_lesson.lesson_content.lesson_title}")
        print(f"     Slide Count: {len(generated_lesson.lesson_content.slides)}")
        
        for slide in generated_lesson.lesson_content.slides:
            print(f"\n     Slide {slide.slide_number} ({slide.slide_type}):")
            print(f"       Title: {slide.title}")
            print(f"       Items: {len(slide.items)}")
            for i, item in enumerate(slide.items, 1):
                print(f"         Item {i} ({item.type}): {item.bullet[:50]}...")
            if slide.duration_seconds:
                print(f"       Duration: {slide.duration_seconds}s")
        
        return generated_lesson, profile
        
    finally:
        db_session.close()


def test_cache_hit():
    """Test that regenerating the same lesson returns cached version."""
    print("\n" + "="*80)
    print("🧪 Test 2: Cache Hit (Regenerating Same Lesson)")
    print("="*80)
    
    session_gen = get_session()
    db_session = next(session_gen)
    
    try:
        # Get same profile
        profile = get_or_create_user_profile(
            "Clinical Researcher",
            "Pharma/Biotech",
            "Intermediate"
        )
        
        # Initialize services
        cache_service = LessonCacheService(db_session)
        generator = LessonGenerator(cache_service)
        
        # Generate same lesson
        print(f"\n  🔄 Regenerating l01_what_llms_are (should hit cache)")
        
        generated_lesson = generator.generate_lesson(
            lesson_id="l01_what_llms_are",
            course_id="c_llm_foundations",
            user_profile=profile,
            difficulty_level=3
        )
        
        # Verify cache hit
        if generated_lesson.generation_metadata.cache_hit:
            print(f"\n  ✅ Cache HIT! (No LLM calls made)")
            print(f"     Generation Time: {generated_lesson.generation_metadata.generation_time_seconds}s")
            return True
        else:
            print(f"\n  ❌ Cache MISS (unexpected)")
            return False
        
    finally:
        db_session.close()


def test_different_difficulty():
    """Test generating same lesson at different difficulty."""
    print("\n" + "="*80)
    print("🧪 Test 3: Different Difficulty Level (Cache Miss Expected)")
    print("="*80)
    
    session_gen = get_session()
    db_session = next(session_gen)
    
    try:
        profile = get_or_create_user_profile(
            "Clinical Researcher",
            "Pharma/Biotech",
            "Intermediate"
        )
        
        cache_service = LessonCacheService(db_session)
        generator = LessonGenerator(cache_service)
        
        # Generate at difficulty 1 (Guided)
        print(f"\n  🎬 Generating l01_what_llms_are at Difficulty 1 (Guided)")
        
        generated_lesson = generator.generate_lesson(
            lesson_id="l01_what_llms_are",
            course_id="c_llm_foundations",
            user_profile=profile,
            difficulty_level=1
        )
        
        print(f"\n  📊 Results:")
        print(f"     Cache Hit: {generated_lesson.generation_metadata.cache_hit}")
        print(f"     Slide Count: {len(generated_lesson.lesson_content.slides)}")
        print(f"     Quality Score: {generated_lesson.generation_metadata.quality_score}/10")
        
        # Difficulty 1 should have more slides (5-6 vs 4-5 for difficulty 3)
        slide_count = len(generated_lesson.lesson_content.slides)
        expected_more_slides = slide_count >= 5
        
        if expected_more_slides:
            print(f"\n  ✅ Difficulty 1 has {slide_count} slides (expected 5-6)")
        else:
            print(f"\n  ⚠️  Difficulty 1 has {slide_count} slides (expected 5-6)")
        
        return expected_more_slides
        
    finally:
        db_session.close()


def test_cache_stats():
    """Test cache statistics."""
    print("\n" + "="*80)
    print("🧪 Test 4: Cache Statistics")
    print("="*80)
    
    session_gen = get_session()
    db_session = next(session_gen)
    
    try:
        cache_service = LessonCacheService(db_session)
        stats = cache_service.get_cache_stats(course_id="c_llm_foundations")
        
        print(f"\n  📊 Cache Stats for c_llm_foundations:")
        print(f"     Total Entries: {stats['total_entries']}")
        print(f"     Total Accesses: {stats['total_accesses']}")
        print(f"     Avg Accesses Per Entry: {stats['avg_accesses_per_entry']}")
        
        if stats['most_accessed_lesson']:
            print(f"\n     Most Accessed Lesson:")
            print(f"       Lesson ID: {stats['most_accessed_lesson']['lesson_id']}")
            print(f"       Difficulty: {stats['most_accessed_lesson']['difficulty']}")
            print(f"       Access Count: {stats['most_accessed_lesson']['access_count']}")
        
        return stats['total_entries'] > 0
        
    finally:
        db_session.close()


def test_different_profile():
    """Test that different profile generates different lesson."""
    print("\n" + "="*80)
    print("🧪 Test 5: Different User Profile (Cache Miss Expected)")
    print("="*80)
    
    session_gen = get_session()
    db_session = next(session_gen)
    
    try:
        # Different profile
        profile = get_or_create_user_profile(
            "HR Manager",
            "Technology",
            "Intermediate"
        )
        
        print(f"\n  📋 Different Profile:")
        print(f"     Profession: {profile.profession}")
        print(f"     Industry: {profile.industry}")
        
        cache_service = LessonCacheService(db_session)
        generator = LessonGenerator(cache_service)
        
        print(f"\n  🎬 Generating l01_what_llms_are for HR Manager")
        
        generated_lesson = generator.generate_lesson(
            lesson_id="l01_what_llms_are",
            course_id="c_llm_foundations",
            user_profile=profile,
            difficulty_level=3
        )
        
        print(f"\n  📊 Results:")
        print(f"     Cache Hit: {generated_lesson.generation_metadata.cache_hit}")
        print(f"     Quality Score: {generated_lesson.generation_metadata.quality_score}/10")
        
        # Check for profession-specific content
        lesson_json = json.dumps(generated_lesson.lesson_content.model_dump())
        has_hr_context = "HR" in lesson_json or "hiring" in lesson_json.lower() or "recruitment" in lesson_json.lower()
        
        if has_hr_context:
            print(f"\n  ✅ Lesson contains HR-specific context")
        else:
            print(f"\n  ⚠️  Lesson may not have HR-specific examples")
        
        return not generated_lesson.generation_metadata.cache_hit
        
    finally:
        db_session.close()


if __name__ == "__main__":
    setup_logging()
    
    print("="*80)
    print("🧪 Lesson Generation Pipeline Tests")
    print("="*80)
    
    # Initialize database
    init_db()
    
    # Run tests
    try:
        test_1_result, profile = test_lesson_generation()
        test_2_result = test_cache_hit()
        test_3_result = test_different_difficulty()
        test_4_result = test_cache_stats()
        test_5_result = test_different_profile()
        
        # Summary
        print("\n" + "="*80)
        print("📊 Test Summary")
        print("="*80)
        print(f"  {'✅' if test_1_result else '❌'} Test 1: Initial Lesson Generation")
        print(f"  {'✅' if test_2_result else '❌'} Test 2: Cache Hit")
        print(f"  {'✅' if test_3_result else '❌'} Test 3: Different Difficulty")
        print(f"  {'✅' if test_4_result else '❌'} Test 4: Cache Statistics")
        print(f"  {'✅' if test_5_result else '❌'} Test 5: Different Profile")
        
        all_passed = all([test_1_result, test_2_result, test_3_result, test_4_result, test_5_result])
        
        print("\n" + "="*80)
        if all_passed:
            print("✅ All tests passed! Lesson generation pipeline is working correctly.")
        else:
            print("⚠️  Some tests had issues. Review the output above.")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
