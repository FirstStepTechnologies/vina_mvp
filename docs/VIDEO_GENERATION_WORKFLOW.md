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
