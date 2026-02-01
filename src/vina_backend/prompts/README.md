# Prompts

This directory contains all LLM prompt templates used in the application.

## Organization

- `profile/` - User profile generation prompts
- `lesson/` - Lesson content generation, review, and rewriting
- `quiz/` - Quiz generation and validation

## Editing Prompts

Prompts use Python `str.format()` style placeholders: `{variable_name}`

When editing:
1. Test changes locally with `scripts/test_profile_gen.py`
2. Verify JSON output structure hasn't changed
3. Check that all placeholders are still populated in code

## Versioning

Major prompt changes should be documented in git commit messages.
Example: "Improve profile generation to include typical_outputs field"