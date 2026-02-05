# Vina LLM Benchmark Report
Generated on: 2026-02-05 15:19:06

## Summary Table
| Model | Success | Latency | Pass 1st | Rewrites | Judge Score |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Gemini 3 Flash | ❌ ERROR | - | - | - | - |
| GPT-4o Mini | ❌ ERROR | - | - | - | - |

## Detailed Analysis

### Gemini 3 Flash
- ❌ ERROR: Failed to parse LLM response as JSON: Expecting property name enclosed in double quotes: line 6 column 21 (char 198)
Provider: gemini, Model: gemini-2.5-flash
Response was: ```json
{
  "lesson_id": "l01_what_llms_are",
  "course_id": "c_llm_foundations",
  "difficulty_level": 3,
  "lesson_title": "Understanding LLMs: Your First Look at AI Text Generation",
  "total_slides": 4,...

### GPT-4o Mini
- ❌ ERROR: Failed to parse LLM response as JSON: Expecting property name enclosed in double quotes: line 6 column 21 (char 199)
Provider: gemini, Model: gemini-2.5-flash
Response was: ```json
{
  "lesson_id": "l01_what_llms_are",
  "course_id": "c_llm_foundations",
  "difficulty_level": 3,
  "lesson_title": "Understanding LLMs: Pattern Prediction, Not Fact Retrieval",
  "total_slides": 4,...