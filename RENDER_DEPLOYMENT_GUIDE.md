# Render Deployment Guide for Vina Backend

This guide walks you through deploying the Vina backend to Render with persistent SQLite database storage.

---

## 🎯 Why Render?

**Perfect for hackathons and demos:**
- ✅ **Persistent Disk Storage** - SQLite database survives deployments
- ✅ **Simple Setup** - No complex database migration needed
- ✅ **Git-based Deployment** - Automatic deploys from GitHub
- ✅ **Free Tier Available** - Great for testing (paid tier recommended for demos)
- ✅ **Easy Database Upload** - Include database in Git or upload via shell

---

## 📋 Prerequisites

- ✅ GitHub repository with your code
- ✅ Render account (sign up at https://render.com)
- ✅ Local `vina.db` with generated content (optional but recommended)
- ✅ API keys for Gemini, ElevenLabs, and Cloudinary

---

## 🚀 Step-by-Step Deployment

### Step 1: Prepare Your Repository

1. **Ensure database is included in Git** (if you want to deploy with existing content):
   
   Your `.gitignore` should have database files uncommented:
   ```gitignore
   # Database files
   # data/
   # *.db
   # *.sqlite
   ```

2. **Commit your database** (optional - only if you have pre-generated content):
   ```bash
   git add data/vina.db
   git commit -m "Add database with lesson content for deployment"
   git push origin main
   ```

3. **Verify required files exist:**
   - ✅ `requirements.txt` - Python dependencies
   - ✅ `src/vina_backend/main.py` - FastAPI application
   - ✅ `data/vina.db` - Database (optional, can be created on Render)

### Step 2: Create a New Web Service on Render

1. **Go to Render Dashboard:**
   - Visit https://dashboard.render.com
   - Click **"New +"** → **"Web Service"**

2. **Connect Your Repository:**
   - Select **"Build and deploy from a Git repository"**
   - Click **"Connect GitHub"** (or GitLab/Bitbucket)
   - Authorize Render to access your repositories
   - Select your repository: `FirstStepTechnologies/vina_mvp`

3. **Configure the Service:**

   | Field | Value |
   |-------|-------|
   | **Name** | `vina-backend` (or your preferred name) |
   | **Region** | Choose closest to you (e.g., Oregon, Frankfurt) |
   | **Branch** | `main` |
   | **Root Directory** | (leave blank) |
   | **Runtime** | `Python 3` |
   | **Build Command** | `pip install -r requirements.txt` |
   | **Start Command** | `uvicorn vina_backend.main:app --host 0.0.0.0 --port $PORT --app-dir src` |
   | **Instance Type** | **Starter** ($7/month) or **Standard** (recommended for demos) |

4. **Click "Create Web Service"**

### Step 3: Add Persistent Disk for Database

**IMPORTANT:** Do this before the first deployment to avoid data loss.

1. **In your service dashboard, click "Disks"** (left sidebar)

2. **Click "Add Disk"**

3. **Configure the disk:**
   - **Name:** `vina-data`
   - **Mount Path:** `/opt/render/project/src/data`
   - **Size:** `1 GB` (sufficient for demo, can increase later)

4. **Click "Create Disk"**

### Step 4: Set Environment Variables

1. **Click "Environment"** in the left sidebar

2. **Add the following environment variables:**

   ```bash
   # Database Configuration
   DATABASE_URL=sqlite:////opt/render/project/src/data/vina.db
   
   # LLM Provider Configuration
   LLM_PROVIDER=gemini
   LLM_MODEL=gemini-3-pro-preview
   LLM_REASONING_MODEL=gemini-3-pro-preview
   GEMINI_API_KEY=your_gemini_api_key_here
   
   # ElevenLabs Configuration
   ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
   ELEVENLABS_MODEL=eleven_turbo_v2
   ELEVENLABS_VOICE_ID=pFZP5JQG7iQjIQuC4Bku
   
   # Cloudinary Configuration
   CLOUDINARY_CLOUD_NAME=your_cloud_name
   CLOUDINARY_API_KEY=your_api_key
   CLOUDINARY_API_SECRET=your_api_secret
   
   # Application Configuration
   LOG_LEVEL=INFO
   SECRET_KEY=your_secret_key_for_jwt_tokens
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=10080
   ```

3. **Click "Save Changes"**

### Step 5: Deploy

Render will automatically deploy your service. Monitor the deployment:

1. **Click "Logs"** to watch the build and deployment process

2. **Wait for deployment to complete** (usually 2-5 minutes)

3. **Look for these success messages:**
   ```
   ==> Build successful 🎉
   ==> Deploying...
   ==> Starting service with 'uvicorn vina_backend.main:app...'
   INFO:     Started server process
   INFO:     Application startup complete.
   INFO:     Uvicorn running on http://0.0.0.0:10000
   ```

4. **Your service URL will be:** `https://vina-backend.onrender.com` (or your custom name)

---

## 📦 Option A: Deploy with Database Included in Git

If you committed your database to Git (Step 1), it will be automatically deployed!

**Verify the database:**
```bash
# Open Render Shell (from dashboard)
ls -lh /opt/render/project/src/data/vina.db

# Check database content
python -c "
from vina_backend.integrations.db.engine import engine
from sqlmodel import Session, select
from vina_backend.services.lesson_cache import LessonCache

with Session(engine) as session:
    count = len(session.exec(select(LessonCache)).all())
    print(f'✅ Found {count} lessons in cache')
"
```

---

## 📦 Option B: Upload Database After Deployment

If you didn't include the database in Git, upload it via Render Shell:

### Method 1: Using Render Shell (Recommended)

1. **Open Render Shell:**
   - In your service dashboard, click **"Shell"** tab
   - Click **"Launch Shell"**

2. **Create a temporary upload script on your local machine:**
   ```bash
   # On your local machine
   cd /path/to/vina-backend
   
   # Create upload script
   cat > upload_db.sh << 'EOF'
   #!/bin/bash
   echo "Uploading database to Render..."
   cat data/vina.db | base64
   EOF
   
   chmod +x upload_db.sh
   ./upload_db.sh > db_base64.txt
   ```

3. **In Render Shell, download and decode:**
   ```bash
   # In Render Shell
   mkdir -p /opt/render/project/src/data
   
   # Paste the base64 content from db_base64.txt, then:
   cat > /tmp/db_base64.txt
   # Paste content, then press Ctrl+D
   
   # Decode and save
   base64 -d /tmp/db_base64.txt > /opt/render/project/src/data/vina.db
   
   # Verify
   ls -lh /opt/render/project/src/data/vina.db
   ```

### Method 2: Generate Content Directly on Render

If you prefer to generate content fresh on Render:

```bash
# In Render Shell
cd /opt/render/project/src

# Generate lessons
python scripts/demo_complete_pipeline.py --lesson 1 --profession nurse --difficulty beginner
python scripts/demo_complete_pipeline.py --lesson 2 --profession nurse --difficulty beginner
python scripts/demo_complete_pipeline.py --lesson 3 --profession nurse --difficulty beginner

# Generate quizzes
python scripts/generate_lesson_quizzes.py \
  --lessons 1 2 3 \
  --professions nurse doctor pharmacist \
  --difficulties beginner intermediate advanced

# Generate practice questions
python scripts/generate_practice_questions.py \
  --lessons 1 2 3 \
  --professions nurse doctor pharmacist
```

---

## 🔍 Verify Deployment

### Test API Endpoints

```bash
# Replace with your Render URL
export RENDER_URL="https://vina-backend.onrender.com"

# Health check
curl $RENDER_URL/health

# Test registration
curl -X POST $RENDER_URL/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123",
    "full_name": "Test User"
  }'

# Test login
curl -X POST $RENDER_URL/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }'
```

### Check Database

```bash
# In Render Shell
python -c "
from vina_backend.integrations.db.engine import engine
from sqlmodel import Session, select, func
from vina_backend.services.lesson_cache import LessonCache
from vina_backend.integrations.db.models.user import User

with Session(engine) as session:
    lesson_count = session.exec(select(func.count(LessonCache.id))).one()
    user_count = session.exec(select(func.count(User.id))).one()
    
    print(f'✅ Lessons: {lesson_count}')
    print(f'✅ Users: {user_count}')
"
```

---

## 🔄 Updating Your Deployment

### Automatic Deployments

Render automatically deploys when you push to your main branch:

```bash
# Make changes locally
git add .
git commit -m "Update lesson content"
git push origin main

# Render will automatically detect and deploy
```

### Manual Deployments

1. Go to your service dashboard
2. Click **"Manual Deploy"** → **"Deploy latest commit"**

### Update Environment Variables

1. Click **"Environment"** in the sidebar
2. Update variables
3. Click **"Save Changes"**
4. Render will automatically redeploy

---

## 💾 Database Backup

### Backup Your Database

```bash
# In Render Shell
cd /opt/render/project/src/data
tar -czf vina_backup_$(date +%Y%m%d).tar.gz vina.db

# Download via Render's file browser or copy content
cat vina_backup_*.tar.gz | base64
# Copy the output and decode locally
```

### Restore from Backup

```bash
# Upload backup (base64 encoded)
# In Render Shell
cat > /tmp/backup.tar.gz.b64
# Paste base64 content, press Ctrl+D

base64 -d /tmp/backup.tar.gz.b64 > /tmp/backup.tar.gz
tar -xzf /tmp/backup.tar.gz -C /opt/render/project/src/data/
```

---

## 🛠️ Troubleshooting

### Issue: "Database is locked"

**Cause:** SQLite doesn't handle high concurrency well.

**Solution:** 
1. Ensure only one instance is running (don't scale horizontally with SQLite)
2. For production, consider migrating to PostgreSQL

### Issue: "Disk full"

**Solution:**
1. Go to **"Disks"** in Render dashboard
2. Increase disk size
3. Service will automatically restart with more space

### Issue: "Module not found"

**Solution:**
1. Verify `requirements.txt` includes all dependencies
2. Check build logs for installation errors
3. Redeploy: **"Manual Deploy"** → **"Clear build cache & deploy"**

### Issue: "Database not persisting"

**Solution:**
1. Verify disk is mounted to correct path: `/opt/render/project/src/data`
2. Check `DATABASE_URL` points to disk path: `sqlite:////opt/render/project/src/data/vina.db`
3. Ensure disk was created BEFORE first deployment

### Issue: "Port already in use"

**Solution:** Render automatically sets `$PORT` environment variable. Ensure your start command uses `--port $PORT`.

---

## 📊 Monitoring & Logs

### View Logs

1. **Real-time logs:** Click **"Logs"** tab in dashboard
2. **Filter logs:** Use the search box
3. **Download logs:** Click **"Download"** button

### Metrics

1. Click **"Metrics"** tab
2. Monitor:
   - CPU usage
   - Memory usage
   - Request count
   - Response times

### Alerts

1. Go to **"Settings"** → **"Notifications"**
2. Set up alerts for:
   - Deploy failures
   - High error rates
   - Resource usage

---

## 💰 Cost Optimization

### Free Tier Limitations
- ⚠️ Services spin down after 15 minutes of inactivity
- ⚠️ Cold starts take 30-60 seconds
- ⚠️ Not suitable for demos

### Recommended for Hackathons
- **Starter Plan:** $7/month
  - No spin down
  - 512 MB RAM
  - Perfect for demos

### Upgrade Path
```
Free → Starter ($7/mo) → Standard ($25/mo) → Pro ($85/mo)
```

---

## 🎯 Next Steps

1. **Update Frontend:** Point `NEXT_PUBLIC_API_URL` to your Render URL
2. **Test End-to-End:** Register, onboard, complete lessons
3. **Generate More Content:** Add lessons 4-5 if needed
4. **Set Up Custom Domain:** (Optional) Add your own domain in Render settings
5. **Enable HTTPS:** Automatically enabled by Render

---

## 📚 Quick Reference

| Task | Command/Location |
|------|------------------|
| View logs | Dashboard → Logs tab |
| Open shell | Dashboard → Shell tab |
| Update env vars | Dashboard → Environment |
| Manual deploy | Dashboard → Manual Deploy |
| Scale service | Dashboard → Settings → Instance Type |
| Add disk | Dashboard → Disks → Add Disk |
| View metrics | Dashboard → Metrics |
| Restart service | Dashboard → Manual Deploy → Deploy latest |

---

## ✅ Deployment Checklist

- [ ] GitHub repository connected
- [ ] Web service created
- [ ] Persistent disk added and mounted to `/opt/render/project/src/data`
- [ ] Environment variables configured (API keys, DATABASE_URL)
- [ ] Build command set: `pip install -r requirements.txt`
- [ ] Start command set: `uvicorn vina_backend.main:app --host 0.0.0.0 --port $PORT --app-dir src`
- [ ] Database uploaded or generated
- [ ] API endpoints tested
- [ ] Frontend connected to Render URL
- [ ] Backup strategy in place

---

## 🔗 Useful Links

- **Render Dashboard:** https://dashboard.render.com
- **Render Docs:** https://render.com/docs
- **Render Status:** https://status.render.com
- **Support:** https://render.com/support

---

**Last Updated:** 2026-02-08  
**Deployment Status:** ✅ Ready for Hackathon Demos

---

## 🎉 You're All Set!

Your Vina backend is now deployed on Render with persistent SQLite storage. The database will survive deployments, and you can easily update content or code by pushing to GitHub.

**Your Render URL:** `https://vina-backend.onrender.com` (replace with your actual URL)

Happy hacking! 🚀
