"""
Quick test to verify the updated prompts load correctly.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from jinja2 import Template

PROMPTS_DIR = Path(__file__).parent.parent / "src" / "vina_backend" / "prompts" / "lesson"

def test_template_loading():
    """Test that all three prompt templates load without syntax errors."""
    
    templates = {
        "generator": "generator_prompt.md",
        "reviewer": "reviewer_prompt.md",
        "rewriter": "rewriter_prompt.md"
    }
    
    print("🧪 Testing Prompt Template Loading\n")
    print("="*60)
    
    all_passed = True
    
    for name, filename in templates.items():
        try:
            template_path = PROMPTS_DIR / filename
            with open(template_path, 'r') as f:
                template = Template(f.read())
            print(f"✅ {name.capitalize()} prompt loaded successfully")
        except Exception as e:
            print(f"❌ {name.capitalize()} prompt failed: {e}")
            all_passed = False
    
    print("="*60)
    
    if all_passed:
        print("\n✅ All prompt templates are valid!")
        return 0
    else:
        print("\n❌ Some templates have errors")
        return 1

if __name__ == "__main__":
    exit(test_template_loading())
