# Managing Practice Content Workflows

This document explains how to use the CLI tools to generate and manage the "Let's Practice" question bank.

## 1. Initial Generation (All Professions)
Run this command to generate the first batch of practice questions for a set of lessons across **all target professions** (HR, Product, Engineering, Sales).

```bash
# Generate questions for Lesson 1 to Lesson 3
uv run scripts/generate_practice_questions.py --start 1 --end 3
```

This will:
1.  Check `src/vina_backend/domain/constants/practice_questions.json`.
2.  Skip any lesson/profession combination that already has 10+ questions.
3.  Generate valid questions for any missing combinations.

## 2. Regenerate/Update Specific Content
If you update the prompts or fix a bug and need to regenerate questions for a specific lesson or profession, use the `--overwrite` flag.

```bash
# Force regenerate Lesson 1 for HR Managers only
uv run scripts/generate_practice_questions.py --start 1 --end 1 --profession "HR Manager" --overwrite
```

## 3. Targeted Generation
To generate content for a specific profession without checking/touching others:

```bash
# Generate Lesson 2 for Sales Representatives
uv run scripts/generate_practice_questions.py --start 2 --end 2 --profession "Sales Representative"
```

## 4. Verify Content Integrity
After generating questions, run the verification script to ensure the API can serve them correctly.

```bash
uv run scripts/verify_practice_feature.py
```

## Troubleshooting
*   **"No lessons found"**: Ensure your `start` and `end` arguments match valid lesson IDs (e.g., `l01_...` matches --start 1).
*   **"Skipping... Found 10 questions"**: The script defaults to skipping existing content to save tokens. Use `--overwrite` if you intend to replace them.
*   **Empty API Response**: If `GET /daily` returns `[]`, it means no questions exist for that user's profession in the JSON file. Run the generator for that profession.
