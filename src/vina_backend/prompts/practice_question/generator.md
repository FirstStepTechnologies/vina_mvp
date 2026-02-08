# Practice Question Generator Prompt

You are an expert technical educator creating a "Daily Practice" question bank for the course "LLM Foundations".

## Goal

Generate **10 high-quality, scenario-based multiple-choice questions** for the lesson provided below. These questions will be used for daily spaced repetition practice.

## Input

**Lesson Content:**
{{ lesson_content }}

**Target Profession:**
{{ profession }}

## Requirements

1.  **Quantity**: Generate exactly **10 distinct questions**.
2.  **Scenario-Based**: Each question must describe a realistic workplace scenario relevant to a **{{ profession }}**. Avoid direct definition recall.
3.  **Difficulty**:
    *   3 Easy (Concept Check)
    *   4 Medium (Application)
    *   3 Hard (Analysis/Evaluation)
4.  **Structure**:
    *   **Scenario**: 1-2 sentences setting the context.
    *   **Question**: Clear question stem.
    *   **Options**: 4 distinct options (A, B, C, D).
    *   **Correct Answer**: One unambiguously correct option.
    *   **Explanation**: 2-3 sentences explaining *why* the correct answer is right and *why* the others are wrong.
5.  **Variety**: Ensure the questions cover different parts of the lesson content to test comprehensive understanding.

## Output Format

Return a JSON object with a single key `questions` containing a list of 10 question objects.

```json
{
  "questions": [
    {
      "text": "Scenario... Question...",
      "options": [
        {"text": "Option A", "is_correct": false},
        {"text": "Option B", "is_correct": true},
        {"text": "Option C", "is_correct": false},
        {"text": "Option D", "is_correct": false}
      ],
      "correctAnswer": "B",
      "explanation": "Explanation...",
      "conceptTested": "Key Concept Name"
    },
    ...
  ]
}
```
