Here is the step-by-step analysis of how video files are handled in your codebase:

1. Where are the files stored? (MP3/MP4)
After generation, files are stored in two local locations before upload:

Run-Specific Cache: cache/runs/{profession_...}/ contains the intermediate assets (images, audio).
Output Location: cache/demo_videos/{name}.mp4 (if running demo_complete_pipeline.py) or cache/pipeline/output.mp4 (default).
Master Cache: A copy is saved to cache/global_assets/videos/{content_hash}.mp4 to prevent re-generation of identical content.
2. Where is the entry registered?
The video entry is registered in your local SQLite database (vina.db), specifically in the lesson_cache table.

Column: video_url
Logic: The demo_complete_pipeline.py script calls cache_service.update_video_url(...) after a successful Cloudinary upload to save the secure URL into this table.
3. Where is the video served from?
The video is served from the Cloudinary URL.

Mechanism: The frontend requests /api/v1/lessons/{id}.
Backend Logic: lessons.py queries the lesson_cache table. If a video_url exists (which points to Cloudinary), it returns that URL.
Fallback: If not in the DB, it checks video_manifest.json, which implies a static mapping (also likely Cloudinary URLs).
4. Local vs. Production Behavior (and the "Workaround")
Current Behavior: The code behaves the same in both environments.

It always attempts to upload to Cloudinary.
If Cloudinary credentials are missing (e.g., local dev without .env), the script prints a warning (⚠️ Cloudinary not configured. Skipping upload.) and does not update the DB.
Result: Without Cloudinary, your local app currently cannot serve the generated video because the DB entry will have video_url=None.

what is the location of the video_manifest.json
ls src/vina_backend/domain/constants/video_manifest.json



1. Handling Multiple Models for the Same Lesson
When the frontend requests a lesson URL, it currently only sends the lesson_id, difficulty, profession, and adaptation. It does not specify which LLM model generated the content.

In the backend (
src/vina_backend/api/routers/lessons.py
), the query to retrieve the video looks like this:

python
statement = select(LessonCache).where(
    LessonCache.lesson_id == lesson_id,
    LessonCache.difficulty_level == difficulty,
    LessonCache.profile_hash == profile_hash,
    LessonCache.adaptation_context == adaptation_val
).order_by(LessonCache.created_at.desc())  # <-- Key Logic
The behavior is:

The backend retrieves all entries that match the criteria (lesson, difficulty, profile).
It sorts them by the creation date in descending order (.order_by(LessonCache.created_at.desc())).
It returns the most recently generated video (.first()).
Conclusion: If you generated a lesson with Gemini Pro and then later generated the same lesson with Claude or Gemini Flash, the backend will automatically serve the newest one, regardless of the model name.
2. Does video_manifest.json get updated?
No, the video_manifest.json does not get updated when you run the pipeline script.

Registration Location: When you run 
scripts/demo_complete_pipeline.py
, the video URL is registered in the SQLite Database (
vina.db
) inside the lesson_cache table.
Manifest Purpose: The 
src/vina_backend/domain/constants/video_manifest.json
 is treated as a static fallback. The backend only looks at the manifest if it fails to find a matching entry in the dynamic database (the 
LessonCache
).
Result: Running the demo script with any flags (like --adaptation "examples") will create a new record in your database, but the JSON file will remain exactly as it is. It's safe to think of the Manifest as "baseline videos" and the Database as "personalized AI videos."
