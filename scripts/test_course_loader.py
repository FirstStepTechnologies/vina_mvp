import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from vina_backend.services.course_loader import load_full_course_config, get_difficulty_knobs

try:
    # Test loading
    config = load_full_course_config("c_llm_foundations")
    print(f"✅ Loaded course: {config['course']['course_name']}")
    print(f"✅ Global config keys: {list(config['global'].keys())}")
    
    # Test difficulty knobs
    knobs = get_difficulty_knobs(3)
    print(f"✅ Difficulty 3 label: {knobs['label']}")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
