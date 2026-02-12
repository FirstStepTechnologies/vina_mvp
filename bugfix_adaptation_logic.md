# Bug Fix: Adaptation Context Logic

## 🐛 The Issue
When a user selected the **"More examples"** option from the adaptation menu, the backend would return the default lesson version instead of the adapted one.

### Root Cause
1.  **Frontend**: The `handleAdapt` function in `page.tsx` was calling `ApiService.getLesson` without passing the selected adaptation type (e.g., "examples").
2.  **API Service**: The `getLesson` method did not have a parameter to accept or transmit `adaptation` context.
3.  **Backend**: The `GET /lessons/{id}` endpoint did not accept an `adaptation` query parameter, meaning it always queried the database for the default lesson (where `adaptation_context` is null).

---

## 🛠️ The Fix

### 1. Frontend: ApiService Update (`src/lib/api/service.ts`)
Updated `getLesson` signature to accept an optional `adaptation` parameter and append it to the query string.

```typescript
static async getLesson(lessonId: string, difficulty: number = 3, profession?: string, adaptation?: string): Promise<Lesson> {
    const adaptationParam = adaptation ? `&adaptation=${encodeURIComponent(adaptation)}` : '';
    // ...
}
```

### 2. Frontend: Page Component Update (`src/app/lesson/[id]/page.tsx`)
Updated `handleAdapt` to pass the `type` to the API service.

```typescript
const data = await ApiService.getLesson(params.id, newDifficulty, profession, type);
```

### 3. Backend: Router Update (`src/vina_backend/api/routers/lessons.py`)
Updated the endpoint to accept `adaptation` as a query parameter and filter the `LessonCache` query.

```python
@router.get("/{lesson_id}")
def get_lesson_detail(
    ...,
    adaptation: Optional[str] = Query(None),
    ...
):
    # ...
    statement = select(LessonCache).where(
        ...,
        LessonCache.adaptation_context == adaptation
    )
```

## ✅ Result
Selecting "More examples" now triggers a request like:
`GET /api/v1/lessons/l01?difficulty=3&adaptation=examples`

The backend correctly retrieves the specific cached lesson generated for that context.
