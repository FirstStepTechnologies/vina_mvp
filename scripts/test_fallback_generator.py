"""
Test script specifically for fallback lesson generation.

This script tests the fallback generator by directly calling it,
bypassing the primary generation workflow.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from vina_backend.services.lesson_generator import LessonGenerator
from vina_backend.services.profile_builder import get_or_create_user_profile
from vina_backend.utils.logging import setup_logging
from vina_backend.integrations.db.engine import init_db, get_session
from vina_backend.services.course_loader import get_lesson_config, get_difficulty_knobs, load_course_config

def test_fallback_generator():
    """Test the fallback generator directly."""
    
    print("=" * 80)
    print("🧪 Fallback Lesson Generator Test")
    print("=" * 80)
    
    # Initialize
    setup_logging()
    init_db()
    
    # Get user profile
    session_gen = get_session()
    session = next(session_gen)
    
    try:
        profile = get_or_create_user_profile(
            session=session,
            profession="Clinical Researcher",
            industry="Pharma/Biotech"
        )
    finally:
        session_gen.close()
    
    print(f"\n📋 User Profile:")
    print(f"   Profession: {profile.profession}")
    print(f"   Industry: {profile.industry}")
    print(f"   Experience: {profile.experience_level}")
    
    # Test parameters
    lesson_id = "l01_what_llms_are"
    course_id = "c_llm_foundations"
    difficulty_level = 3
    
    print(f"\n🎬 Testing Fallback Generator:")
    print(f"   Lesson: {lesson_id}")
    print(f"   Difficulty: {difficulty_level}")
    
    # Load context
    lesson_spec = get_lesson_config(course_id, lesson_id)
    difficulty_knobs = get_difficulty_knobs(difficulty_level)
    course_config = load_course_config(course_id)
    
    # Initialize generator
    generator = LessonGenerator(cache_service=None)  # No caching for test
    
    # Call fallback generator directly
    print(f"\n⏳ Generating fallback lesson...")
    
    try:
        fallback_lesson = generator._fallback_lesson(
            lesson_id=lesson_id,
            course_id=course_id,
            difficulty_level=difficulty_level,
            lesson_spec=lesson_spec,
            user_profile=profile,
            difficulty_knobs=difficulty_knobs,
            course_config=course_config
        )
        
        print(f"\n✅ Fallback Lesson Generated Successfully!")
        
        # Display results
        print(f"\n📊 Generation Metadata:")
        print(f"   Cache Hit: {fallback_lesson.generation_metadata.cache_hit}")
        print(f"   LLM Model: {fallback_lesson.generation_metadata.llm_model}")
        print(f"   Review Passed: {fallback_lesson.generation_metadata.review_passed_first_time}")
        print(f"   Rewrite Count: {fallback_lesson.generation_metadata.rewrite_count}")
        
        print(f"\n📝 Lesson Content:")
        print(f"   Title: {fallback_lesson.lesson_content.lesson_title}")
        print(f"   Slide Count: {len(fallback_lesson.lesson_content.slides)}")
        print(f"   Total Slides: {fallback_lesson.lesson_content.total_slides}")
        
        # Verify slide count matches difficulty
        expected_slides = 3 if difficulty_level <= 2 else (4 if difficulty_level == 3 else 5)
        actual_slides = len(fallback_lesson.lesson_content.slides)
        
        if actual_slides == expected_slides:
            print(f"   ✅ Slide count matches difficulty ({actual_slides} slides)")
        else:
            print(f"   ⚠️  Slide count mismatch: expected {expected_slides}, got {actual_slides}")
        
        # Display each slide
        for slide in fallback_lesson.lesson_content.slides:
            print(f"\n   Slide {slide.slide_number} ({slide.slide_type}):")
            print(f"     Title: {slide.title}")
            print(f"     Items: {len(slide.items)}")
            
            for i, item in enumerate(slide.items, 1):
                print(f"       Item {i} ({item.type}):")
                print(f"         Bullet: {item.bullet}")
                print(f"         Talk: {item.talk[:80]}..." if len(item.talk) > 80 else f"         Talk: {item.talk}")
                
                # Verify no figures
                if item.type == "figure":
                    print(f"         ❌ ERROR: Found figure in fallback lesson!")
                
                # Verify bullet length
                bullet_words = len(item.bullet.split())
                if bullet_words > 12:
                    print(f"         ⚠️  Bullet too long: {bullet_words} words (max 12)")
                
                # Verify talk length
                talk_words = len(item.talk.split())
                if len(slide.items) == 2:
                    if not (40 <= talk_words <= 55):
                        print(f"         ⚠️  Talk length: {talk_words} words (expected 40-55 for 2-item slide)")
                elif len(slide.items) == 3:
                    if not (30 <= talk_words <= 45):
                        print(f"         ⚠️  Talk length: {talk_words} words (expected 30-45 for 3-item slide)")
        
        # Check for profession-specific content
        all_text = " ".join([
            item.talk for slide in fallback_lesson.lesson_content.slides 
            for item in slide.items
        ])
        
        print(f"\n🔍 Content Analysis:")
        
        if profile.profession.lower() in all_text.lower():
            print(f"   ✅ Contains profession reference: {profile.profession}")
        else:
            print(f"   ⚠️  Missing profession reference: {profile.profession}")
        
        # Check for typical outputs
        typical_outputs_found = [
            output for output in profile.typical_outputs 
            if output.lower() in all_text.lower()
        ]
        if typical_outputs_found:
            print(f"   ✅ References typical outputs: {', '.join(typical_outputs_found[:2])}")
        else:
            print(f"   ⚠️  No typical output references found")
        
        # Check for safety language if high-stakes
        if profile.high_stakes_areas:
            safety_keywords = ["verify", "review", "oversight", "human", "check"]
            safety_found = [kw for kw in safety_keywords if kw in all_text.lower()]
            if safety_found:
                print(f"   ✅ Contains safety language: {', '.join(safety_found[:3])}")
            else:
                print(f"   ⚠️  Missing safety language for high-stakes areas")
        
        print(f"\n" + "=" * 80)
        print(f"✅ Fallback generator test completed successfully!")
        print(f"=" * 80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Fallback generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_different_difficulties():
    """Test fallback generator with different difficulty levels."""
    
    print("\n" + "=" * 80)
    print("🧪 Testing Fallback Generator Across Difficulty Levels")
    print("=" * 80)
    
    init_db()
    
    session_gen = get_session()
    session = next(session_gen)
    
    try:
        profile = get_or_create_user_profile(
            session=session,
            profession="HR Manager",
            industry="Technology"
        )
    finally:
        session_gen.close()
    
    lesson_id = "l01_what_llms_are"
    course_id = "c_llm_foundations"
    
    lesson_spec = get_lesson_config(course_id, lesson_id)
    course_config = load_course_config(course_id)
    generator = LessonGenerator(cache_service=None)
    
    results = []
    
    for difficulty in [1, 3, 5]:
        print(f"\n📊 Testing Difficulty {difficulty}:")
        
        difficulty_knobs = get_difficulty_knobs(difficulty)
        
        try:
            fallback = generator._fallback_lesson(
                lesson_id=lesson_id,
                course_id=course_id,
                difficulty_level=difficulty,
                lesson_spec=lesson_spec,
                user_profile=profile,
                difficulty_knobs=difficulty_knobs,
                course_config=course_config
            )
            
            expected_slides = 3 if difficulty <= 2 else (4 if difficulty == 3 else 5)
            actual_slides = len(fallback.lesson_content.slides)
            
            match = "✅" if actual_slides == expected_slides else "❌"
            print(f"   {match} Expected {expected_slides} slides, got {actual_slides}")
            print(f"   Title: {fallback.lesson_content.lesson_title}")
            
            results.append({
                "difficulty": difficulty,
                "expected": expected_slides,
                "actual": actual_slides,
                "success": actual_slides == expected_slides
            })
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            results.append({
                "difficulty": difficulty,
                "expected": None,
                "actual": None,
                "success": False
            })
    
    print(f"\n" + "=" * 80)
    print(f"📊 Summary:")
    for r in results:
        status = "✅" if r["success"] else "❌"
        print(f"   {status} Difficulty {r['difficulty']}: {r['actual']}/{r['expected']} slides")
    
    all_passed = all(r["success"] for r in results)
    if all_passed:
        print(f"\n✅ All difficulty levels passed!")
    else:
        print(f"\n⚠️  Some difficulty levels failed")
    
    print(f"=" * 80)
    
    return all_passed


if __name__ == "__main__":
    print("\n🚀 Starting Fallback Generator Tests\n")
    
    # Test 1: Basic fallback generation
    test1_passed = test_fallback_generator()
    
    # Test 2: Different difficulty levels
    test2_passed = test_different_difficulties()
    
    print(f"\n" + "=" * 80)
    print(f"📊 Final Results:")
    print(f"   Test 1 (Basic Generation): {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"   Test 2 (Difficulty Levels): {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print(f"\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  Some tests failed")
    
    print(f"=" * 80)
