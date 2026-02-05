"""
Test script to verify fallback generator prompt loads correctly.
"""
from pathlib import Path
from jinja2 import Template

# Path to prompts directory
PROMPTS_DIR = Path(__file__).parent.parent / "src" / "vina_backend" / "prompts" / "lesson"

def test_fallback_template():
    """Test that fallback generator template loads without errors."""
    template_path = PROMPTS_DIR / "fallback_generator.md"
    
    print(f"Loading template from: {template_path}")
    
    with open(template_path, 'r') as f:
        template_content = f.read()
    
    # Try to create Jinja2 template
    try:
        template = Template(template_content)
        print("✅ Template loaded successfully")
    except Exception as e:
        print(f"❌ Template loading failed: {e}")
        return False
    
    # Test rendering with sample data
    test_context = {
        "profession": "Clinical Researcher",
        "industry": "Pharma/Biotech",
        "experience_level": "Intermediate",
        "technical_comfort_level": "Moderate",
        "typical_outputs": ["Study protocols", "SAE narratives"],
        "daily_responsibilities": ["Protocol development", "Data review"],
        "pain_points": ["Manual documentation", "Compliance tracking"],
        "safety_priorities": ["GCP compliance", "Patient safety"],
        "high_stakes_areas": ["Adverse event reporting", "Regulatory submissions"],
        "lesson_id": "l01_what_llms_are",
        "course_id": "c_llm_foundations",
        "lesson_name": "What LLMs Are",
        "topic_group": "Foundations",
        "estimated_duration_minutes": 3,
        "what_learners_will_understand": [
            "What LLMs are and how they work",
            "Key limitations of LLMs"
        ],
        "misconceptions_to_address": [
            "LLMs know facts like a database",
            "LLMs always browse the web"
        ],
        "difficulty_level": 3
    }
    
    try:
        rendered = template.render(**test_context)
        print(f"✅ Template rendered successfully ({len(rendered)} characters)")
        print(f"\n📝 First 500 characters of rendered prompt:")
        print(rendered[:500])
        return True
    except Exception as e:
        print(f"❌ Template rendering failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 80)
    print("Testing Fallback Generator Prompt")
    print("=" * 80)
    success = test_fallback_template()
    print("=" * 80)
    if success:
        print("✅ All tests passed!")
    else:
        print("❌ Tests failed!")
