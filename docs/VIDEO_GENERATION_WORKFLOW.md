# Video Generation & Deployment Workflow

This guide details how to generate "More Examples" videos for all professions and deploy them to the Render production environment using a **safe, selective sync** strategy.

## 1. Prerequisites
- Local development environment set up with `.env`.
- Git access to the `vina-backend` repository.

## 2. Batch Generation Script
Instead of running 20 individual commands, use the Python batch script to automate the process.

**Run the generator:**
```bash
python3 scripts/generate_batch_content.py
```

This script will:
- Iterate through all 4 default professions.
- Generate "More Examples" for Lessons 1 through 5 for each.
- Automatically upload to Cloudinary and update your local database.
- Include a 2-second cooldown between lessons to respect API rate limits.

## 3. Safe Deployment Strategy (Selective Sync)

To update the generated videos on production **WITHOUT** overwriting user data, we use the `scripts/sync_project_content.py` tool.

### Step A: Export Content (Local Machine)
After generating the videos locally:
1.  Run the export command:
    ```bash
    python3 scripts/sync_project_content.py export
    ```
2.  This creates `data/content_export.json`.
3.  **Commit and push** this JSON file:
    ```bash
    git add data/content_export.json
    git commit -m "Content Update: Exported latest lesson videos"
    git push origin main
    ```

### Step B: Import Content (Render Production)
Once the code is deployed to Render:
1.  Access the Render Shell.
2.  Run the import command:
    ```bash
    python3 scripts/sync_project_content.py import
    ```
3.  This reads the JSON file and safely **upserts** the video links into the production database, leaving user profiles and progress untouched.

## 4. Troubleshooting
- **Missing JSON:** Ensure `data/content_export.json` is committed and not ignored by `.gitignore`.
- **Cloudinary:** Generation requires valid Cloudinary credentials in `.env` to host the video files.

## 5. Production Troubleshooting & Quirks
If videos play locally but fail in production, check these known issues:

### Lesson ID Mismatch
- **Symptom:** API returns 404 or falls back to default video.
- **Cause:** Frontend uses long IDs (e.g., `c_llm_foundations:l01...`) while the DB stores short IDs (`l01...`).
- **Fix:** The backend `lessons.py` automatically strips the `c_llm_foundations:` prefix. Ensure this logic remains in place.

### Adaptation Parameter Missing
- **Symptom:** "More Examples" (or other adaptations) load the default video instead of the adapted version.
- **Cause:** The Frontend `getLesson` call might be missing the `adaptation` query parameter.
- **Fix:** Ensure `src/lib/api/service.ts` correctly appends `&adaptation=...` to the URL. Debug with `console.log` in `ApiService`.

### "More Examples" Mapping
- **Symptom:** "More Examples" returns no video, even if generated.
- **Cause:** Frontend requests `more_examples`, but the generator saves content under the `examples` context.
- **Fix:** The backend `lessons.py` maps `more_examples` -> `examples` before querying the database.

