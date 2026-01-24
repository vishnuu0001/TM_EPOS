# ePOS - Vercel Deployment Guide

## 🚀 Deploy to Vercel

This guide will help you deploy the ePOS application to Vercel.

---

## 📋 Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **GitHub Repository**: Push your code to GitHub (recommended for CI/CD)
3. **No Database Setup Required**: Uses SQLite (file-based database)

---

## 🗄️ Database Setup

### SQLite (Built-in - No External Service Needed)

The application uses **SQLite**, a file-based database that requires no external database service. This makes deployment simpler and more cost-effective.

**Key Points:**
- ✅ No database server required
- ✅ No connection strings to manage
- ✅ Perfect for small to medium applications
- ✅ Database file stored in `/tmp` on Vercel serverless functions
- ⚠️ Data is ephemeral on Vercel (resets on function cold starts)

**For Production with Persistent Data:**

If you need persistent data across deployments, consider:
- **Vercel Postgres** - Managed PostgreSQL service
- **Turso** - Distributed SQLite (recommended for SQLite in production)
- **PlanetScale** - Serverless MySQL
- **Supabase** - PostgreSQL with real-time features

To switch to PostgreSQL, update `DATABASE_URL` environment variable.

### Initialize Database

The database is automatically initialized on first use. You can also initialize it manually:

```bash
# Locally
cd backend
python init_db.py
```

---

## 🔧 Deployment Steps (Detailed, Working)

This project deploys best as **two Vercel projects**:
- **Backend API** (Python serverless function)
- **Frontend** (React static app)

This avoids route conflicts and makes logs clearer.

---

### ✅ Step 1: Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit for Vercel deployment"
git remote add origin <your-github-repo-url>
git push -u origin main
```

---

### ✅ Step 2: Deploy Backend (API) on Vercel

1. Go to [vercel.com/dashboard](https://vercel.com/dashboard) → **Add New → Project**
2. Import your repository
3. **Project Name**: `epos-api`
4. **Framework Preset**: Other
5. **Root Directory**: `backend/api-gateway`

#### ✅ Build & Output Settings (Backend)

- **Build Command**: *(leave empty)*
- **Output Directory**: *(leave empty)*
- **Install Command**: *(leave empty)*

Vercel automatically installs Python dependencies from:
`backend/api-gateway/requirements_vercel.txt`

#### ✅ Environment Variables (Backend)

Go to **Project → Settings → Environment Variables** and add:

```
DATABASE_URL=sqlite:////tmp/epos.db
SECRET_KEY=<your-strong-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=525600
```

**Important:**
- Use the absolute `/tmp` path: `sqlite:////tmp/epos.db`
- Do not prefix `SECRET_KEY` with `@`

#### ✅ Deploy

Click **Deploy**.

After deployment, copy the API URL:

```
https://epos-api.vercel.app
```

Test it:

```
https://epos-api.vercel.app/api/health
```

---

### ✅ Step 3: Deploy Frontend on Vercel

1. Go to Vercel → **Add New → Project**
2. Import the same repository again
3. **Project Name**: `epos-frontend`
4. **Framework Preset**: Vite
5. **Root Directory**: `frontend`

#### ✅ Build & Output Settings (Frontend)

- **Build Command**: `npm run build`
- **Output Directory**: `dist`
- **Install Command**: `npm install`

#### ✅ Environment Variables (Frontend)

```
VITE_API_URL=https://epos-api.vercel.app
VITE_APP_NAME=ePOS
VITE_APP_VERSION=1.0.0
```

#### ✅ Deploy

Click **Deploy**.

Your frontend will be available at:

```
https://epos-frontend.vercel.app
```

---

### ✅ Step 4: Allow Frontend Domain in CORS (Backend)

If you see CORS errors, set the frontend origin in backend environment variables:

```
CORS_ORIGINS=["https://epos-frontend.vercel.app"]
```

Then **Redeploy** the backend.

---

### ✅ Step 5: Verify End‑to‑End

1. Open the frontend URL
2. Login using valid credentials
3. Ensure API calls work without CORS errors

---

## ✅ Frontend (React JSX) Notes

- The frontend now uses **.jsx** files (no TypeScript). Entry point is `frontend/src/main.jsx`.
- Vite config is in `frontend/vite.config.js` and **resolves .jsx/.js first**.
- If you previously set Vercel build settings in the dashboard, note that **`builds` in `vercel.json` overrides those settings**. The build output is `frontend/dist` (configured as `dist` under `frontend/package.json`).

---

## ✅ Required Vercel Settings (Dashboard)

**Framework Preset:** Other

**Root Directory:** `./`

**Build Command:**
```
cd frontend && npm install && npm run build
```

**Output Directory:**
```
frontend/dist
```

**Install Command:**
```
cd frontend && npm install
```

> Note: If you keep `builds` in `vercel.json`, the dashboard settings are ignored. You can still keep these values for clarity.

---

## 🔄 Deployment Architecture

### Vercel Deployment Structure

```
┌─────────────────────────────────────────┐
│     Vercel Edge Network (CDN)           │
│   Frontend: React App (Static Files)    │
└──────────────┬──────────────────────────┘
               │
               ├─── /api/auth/* ──────────┐
               │                           │
               ├─── /api/colony/* ────────┤
               │                           │
               └─── /api/* ───────────────┤
                                           ▼
┌──────────────────────────────────────────────────┐
│      Vercel Serverless Functions (Python)        │
│  • SQLite Database (epos.db in /tmp)            │
└──────────────────────────────────────────────────┘

Note: SQLite database is file-based and stored in /tmp.
For persistent data, consider Turso or PostgreSQL.
│  (Vercel Postgres / Supabase / Neon)            │
└──────────────────────────────────────────────────┘
```

---

## 📝 Project Structure for Vercel

```
TechDev2026_POS/
├── vercel.json                 # Vercel configuration
├── frontend/
│   ├── dist/                   # Build output (auto-generated)
│   ├── src/
│   ├── package.json
│   └── vite.config.ts
├── backend/
│   ├── api-gateway/
│   │   ├── vercel_app.py      # Serverless function
│   │   └── requirements_vercel.txt
│   └── services/
│       └── colony-maintenance/
│           ├── vercel_app.py  # Serverless function
│           └── requirements_vercel.txt
└── shared/                     # Shared utilities
```

---

## ⚙️ Configuration Files

### vercel.json

The `vercel.json` file configures:
- Build settings for frontend and backend
- API routes mapping
- Environment variables
- CORS settings

### Key Routes:
- `/` → Frontend (React app)
- `/api/auth/*` → API Gateway
- `/api/colony/*` → Colony Maintenance Service
- `/api/*` → API Gateway (fallback)

---

## 🔐 Security Configuration

### Environment Variables in Vercel

Set these in: **Dashboard → Settings → Environment Variables**

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | ⚠️ Optional | SQLite by default, or external DB connection |
| `SECRET_KEY` | ✅ Yes | JWT secret (min 32 chars) |
| `CORS_ORIGINS` | ⚠️ Auto | CORS allowed origins |
| `SMTP_HOST` | ❌ No | Email server (optional) |
| `SMS_API_URL` | ❌ No | SMS gateway (optional) |

### Generate Secure SECRET_KEY

```python
# Run this locally to generate a secure key
import secrets
print(secrets.token_urlsafe(32))
```

Or use:
```bash
openssl rand -base64 32
```

---

## 🧪 Testing Deployment

### 1. Test Locally Before Deploy

```bash
# Frontend
cd frontend
npm run build
npm run preview

# Backend (simulate serverless)
cd backend/api-gateway
vercel dev
```

### 2. Test After Deployment

```bash
# Check health endpoint
curl https://your-app.vercel.app/api/health

# Test login
curl -X POST https://your-app.vercel.app/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@epos.com&password=Admin@123"
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. Build Fails - TypeScript Errors
**Solution**: 
- We've updated the build script to skip TypeScript checking
- If issues persist, fix TypeScript errors or add `// @ts-ignore`

#### 2. Database Connection Error
**Solution**:
- SQLite database will be created automatically in /tmp
- For persistent storage, switch to Turso or PostgreSQL
- Ensure write permissions for database file

#### 3. API Returns 404
**Solution**:
- Check `vercel.json` route configuration
- Ensure API paths match (e.g., `/api/auth/login`)
- Verify serverless functions are deployed

#### 4. CORS Errors
**Solution**:
- Add your Vercel domain to CORS_ORIGINS
- Check frontend API URL matches deployed URL
- Clear browser cache

#### 5. Import Errors in Serverless Functions
**Solution**:
- Check `requirements_vercel.txt` includes all dependencies
- Ensure `mangum` is installed (required for FastAPI on Vercel)
- Verify Python version is 3.9+ in Vercel settings

---

## 📊 Monitoring & Logs

### View Logs in Vercel

1. Go to Vercel Dashboard
2. Select your project
3. Click on a deployment
4. View "Functions" tab for backend logs
5. Check "Build Logs" for build issues

### Add Logging

```python
# In your serverless functions
import logging
logger = logging.getLogger(__name__)
logger.info("Request received")
```

---

## 🔄 Continuous Deployment

### Automatic Deployments

Vercel automatically deploys when you push to GitHub:

- **main branch** → Production deployment
- **Other branches** → Preview deployments

### Manual Redeployment

```bash
# Trigger redeploy from CLI
vercel --prod

# Or from dashboard:
# Deployments → Click "..." → Redeploy
```

---

## 📈 Scaling Considerations

### Vercel Limits (Hobby Plan)

- **Bandwidth**: 100GB/month
- **Serverless Functions**: 100GB-hours/month
- **Build Time**: 6000 minutes/month
- **Function Timeout**: 10 seconds

### Optimization Tips

1. **Frontend**:
   - Use lazy loading for routes
   - Optimize images and assets
   - Enable compression (automatic on Vercel)

2. **Backend**:
   - Use database connection pooling
   - Cache frequent queries
   - Keep serverless functions lightweight

3. **Database**:
   - Add indexes on frequently queried fields
   - Use read replicas for heavy loads
   - Monitor query performance

---

## 🎯 Post-Deployment Checklist

- ✅ Frontend loads correctly
- ✅ Login functionality works
- ✅ API endpoints return data
- ✅ Database connection established
- ✅ Environment variables set
- ✅ CORS configured correctly
- ✅ SSL certificate active (automatic)
- ✅ Custom domain configured (optional)
- ✅ Monitoring enabled
- ✅ Error tracking set up

---

## 🌐 Custom Domain

### Add Custom Domain

1. Go to: **Dashboard → Settings → Domains**
2. Click "Add Domain"
3. Enter your domain (e.g., `epos.yourcompany.com`)
4. Follow DNS configuration instructions
5. Wait for SSL certificate (automatic)

---

## 📚 Additional Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Vercel Python Runtime](https://vercel.com/docs/runtimes#official-runtimes/python)
- [FastAPI on Vercel](https://vercel.com/guides/deploying-fastapi-with-vercel)
- [Vercel Environment Variables](https://vercel.com/docs/concepts/projects/environment-variables)
- [Vercel Postgres](https://vercel.com/docs/storage/vercel-postgres)

---

## 🎉 Success!

Your ePOS application is now deployed on Vercel!

**Production URL**: `https://your-app.vercel.app`

**Next Steps**:
1. Configure custom domain (optional)
2. Set up monitoring and alerts
3. Complete remaining microservices
4. Add analytics tracking

---

## 💡 Notes

- **Serverless Functions**: Each API route runs as a separate serverless function
- **Cold Starts**: First request may be slower (1-3 seconds)
- **Database**: Use connection pooling to avoid connection limits
- **Static Assets**: Frontend is served via Vercel's global , database initializes on first request
- **Database**: SQLite file stored in `/tmp` - data may be lost on cold starts (use Turso for persistence)
- **Static Assets**: Frontend is served via Vercel's global CDN
- **Auto-Scaling**: Vercel automatically scales based on traffic
- **Data Persistence**: For production apps with critical data, use Turso, PostgreSQL, or external DB

**Need Help?**
- Check Vercel logs for errors
- Review `vercel.json` configuration
- Verify environment variables
- Test API endpoints with Postman

---

*Deployed with ❤️ on Vercel*
