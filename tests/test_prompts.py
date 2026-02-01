# tests/test_prompts.py
def test_prompt_has_required_placeholders():
    """Ensure prompt template has all required placeholders."""
    with open("src/vina_backend/prompts/profile/user_profile_gen.md") as f:
        prompt = f.read()
    
    required = ["{profession}", "{industry}", "{experience_level}"]
    for placeholder in required:
        assert placeholder in prompt, f"Missing placeholder: {placeholder}"