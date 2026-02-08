# Railway Database Setup & Population Guide

This guide walks you through setting up and populating the PostgreSQL database on Railway with lesson content, quizzes, and practice questions.

---

## 📋 Prerequisites

- ✅ Railway deployment is successful and running
- ✅ PostgreSQL database is provisioned in Railway
- ✅ `DATABASE_URL` environment variable is set in Railway
- ✅ Railway CLI installed locally: `npm install -g @railway/cli`

---

## 🔧 Step 1: Verify Database Connection

The database tables are **automatically created** when your Railway app starts via the `init_db()` function in `main.py`.

### Verify Tables Were Created

1. **Login to Railway CLI:**
   ```bash
   railway login
   ```

2. **Link to your project:**
   ```bash
   cd /path/to/vina-backend
   railway link
   ```
   Select your project and environment.

3. **Connect to PostgreSQL:**
   ```bash
   railway connect Postgres
   ```

4. **List tables:**
   ```sql
   \dt
   ```
   
   You should see:
   - `user`
   - `userprofile`
   - `session`
   - `quizattempt`
   - `lesson_cache`

5. **Exit PostgreSQL:**
   ```sql
   \q
   ```

---

## 📦 Step 2: Populate Lesson Cache (Videos & Content)

The lesson cache stores generated lesson content and video URLs. You have two options:

### Option A: Generate Fresh Content on Railway (Recommended for Production)

**Note:** This requires your API keys to be set in Railway environment variables.

1. **Ensure environment variables are set in Railway:**
   - `GEMINI_API_KEY`
   - `ELEVENLABS_API_KEY`
   - `CLOUDINARY_CLOUD_NAME`
   - `CLOUDINARY_API_KEY`
   - `CLOUDINARY_API_SECRET`

2. **Run generation script via Railway CLI:**
   ```bash
   # Generate lessons 1-3 for all professions and difficulties
   railway run python scripts/demo_complete_pipeline.py --lesson 1 --profession nurse --difficulty beginner
   railway run python scripts/demo_complete_pipeline.py --lesson 1 --profession nurse --difficulty intermediate
   railway run python scripts/demo_complete_pipeline.py --lesson 1 --profession nurse --difficulty advanced
   
   # Repeat for other professions (doctor, pharmacist) and lessons (2, 3)
   ```

### Option B: Copy Lesson Cache from Local Database (Faster for Demo)

**This is faster if you already have generated content locally.**

1. **Export lesson cache from local SQLite:**
   ```bash
   # On your local machine
   cd /path/to/vina-backend
   
   # Create export script
   python -c "
   import json
   from sqlmodel import Session, select
   from vina_backend.integrations.db.engine import engine
   from vina_backend.services.lesson_cache import LessonCache
   
   with Session(engine) as session:
       lessons = session.exec(select(LessonCache)).all()
       data = [
           {
               'profession': l.profession,
               'difficulty': l.difficulty,
               'lesson_number': l.lesson_number,
               'lesson_json': l.lesson_json,
               'video_url': l.video_url,
               'thumbnail_url': l.thumbnail_url
           }
           for l in lessons
       ]
       with open('lesson_cache_export.json', 'w') as f:
           json.dump(data, f, indent=2)
   
   print(f'Exported {len(data)} lessons')
   "
   ```

2. **Import to Railway PostgreSQL:**
   ```bash
   # Create import script
   cat > import_lessons.py << 'EOF'
   import json
   import os
   from sqlmodel import Session, select
   from vina_backend.integrations.db.engine import engine
   from vina_backend.services.lesson_cache import LessonCache
   
   with open('lesson_cache_export.json', 'r') as f:
       data = json.load(f)
   
   with Session(engine) as session:
       for item in data:
           # Check if lesson already exists
           existing = session.exec(
               select(LessonCache).where(
                   LessonCache.profession == item['profession'],
                   LessonCache.difficulty == item['difficulty'],
                   LessonCache.lesson_number == item['lesson_number']
               )
           ).first()
           
           if not existing:
               lesson = LessonCache(**item)
               session.add(lesson)
       
       session.commit()
       print(f'Imported {len(data)} lessons')
   EOF
   
   # Run import on Railway
   railway run python import_lessons.py
   ```

---

## 📝 Step 3: Generate Lesson Quizzes

Generate quizzes for each lesson, profession, and difficulty level.

### Generate All Quizzes

```bash
# Generate quizzes for lessons 1-5, all professions, all difficulties
railway run python scripts/generate_lesson_quizzes.py \
  --lessons 1 2 3 4 5 \
  --professions nurse doctor pharmacist \
  --difficulties beginner intermediate advanced \
  --overwrite
```

### Generate Specific Quizzes

```bash
# Generate only for specific lesson/profession/difficulty
railway run python scripts/generate_lesson_quizzes.py \
  --lessons 1 \
  --professions nurse \
  --difficulties beginner
```

**Output:** Quizzes are saved to `cache/quizzes/lesson_quizzes.json`

---

## 🎯 Step 4: Generate Practice Questions

Generate daily practice questions for each lesson and profession.

### Generate All Practice Questions

```bash
# Generate practice questions for lessons 1-5, all professions
railway run python scripts/generate_practice_questions.py \
  --lessons 1 2 3 4 5 \
  --professions nurse doctor pharmacist \
  --overwrite
```

### Generate Specific Practice Questions

```bash
# Generate only for specific lesson/profession
railway run python scripts/generate_practice_questions.py \
  --lessons 1 \
  --professions nurse
```

**Output:** Practice questions are saved to `cache/practice_questions/practice_questions.json`

---

## 🔍 Step 5: Verify Database Population

### Check Lesson Cache Count

```bash
railway connect Postgres
```

```sql
-- Count lessons in cache
SELECT profession, difficulty, COUNT(*) 
FROM lesson_cache 
GROUP BY profession, difficulty;

-- View sample lesson
SELECT profession, difficulty, lesson_number, video_url 
FROM lesson_cache 
LIMIT 5;
```

### Check Quiz Files

```bash
# List quiz files
railway run ls -la cache/quizzes/

# View quiz content
railway run cat cache/quizzes/lesson_quizzes.json | head -50
```

### Check Practice Questions

```bash
# List practice question files
railway run ls -la cache/practice_questions/

# View practice questions
railway run cat cache/practice_questions/practice_questions.json | head -50
```

---

## 🚀 Step 6: Test API Endpoints

### Get Railway App URL

```bash
railway status
```

Or check Railway dashboard for your app URL (e.g., `https://vina-backend-production.up.railway.app`)

### Test Endpoints

```bash
# Replace with your Railway URL
export RAILWAY_URL="https://your-app.up.railway.app"

# Health check
curl $RAILWAY_URL/health

# Get lesson (requires authentication)
curl $RAILWAY_URL/api/lessons/1?profession=nurse&difficulty=beginner

# Register user
curl -X POST $RAILWAY_URL/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123",
    "full_name": "Test User"
  }'

# Login
curl -X POST $RAILWAY_URL/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }'
```

---

## 📊 Complete Setup Script (All-in-One)

For a fresh Railway deployment, run this complete setup:

```bash
#!/bin/bash
# complete_railway_setup.sh

echo "🚀 Starting Railway Database Setup..."

# Step 1: Verify Railway connection
echo "📡 Verifying Railway connection..."
railway status || { echo "❌ Not connected to Railway. Run 'railway link' first."; exit 1; }

# Step 2: Generate lesson content (if not copying from local)
echo "📦 Generating lesson content..."
for lesson in 1 2 3; do
  for profession in nurse doctor pharmacist; do
    for difficulty in beginner intermediate advanced; do
      echo "Generating: Lesson $lesson - $profession - $difficulty"
      railway run python scripts/demo_complete_pipeline.py \
        --lesson $lesson \
        --profession $profession \
        --difficulty $difficulty
    done
  done
done

# Step 3: Generate quizzes
echo "📝 Generating lesson quizzes..."
railway run python scripts/generate_lesson_quizzes.py \
  --lessons 1 2 3 4 5 \
  --professions nurse doctor pharmacist \
  --difficulties beginner intermediate advanced \
  --overwrite

# Step 4: Generate practice questions
echo "🎯 Generating practice questions..."
railway run python scripts/generate_practice_questions.py \
  --lessons 1 2 3 4 5 \
  --professions nurse doctor pharmacist \
  --overwrite

echo "✅ Railway database setup complete!"
echo "🔍 Verify at: $(railway status | grep 'URL')"
```

**Make it executable and run:**
```bash
chmod +x complete_railway_setup.sh
./complete_railway_setup.sh
```

---

## 🔄 Updating Content Later

### Add New Lessons (e.g., Lessons 4-5)

```bash
# Generate new lesson content
railway run python scripts/demo_complete_pipeline.py --lesson 4 --profession nurse --difficulty beginner

# Generate quizzes for new lessons
railway run python scripts/generate_lesson_quizzes.py --lessons 4 5 --professions nurse doctor pharmacist --difficulties beginner intermediate advanced

# Generate practice questions
railway run python scripts/generate_practice_questions.py --lessons 4 5 --professions nurse doctor pharmacist
```

### Update Existing Content

```bash
# Regenerate with --overwrite flag
railway run python scripts/demo_complete_pipeline.py --lesson 1 --profession nurse --difficulty beginner --overwrite
```

---

## 🛠️ Troubleshooting

### Issue: "No module named 'vina_backend'"

**Solution:** Ensure you're running commands via `railway run` which sets up the correct environment.

### Issue: "Database connection failed"

**Solution:** 
1. Verify `DATABASE_URL` is set: `railway variables`
2. Check PostgreSQL service is running: `railway status`
3. Restart the app: `railway up --detach`

### Issue: "API keys not found"

**Solution:** Set environment variables in Railway:
```bash
railway variables set GEMINI_API_KEY=your_key_here
railway variables set ELEVENLABS_API_KEY=your_key_here
railway variables set CLOUDINARY_CLOUD_NAME=your_cloud_name
railway variables set CLOUDINARY_API_KEY=your_api_key
railway variables set CLOUDINARY_API_SECRET=your_api_secret
```

### Issue: "Out of memory during generation"

**Solution:** Generate content in smaller batches or upgrade Railway plan for more resources.

---

## 📚 Quick Reference

| Task | Command |
|------|---------|
| Connect to Railway | `railway login && railway link` |
| Check deployment status | `railway status` |
| View logs | `railway logs` |
| Connect to PostgreSQL | `railway connect Postgres` |
| Run script on Railway | `railway run python script.py` |
| Set environment variable | `railway variables set KEY=value` |
| List environment variables | `railway variables` |
| Restart application | `railway up --detach` |

---

## ✅ Checklist

- [ ] Railway deployment is successful
- [ ] PostgreSQL database is provisioned
- [ ] Database tables are created (verified via `\dt`)
- [ ] Environment variables are set (API keys)
- [ ] Lesson cache is populated (lessons 1-3 minimum)
- [ ] Lesson quizzes are generated
- [ ] Practice questions are generated
- [ ] API endpoints are tested and working
- [ ] Frontend can connect to Railway backend

---

## 🎯 Next Steps

1. **Update Frontend:** Point your frontend's `NEXT_PUBLIC_API_URL` to your Railway URL
2. **Test End-to-End:** Register a user, complete onboarding, take lessons
3. **Monitor:** Use Railway dashboard to monitor logs and performance
4. **Scale:** Adjust Railway resources based on usage

---

**Last Updated:** 2026-02-08
**Railway Deployment:** ✅ Success
