# Feature Implementation Report: Generic Multi-Agent Onboarding Quiz

**Date:** 2026-02-07
**Status:** ✅ Implemented, Verified & Optimized

## 1. Overview
The **Onboarding Quiz** is a critical feature that determines a user's starting point in the curriculum based on their prior knowledge. We have implemented a **Generic Multi-Agent Pipeline** that allows the system to generate high-quality, profession-specific placement quizzes for *any* course by dynamically analyzing the curriculum configuration.

## 2. Problem Solved
1.  **Static Logic**: Initial implementations were hardcoded for the "LLM Foundations" course, making it difficult to scale to other courses.
2.  **Quality Control**: Single-pass generation often resulted in questions that didn't follow the difficulty curve or failed to map to valid lesson IDs.
3.  **Indiscrepancy in Code Structure**: Logic and prompts were scattered across scripts and services.

## 3. Technical Implementation

### A. Multi-Agent Pipeline (`src/vina_backend/services/agents/`)
We deployed a 3-agent orchestration pattern:
*   **`QuizGeneratorAgent`**: Acts as a "Master Technical Educator". It uses the curriculum structure to draft 5 questions with a strict difficulty progression (1-5).
*   **`QuizReviewerAgent`**: Acts as a "Quality Assurance Expert". It evaluates the draft against a 6-point rubric (Difficulty, Profession Context, Answer Quality, Concept Diversity, Lesson Mapping, Explanation Quality).
*   **`QuizRewriterAgent`**: Acts as a "Quiz Improvement Specialist". It fixes specific issues identified by the reviewer while preserving valid elements.

### B. Prompt Engineering (`src/vina_backend/prompts/quiz/`)
Prompts were moved from Python strings to **external Markdown templates** using Jinja2:
*   `generator.md`: Defines the persona and structural rules.
*   `reviewer.md`: Contains the rubric and Pass/Fail logic.
*   `rewriter.md`: Provides instructions for targeted revisions.
*   **Genericity**: Prompts use dynamic variables (`{{course_name}}`, `{{curriculum_guidance}}`) making them course-agnostic.

### C. Dynamic Curriculum Analysis
The generation script (`scripts/generate_onboarding_quizzes.py`) now includes an `analyze_curriculum` function that:
*   Parses `pedagogical_progression` from the course JSON.
*   Maps stages to specific question slots (e.g., Stage 1 -> Q1, Q2).
*   Extracts concepts and valid lesson IDs to guide the agents.

### D. Scoring & Placement Engine (`src/vina_backend/services/quiz_engine.py`)
A dedicated engine calculates results and maps scores to starting lessons:
*   **0-1 Correct**: Start at `l01_what_llms_are` (Foundations).
*   **2-3 Correct**: Start at `l04_where_llms_excel` (Application).
*   **4-5 Correct**: Start at `l11_cloud_apis` (Mastery).

### E. API Endpoints (`src/vina_backend/api/routers/onboarding.py`)
*   `GET /api/v1/onboarding/quiz/{profession}`: Retrieves the pre-generated "Gold Standard" quiz.
*   `POST /api/v1/onboarding/submit`: Grades the user and returns the placement result.

## 4. Verification & Reliability
*   **Automated Tests**: Implemented `tests/test_onboarding_quiz.py` covering:
    *   Dynamic fetch of quizzes.
    *   Accurate scoring for low and high performers.
    *   Error handling for invalid professions.
*   **Validation**: All generated quizzes pass Pydantic validation (`ProfessionQuiz` model) ensuring schema compliance (e.g., `camelCase` fields for frontend).
*   **Success Rate**: The review loop ensures that 100% of the final output maps to valid lesson IDs and follows the progression curve.

## 5. File Structure
```text
src/vina_backend/
├── api/routers/onboarding.py    # API Router
├── domain/
│   ├── schemas/quiz.py          # Pydantic Models
│   └── constants/enums.py       # Profession Enums
├── prompts/quiz/                # External Prompt Templates
└── services/
    ├── agents/                  # Generator/Reviewer/Rewriter
    └── quiz_engine.py           # Scoring Logic
```

---
**Prepared By:** Antigravity (AI Coding Assistant)
**Consolidated From:** `Implementation Plan`, `Task logs`, and `test_onboarding_quiz.py`.
