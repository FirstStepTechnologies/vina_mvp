"""
Validate that all configuration and profile generation works.
Run this before starting Learner State implementation.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from vina_backend.services.course_loader import (
    load_global_config,
    load_course_config,
    get_lesson_config,
    get_difficulty_knobs,
    get_pedagogical_stage
)
from vina_backend.services.profile_builder import generate_user_profile
from vina_backend.utils.logging import setup_logging

def validate_configs():
    """Validate all configurations load correctly."""
    print("🔍 Validating Configurations...")
    
    # 1. Global config
    try:
        global_config = load_global_config()
        assert "global_difficulty_framework" in global_config
        assert "global_adaptation_rules" in global_config
        print("  ✅ Global config loaded")
    except Exception as e:
        print(f"  ❌ Global config failed: {e}")
        return False
    
    # 2. Course config
    try:
        course_config = load_course_config("c_llm_foundations")
        assert "lessons" in course_config
        assert len(course_config["lessons"]) == 17
        print("  ✅ Course config loaded (17 lessons)")
    except Exception as e:
        print(f"  ❌ Course config failed: {e}")
        return False
    
    # 3. Lesson config
    try:
        lesson = get_lesson_config("c_llm_foundations", "l01_what_llms_are")
        assert "what_learners_will_understand" in lesson
        print("  ✅ Lesson config loaded")
    except Exception as e:
        print(f"  ❌ Lesson config failed: {e}")
        return False
    
    # 4. Difficulty knobs
    try:
        knobs = get_difficulty_knobs(3)
        assert "delivery_metrics" in knobs
        print("  ✅ Difficulty knobs loaded")
    except Exception as e:
        print(f"  ❌ Difficulty knobs failed: {e}")
        return False
    
    # 5. Pedagogical stage (optional)
    try:
        stage = get_pedagogical_stage("c_llm_foundations", "l01_what_llms_are")
        if stage is not None:
            assert stage["stage_name"] == "stage_1_foundations"
            print("  ✅ Pedagogical stage detected")
        else:
            print("  ⚠️  Pedagogical stage not configured (optional)")
    except Exception as e:
        print(f"  ❌ Pedagogical stage failed: {e}")
        return False
    
    return True


def validate_profile_generation():
    """Validate profile generation works."""
    print("\n🔍 Validating Profile Generation...")
    
    try:
        profile = generate_user_profile(
            "Clinical Researcher",
            "Pharma/Biotech",
            "Intermediate"
        )
        
        # Check new fields
        assert len(profile.safety_priorities) >= 2
        assert len(profile.high_stakes_areas) >= 2
        
        print("  ✅ Profile generated with safety fields")
        print(f"     Safety priorities: {len(profile.safety_priorities)}")
        print(f"     High-stakes areas: {len(profile.high_stakes_areas)}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Profile generation failed: {e}")
        return False


if __name__ == "__main__":
    setup_logging()
    
    print("="*80)
    print("🧪 Pre-Learner State Validation")
    print("="*80)
    
    config_ok = validate_configs()
    profile_ok = validate_profile_generation()
    
    print("\n" + "="*80)
    if config_ok and profile_ok:
        print("✅ All validations passed! Ready for Learner State implementation.")
    else:
        print("❌ Some validations failed. Fix issues before proceeding.")
    print("="*80)