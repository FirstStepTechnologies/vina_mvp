# Vina Backend API Specification

This document details the RESTful API endpoints required to power the Vina frontend application. The backend team should implement these endpoints to replace the current mock data layer.

## 1. Authentication & User Management [`/api/auth`]

### `POST /api/auth/register`
Creates a new user account.
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "securepassword123",
    "fullName": "Jane Doe"
  }
  ```
- **Response (201 Created)**:
  ```json
  {
    "userId": "usr_12345",
    "token": "jwt_token_here",
    "user": { ...userObject }
  }
  ```

### `POST /api/auth/login`
Authenticates an existing user.
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "securepassword123"
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "token": "jwt_token_here",
    "user": { ...userObject }
  }
  ```

### `GET /api/user/profile`
Retrieves the current user's profile and preferences.
- **Headers**: `Authorization: Bearer <token>`
- **Response (200 OK)**:
  ```json
  {
    "userId": "usr_12345",
    "fullName": "Jane Doe",
    "email": "user@example.com",
    "profession": "Software Engineer", // or null if not set
    "preferences": {
        "dailyGoal": 15, // minutes
        "difficulty": "adaptive"
    },
    "streak": 5, // current daily streak
    "totalXp": 1250
  }
  ```

### `PUT /api/user/profile`
Updates user profile information (e.g. after onboarding).
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "profession": "Product Manager",
    "preferences": { "dailyGoal": 20 }
  }
  ```

---

## 2. Course & Curriculum [`/api/course`]

### `GET /api/course/map`
Retrieves the full list of lessons for the main dashboard (S-curve map).
- **Headers**: `Authorization: Bearer <token>`
- **Response (200 OK)**:
  ```json
  [
    {
      "lessonId": "l01_intro",
      "title": "Introduction to LLMs",
      "shortTitle": "Intro",
      "description": "What are Large Language Models?",
      "lessonNumber": 1,
      "status": "completed", // "locked" | "active" | "completed"
      "type": "video", // "video" | "interactive"
      "duration": 5, // minutes
      "xp": 100,
      "thumbnailUrl": "https://cdn.vina.ai/thumbs/l01.jpg"
    },
    // ... more lessons
  ]
  ```
  **Note**: The backend should calculate the `status` field for each lesson based on the user's progress and the lesson's prerequisites.

### `GET /api/lesson/:id`
Retrieves detailed content for a specific lesson, including video URLs and quiz data.
- **Headers**: `Authorization: Bearer <token>`
- **Path Params**: `id` (e.g., `l01_intro`)
- **Response (200 OK)**:
  ```json
  {
    "lessonId": "l01_intro",
    "title": "What are LLMs?",
    "videoUrl": "https://cdn.vina.ai/videos/l01_standard.mp4",
    "transcript": "In this lesson...",
    "quiz": {
        "id": "quiz_l01",
        "questions": [
            {
                "id": "q1",
                "text": "What does LLM stand for?",
                "options": [
                    "Large Language Model",
                    "Long Learning Machine",
                    "Little Logic Maker"
                ],
                "correctIndex": 0 // Optional: Backend can validate answers instead of sending this
            }
        ]
    },
    "adaptations": {
        "simplify": "https://cdn.vina.ai/videos/l01_simple.mp4",
        "deep_dive": "https://cdn.vina.ai/videos/l01_advanced.mp4"
    }
  }
  ```

---

## 3. Progress & Activity [`/api/progress`]

### `POST /api/lesson/:id/complete`
Marks a lesson as complete and awards XP.
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "score": 85, // Quiz score percentage
    "timeSpent": 320 // Seconds spent on lesson
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "success": true,
    "xpAwarded": 100,
    "newTotalXp": 1350,
    "nextUnlock": "l02_architecture",
    "streakUpdated": true
  }
  ```

### `GET /api/progress/summary`
Returns high-level stats for the dashboard header/widgets.
- **Headers**: `Authorization: Bearer <token>`
- **Response (200 OK)**:
  ```json
  {
    "completedLessonsCount": 4,
    "totalLessonsCount": 17,
    "currentStreak": 5,
    "dailyGoalProgress": 0.6 // 60% of today's goal met
  }
  ```

---

## 4. Adaptive Learning (Future/Phase 2) [`/api/adapt`]

### `POST /api/adapt/generate`
Triggers an on-demand generation of lesson content tailored to the user.
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "lessonId": "l03_transformers",
    "adaptationType": "simplify", // "simplify" | "concise" | "analogy_based"
    "userNotes": "Explain like I'm 5"
  }
  ```
- **Response (202 Accepted)**:
  ```json
  {
    "status": "generating",
    "jobId": "job_889922",
    "estimatedTime": 15 // seconds
  }
  ```
  *(Frontend will likely poll a status endpoint or use WebSockets for the result)*

---

## Data Models (Reference)

### User Profile
- `id`: UUID
- `email`: String (Unique)
- `passwordHash`: String
- `fullName`: String
- `profession`: Enum (Engineer, PM, Designer, Student, Other)
- `createdAt`: Timestamp

### Lesson
- `id`: String (Unique Identifier)
- `title`: String
- `category`: String (Concepts, Application, Ethics)
- `prerequisiteIds`: Array[String] (Lesson IDs that must be completed first)
- `baseXp`: Integer

### UserProgress
- `userId`: UUID
- `lessonId`: String
- `status`: Enum (Started, Completed)
- `quizScore`: Integer (0-100)
- `completedAt`: Timestamp
