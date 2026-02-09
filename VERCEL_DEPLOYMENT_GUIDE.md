# Vercel Deployment Guide - Vina Frontend

**Step-by-step guide for deploying your Next.js frontend to Vercel**

---

## ✅ Prerequisites

- [x] Frontend working locally
- [x] Backend deployed on Render: `https://vina-backend-6snh.onrender.com`
- [x] `.env.local` updated with Render URL
- [ ] Vercel account (sign up at https://vercel.com)
- [ ] GitHub repository with frontend code

---

## 🚀 Step-by-Step Deployment

### Step 1: Commit Your Changes

First, commit the updated `.env.local` configuration:

```bash
cd /Users/bkadirve/development/first_step_codebases/vina-frontend

# Check what's changed
git status

# Add the environment file
git add .env.local

# Commit
git commit -m "Update API URL to point to Render backend"

# Push to GitHub
git push origin main
```

**Note:** `.env.local` is typically in `.gitignore`. We'll set the environment variable directly in Vercel instead.

### Step 2: Sign Up / Log In to Vercel

1. Go to: https://vercel.com
2. Click **"Sign Up"** (or **"Log In"** if you have an account)
3. Choose **"Continue with GitHub"**
4. Authorize Vercel to access your GitHub account

### Step 3: Import Your Project

1. **On Vercel Dashboard**, click **"Add New..."** → **"Project"**

2. **Import Git Repository:**
   - You'll see a list of your GitHub repositories
   - Find: `FirstStepTechnologies/vina-frontend` (or your frontend repo name)
   - Click **"Import"**

3. **Configure Project:**

   | Setting | Value |
   |---------|-------|
   | **Project Name** | `vina-frontend` (or your preferred name) |
   | **Framework Preset** | `Next.js` (auto-detected) |
   | **Root Directory** | `.` (leave as default) |
   | **Build Command** | `npm run build` (auto-detected) |
   | **Output Directory** | `.next` (auto-detected) |
   | **Install Command** | `npm install` (auto-detected) |

### Step 4: Set Environment Variables

**CRITICAL:** Set your environment variables before deploying!

1. **Expand "Environment Variables"** section

2. **Add this variable:**
   - **Key:** `NEXT_PUBLIC_API_URL`
   - **Value:** `https://vina-backend-6snh.onrender.com/api/v1`
   - **Environment:** Check all three: Production, Preview, Development

3. Click **"Add"**

### Step 5: Deploy!

1. Click **"Deploy"**

2. Vercel will:
   - Clone your repository
   - Install dependencies (`npm install`)
   - Build your Next.js app (`npm run build`)
   - Deploy to production

3. **Wait for deployment** (usually 1-3 minutes)

4. **Look for success message:**
   ```
   ✓ Build Completed
   ✓ Deployment Ready
   ```

5. **Your app URL will be shown:**
   - Production: `https://vina-frontend.vercel.app`
   - Or custom: `https://your-project-name.vercel.app`

---

## ✅ Verify Deployment

### Test 1: Visit Your Site

Click the deployment URL or visit:
```
https://vina-frontend.vercel.app
```

### Test 2: Check API Connection

1. Open browser DevTools (F12)
2. Go to **Console** tab
3. Try registering a user
4. Check Network tab for API calls to Render

### Test 3: Complete User Flow

1. **Register** a new user
2. **Complete onboarding** (select profession, take quiz)
3. **Take a lesson**
4. **Complete quiz**

---

## 🔄 Automatic Deployments

Vercel automatically deploys when you push to GitHub:

```bash
# Make changes locally
git add .
git commit -m "Update homepage"
git push origin main

# Vercel automatically deploys!
```

**Deployment Types:**
- **Production:** Pushes to `main` branch
- **Preview:** Pushes to other branches or pull requests

---

## 🛠️ Post-Deployment Configuration

### Custom Domain (Optional)

1. Go to **Project Settings** → **Domains**
2. Click **"Add Domain"**
3. Enter your domain (e.g., `vina.yourdomain.com`)
4. Follow DNS configuration instructions

### Environment Variables

To update environment variables:

1. Go to **Project Settings** → **Environment Variables**
2. Edit or add variables
3. Click **"Save"**
4. **Redeploy** for changes to take effect

### Analytics (Optional)

Vercel provides built-in analytics:

1. Go to **Analytics** tab
2. View page views, performance metrics, etc.

---

## 🔍 Troubleshooting

### Issue: Build Failed

**Check build logs:**
1. Click on the failed deployment
2. View **"Build Logs"**
3. Look for error messages

**Common fixes:**
- Ensure `package.json` has all dependencies
- Check for TypeScript errors
- Verify Next.js version compatibility

### Issue: API Calls Failing

**Check environment variables:**
1. Project Settings → Environment Variables
2. Verify `NEXT_PUBLIC_API_URL` is set correctly
3. Redeploy after changes

**Check CORS:**
- Ensure your Render backend allows requests from Vercel domain
- Check browser console for CORS errors

### Issue: 404 on Routes

**Next.js routing:**
- Vercel automatically handles Next.js routing
- Ensure your routes are in `src/app/` directory
- Check for case sensitivity in file names

### Issue: Environment Variable Not Working

**Remember:**
- Environment variables starting with `NEXT_PUBLIC_` are exposed to browser
- Must redeploy after changing environment variables
- Clear browser cache if needed

---

## 📊 Monitoring & Logs

### View Deployment Logs

1. Go to **Deployments** tab
2. Click on any deployment
3. View **"Build Logs"** and **"Function Logs"**

### Real-time Logs

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# View logs
vercel logs
```

---

## 💰 Pricing

| Plan | Price | Best For |
|------|-------|----------|
| **Hobby** | Free | Personal projects, demos |
| **Pro** | $20/month | Professional projects |
| **Enterprise** | Custom | Large teams |

**Free tier includes:**
- Unlimited deployments
- Automatic HTTPS
- 100GB bandwidth/month
- Serverless functions

---

## 🎯 Your Deployment URLs

After deployment, you'll have:

- **Production:** `https://vina-frontend.vercel.app`
- **Backend:** `https://vina-backend-6snh.onrender.com`
- **API Endpoint:** `https://vina-backend-6snh.onrender.com/api/v1`

---

## ✅ Deployment Checklist

- [ ] Vercel account created
- [ ] GitHub repository connected
- [ ] Environment variable `NEXT_PUBLIC_API_URL` set
- [ ] Project deployed successfully
- [ ] Site loads correctly
- [ ] API connection working
- [ ] User registration works
- [ ] Onboarding flow works
- [ ] Lessons load correctly
- [ ] Quizzes work

---

## 🔗 Useful Links

- **Vercel Dashboard:** https://vercel.com/dashboard
- **Vercel Docs:** https://vercel.com/docs
- **Next.js on Vercel:** https://vercel.com/docs/frameworks/nextjs
- **Your Project:** `https://vercel.com/your-username/vina-frontend`

---

## 📝 Important Notes

1. **Environment Variables:** Always use `NEXT_PUBLIC_` prefix for client-side variables
2. **Automatic Deploys:** Every push to `main` triggers a production deployment
3. **Preview Deployments:** Pull requests get unique preview URLs
4. **HTTPS:** Automatically enabled for all deployments
5. **CDN:** Your app is served from Vercel's global CDN

---

## 🎉 You're Done!

Your Vina frontend is now live on Vercel!

**Full Stack Deployment:**
- ✅ **Frontend:** Vercel (`https://vina-frontend.vercel.app`)
- ✅ **Backend:** Render (`https://vina-backend-6snh.onrender.com`)
- ✅ **Database:** SQLite on Render persistent disk
- ✅ **Auto-deploy:** Enabled for both frontend and backend

**Next steps:**
1. Share your Vercel URL with stakeholders
2. Test all features end-to-end
3. Monitor analytics and logs
4. Add custom domain (optional)

---

**Last Updated:** 2026-02-09  
**Status:** ✅ Ready for Production
