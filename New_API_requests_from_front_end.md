# Vina Frontend-Backend API Handoff Specification

**Version**: 2.0
**Date**: October 26, 2023
**Status**: Ready for Implementation

This document outlines the exact API endpoints and data structures required to support the current Vina frontend implementation. The frontend currently mocks these interactions in `src/lib/api/service.ts` and persists state via `localStorage` in Context providers.

---

## 1. Authentication & Onboarding

### `POST /api/auth/register`
Creates a new user account and initializes their profile with default gamification stats.

*   **Request Body**:
    ```json
    {
      "email": "user@example.com",
      "password": "secureFromFrontend",
      "fullName": "New Learner"
    }
    ```
*   **Response (201 Created)**:
    ```json
    {
      "token": "jwt_token_string",
      "user": {
        "userId": "uuid-v4",
        "email": "user@example.com",
        "createdAt": "2023-10-26T10:00:00Z"
      }
    }
    ```

### `POST /api/onboarding/submit`
Submits the user's initial personalization responses. This triggers the initial pathway generation.

*   **Request Body**:
    ```json
    {
      "responses": {
        "role": "Product Manager",
        "industry": "Fintech",
        "experience": "Intermediate",
        "goal": "Strategic Overview"
        // ... other onboarding keys
      }
    }
    ```
*   **Response (200 OK)**:
    ```json
    {
      "success": true,
      "recommendedPathway": "strategy_pm_track"
    }
    ```

---

## 2. User Profile & Settings

### `GET /api/user/profile`
Fetches the user's core profile data, including their learning resolution.

*   **Response (200 OK)**:
    ```json
    {
      "userId": "uuid-v4",
      "profession": "Product Manager",
      "dailyGoalMinutes": 15,
      "resolution": "Mastering AI Strategy for 2026",
      "onboardingResponses": { ... },
      "createdAt": "2023-10-26T10:00:00Z"
    }
    ```

### `PATCH /api/user/profile`
Updates specific profile fields. Used when user edits their goal or resolution in the Profile section.

*   **Request Body** (Partial):
    ```json
    {
      "dailyGoalMinutes": 20,
      "resolution": "Updated resolution text..."
    }
    ```
*   **Response (200 OK)**: Returns updated user object.

### `POST /api/user/profile/reset-pathway`
**CRITICAL**: Triggered when a user changes their 'Job Role'. This performs a "Hard Reset" of their learning path.
*   **Action**: Backend must archive current progress and re-generate the course map based on the new role.
*   **Response (200 OK)**:
    ```json
    {
      "status": "reset_complete",
      "newCourseMapId": "map_id_new"
    }
    ```

---

## 3. Engagement & Gamification (The "Progress" Context)

The frontend manages a complex `VinaProgress` object. The backend needs to persist this state reliably.

### `GET /api/user/progress`
Fetches the complete gamification state for the Dashboard.

*   **Response (200 OK)**:
    ```json
    {
      "userId": "uuid-v4",
      "diamonds": 120, // Main currency
      "streak": 5,
      "minutesToday": 12,
      "minutesThisWeek": 45,
      "lastActiveDate": "2023-10-26",
      "tourCompleted": true, // Boolean for Vina Assistant status
      "currentTourStep": 9,
      "completedLessons": ["l01", "l02"],
      "dailyGoalHistory": {
        "2023-10-25": true,
        "2023-10-24": false
      }
    }
    ```

### `POST /api/user/progress/sync`
Periodic sync (or event-based) to update progress.
*   **Request Body**:
    ```json
    {
      "minutesAdded": 5,
      "diamondsEarned": 100, // e.g., from Resolution Bonus
      "action": "daily_goal_met" // optional context
    }
    ```

### `PATCH /api/user/tour`
Updates the implementation state of the Vina Assistant.
*   **Request Body**:
    ```json
    {
      "tourCompleted": true,
      "currentTourStep": 9
    }
    ```

---

## 4. Course Content & Lessons

### `GET /api/course/map`
Returns the list of lessons (nodes) for the user's tailored pathway.

*   **Response (200 OK)**: List of `Lesson` objects.
    ```json
    [
      {
        "lessonId": "l01_what_llms_are",
        "lessonNumber": 1,
        "lessonName": "What LLMs Are",
        "shortTitle": "What are LLMs?",
        "topicGroup": "The Foundations",
        "estimatedDuration": 3,
        "prerequisites": [],
        "status": "completed" // Backend computed field
      },
      // ...
    ]
    ```

### `GET /api/lesson/{id}`
Fetches details for a single lesson room.
*   **Response**:
    ```json
    {
      "lessonId": "l01...",
      "videoUrl": "https://...",
      "transcript": "...",
      "resources": [...]
    }
    ```

---

## 5. Quizzes & Validation

### `GET /api/lesson/{id}/quiz`
Fetches the quiz questions for a specific lesson.

*   **Response (200 OK)**: List of `QuizQuestion` objects.
    ```json
    [
      {
        "id": "q_l01_01",
        "questionText": "What does LLM stand for?",
        "options": ["A", "B", "C", "D"],
        "correctAnswer": "Large Language Model",
        "explanation": "..."
      }
    ]
    ```

### `POST /api/lesson/{id}/quiz/submit`
Submits answers for validation and scoring.

*   **Request Body**:
    ```json
    {
      "answers": {
        "q_l01_01": "Large Language Model",
        "q_l01_02": "Predicting tokens"
      }
    }
    ```
*   **Response (200 OK)**:
    ```json
    {
      "passed": true,
      "score": 100,
      "diamondsEarned": 50,
      "nextLessonUnlocked": "l02_tokens_context"
    }
    ```

---

## 6. Pre-Assessment

### `GET /api/assessment/pre`
Fetches the initial placement test questions.

### `POST /api/assessment/pre/submit`
Submits placement test results to determine the starting node.
*   **Response**:
    ```json
    {
      "startingLessonId": "l03_advanced_concepts",
      "initialDiamonds": 50
    }
    ```

---

## 7. AI Adaptation (Future Phase)

### `POST /api/adapt/lesson`
*   **Description**: Triggers the "Adapt" feature seen in the Lesson Room.
*   **Request**: `{ "lessonId": "...", "adaptationType": "simplify" }`
*   **Response**: Returns a new video URL or text summary generated by the AI agent.
