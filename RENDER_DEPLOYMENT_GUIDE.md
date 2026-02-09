# Render Deployment Guide - Vina Backend

**Simplified guide for deploying with database already in Git**

Since your `data/vina.db` is already committed to GitHub, deployment is straightforward!

---

## ✅ Prerequisites Checklist

- [x] Database (`data/vina.db`) is committed to GitHub
- [x] `requirements.txt` exists
- [x] Render account created (https://render.com)
- [ ] API keys ready (Gemini, ElevenLabs, Cloudinary)

---

## 🚀 Step-by-Step Deployment

### Step 1: Create New Web Service

1. **Go to Render Dashboard**
   - Visit: https://dashboard.render.com
   - Click: **"New +"** → **"Web Service"**

2. **Connect GitHub Repository**
   - Select: **"Build and deploy from a Git repository"**
   - Click: **"Connect GitHub"**
   - Authorize Render
   - Select repository: **`FirstStepTechnologies/vina_mvp`**
   - Click: **"Connect"**

### Step 2: Configure Service Settings

Fill in these exact values:

| Setting | Value |
|---------|-------|
| **Name** | `vina-backend` |
| **Region** | Oregon (US West) or closest to you |
| **Branch** | `main` |
| **Root Directory** | *(leave blank)* |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn vina_backend.main:app --host 0.0.0.0 --port $PORT --app-dir src` |

**Instance Type:**
- For demos/hackathons: **Starter** ($7/month) - Recommended
- For testing: **Free** (spins down after inactivity)

Click **"Create Web Service"** but **DON'T deploy yet!**

### Step 3: Add Persistent Disk (CRITICAL!)

⚠️ **Do this BEFORE first deployment to preserve your database!**

1. In your service dashboard, click **"Disks"** (left sidebar)
2. Click **"Add Disk"**
3. Configure:
   - **Name:** `vina-data`
   - **Mount Path:** `/opt/render/project/src/data`
   - **Size:** `1 GB`
4. Click **"Create"**

### Step 4: Set Environment Variables

1. Click **"Environment"** (left sidebar)
2. Click **"Add Environment Variable"**
3. Add these variables one by one:

```bash
# Database
DATABASE_URL=sqlite:////opt/render/project/src/data/vina.db

# LLM Configuration
LLM_PROVIDER=gemini
LLM_MODEL=gemini-3-pro-preview
LLM_REASONING_MODEL=gemini-3-pro-preview
GEMINI_API_KEY=<your_gemini_key>

# ElevenLabs
ELEVENLABS_API_KEY=<your_elevenlabs_key>
ELEVENLABS_MODEL=eleven_turbo_v2
ELEVENLABS_VOICE_ID=pFZP5JQG7iQjIQuC4Bku

# Cloudinary
CLOUDINARY_CLOUD_NAME=<your_cloud_name>
CLOUDINARY_API_KEY=<your_cloudinary_key>
CLOUDINARY_API_SECRET=<your_cloudinary_secret>

# Auth
SECRET_KEY=<generate_random_secret_key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# Logging
LOG_LEVEL=INFO
```

**To generate a secret key:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

4. Click **"Save Changes"**

### Step 5: Deploy!

1. Render will automatically start deploying
2. Click **"Logs"** to watch the deployment
3. Wait for these messages:
   ```
   ==> Build successful 🎉
   ==> Deploying...
   INFO:     Started server process
   INFO:     Application startup complete.
   ```

4. Your app URL will be shown at the top (e.g., `https://vina-backend.onrender.com`)

---

## ✅ Verify Deployment

### Test 1: Health Check

```bash
curl https://your-app-name.onrender.com/health
```

Expected: `{"status":"healthy"}`

### Test 2: Check Database

Open Render Shell (Dashboard → Shell tab):

```bash
# Check database exists and has content
ls -lh /opt/render/project/src/data/vina.db

# Should show ~5.1 MB (not 92K)
```

### Test 3: Verify Lesson Data

```bash
# In Render Shell
sqlite3 /opt/render/project/src/data/vina.db "SELECT COUNT(*) FROM lesson_cache;"
```

Expected: A number > 0 (like 27 if you have lessons 1-3)

### Test 4: Test API Endpoints

```bash
# Replace with your actual URL
export RENDER_URL="https://vina-backend.onrender.com"

# Test registration
curl -X POST $RENDER_URL/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo@example.com",
    "password": "demo123",
    "full_name": "Demo User"
  }'

# Test login
curl -X POST $RENDER_URL/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo@example.com",
    "password": "demo123"
  }'
```

---

## 🔄 Updating Your Deployment

### Automatic Updates

Render auto-deploys when you push to `main`:

```bash
# Make changes locally
git add .
git commit -m "Update content"
git push origin main

# Render automatically deploys!
```

### Manual Deploy

Dashboard → **"Manual Deploy"** → **"Deploy latest commit"**

---

## 🛠️ Troubleshooting

### Issue: Database is empty (92K instead of 5.1 MB)

**Cause:** Disk wasn't mounted before first deployment

**Solution:**
1. Delete the service
2. Create new service
3. Add disk BEFORE first deployment
4. Deploy again

### Issue: "Module not found"

**Solution:**
- Dashboard → Manual Deploy → **"Clear build cache & deploy"**

### Issue: App is slow/timing out

**Cause:** Free tier spins down after 15 min

**Solution:**
- Upgrade to Starter plan ($7/month)

### Issue: Database changes not persisting

**Check:**
1. Disk is mounted to `/opt/render/project/src/data`
2. `DATABASE_URL` points to `/opt/render/project/src/data/vina.db`
3. Disk was created BEFORE first deployment

---

## 📊 Monitoring

### View Logs
Dashboard → **"Logs"** tab

### View Metrics
Dashboard → **"Metrics"** tab
- CPU usage
- Memory usage
- Request count

### Set Up Alerts
Dashboard → **"Settings"** → **"Notifications"**

---

## 💰 Pricing

| Plan | Price | Best For |
|------|-------|----------|
| **Free** | $0 | Testing only (spins down) |
| **Starter** | $7/mo | ⭐ Demos & Hackathons |
| **Standard** | $25/mo | Production |

---

## 🎯 Connect Frontend

Update your frontend's environment variable:

```bash
# In vina-frontend/.env.local
NEXT_PUBLIC_API_URL=https://vina-backend.onrender.com
```

Then redeploy your frontend!

---

## ✅ Deployment Checklist

- [ ] Render account created
- [ ] GitHub repository connected
- [ ] Web service created with correct build/start commands
- [ ] **Persistent disk added BEFORE first deployment**
- [ ] Environment variables configured
- [ ] Service deployed successfully
- [ ] Health check passes
- [ ] Database has content (5.1 MB)
- [ ] API endpoints working
- [ ] Frontend connected

---

## 🔗 Quick Links

- **Dashboard:** https://dashboard.render.com
- **Docs:** https://render.com/docs
- **Your App:** `https://vina-backend.onrender.com` *(replace with actual URL)*

---

## 📝 Important Notes

1. **Database is in Git:** Your `data/vina.db` will be deployed automatically
2. **Disk is persistent:** Data survives deployments and restarts
3. **Auto-deploy enabled:** Pushes to `main` trigger automatic deployment
4. **HTTPS included:** Render provides free SSL certificates

---

## 🎉 You're Done!

Your Vina backend is now live on Render with all your lesson content!

**Next steps:**
1. Test all API endpoints
2. Connect your frontend
3. Run end-to-end tests
4. Share your demo URL!

---

**Last Updated:** 2026-02-09  
**Status:** ✅ Ready for Deployment
