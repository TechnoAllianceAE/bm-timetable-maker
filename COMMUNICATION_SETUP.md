# Frontend-Backend-Python Communication Setup

## 🔗 Communication Chain

```
Frontend (Next.js:3000)
    ↓ HTTP POST
Backend (NestJS:5000)
    ↓ HTTP POST
Python Engine (FastAPI:8000)
```

## 📋 Complete Request Flow

### 1. Frontend → Backend
**Endpoint:** `POST /api/v1/timetables/generate`
- **Frontend File:** `frontend/lib/api.ts` (line 159)
- **Base URL:** `/api/v1` (browser) or `http://localhost:5000/api/v1` (server)
- **Proxy:** Next.js rewrites `/api/v1/*` → `http://localhost:5000/api/v1/*`
- **Auth:** JWT Bearer token from localStorage

### 2. Backend → Python
**Endpoint:** `POST http://localhost:8000/generate`
- **Backend File:** `backend/src/modules/timetables/timetables.service.ts` (line 235)
- **URL Source:** Environment variable `PYTHON_TIMETABLE_URL`
- **Default:** `http://localhost:8000`
- **Timeout:** 120 seconds (2 minutes)

### 3. Python Service
**Endpoint:** `POST /generate`
- **Python File:** `timetable-engine/main_v25.py` (line 304) or `main_v20.py`
- **Port:** 8000
- **CORS:** Enabled for all origins (configure for production)

## 🚨 Common Communication Issues & Solutions

### Issue 1: "Python timetable service is not running"
**Symptoms:**
- Error: `ECONNREFUSED` or connection refused
- Backend logs: "Python service returned error"

**Cause:** Python service not started

**Solution:**
```bash
cd timetable-engine

# Option 1: Start v2.5 (RECOMMENDED - Metadata-driven optimization)
python main_v25.py

# Option 2: Start v2.0 (Legacy but stable)
python main_v20.py

# Verify service is running
curl http://localhost:8000/docs
```

### Issue 2: "Port 8000 already in use"
**Symptoms:**
- Python service won't start
- Error: Address already in use

**Solution:**
```bash
# Find process using port 8000
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :8000
kill -9 <PID>
```

### Issue 3: Backend can't reach Python service
**Symptoms:**
- Timeout errors
- No response from Python service

**Cause:** Wrong `PYTHON_TIMETABLE_URL` configuration

**Solution:**
```bash
# Check backend/.env
PYTHON_TIMETABLE_URL="http://localhost:8000"

# If Python is on different host/port:
PYTHON_TIMETABLE_URL="http://192.168.1.100:8000"
```

### Issue 4: CORS errors in browser
**Symptoms:**
- Browser console: "CORS policy" errors
- Frontend can't access backend

**Cause:** Next.js proxy not working or backend CORS misconfigured

**Solution 1:** Verify Next.js proxy in `frontend/next.config.js`:
```javascript
async rewrites() {
  return [
    {
      source: '/api/v1/:path*',
      destination: 'http://localhost:5000/api/v1/:path*',
    },
  ];
}
```

**Solution 2:** Restart Next.js dev server:
```bash
cd frontend
npm run dev
```

### Issue 5: Authentication failures
**Symptoms:**
- 401 Unauthorized errors
- "No token provided" errors

**Cause:** JWT token not being sent or invalid

**Solution:**
1. Login again to get fresh token
2. Check browser localStorage for 'token'
3. Verify JWT_SECRET matches in backend/.env

### Issue 6: Validation errors from Python
**Symptoms:**
- 422 Unprocessable Entity
- "Validation errors" from Python service

**Cause:** Data format mismatch between Backend and Python

**Solution:**
Check backend logs for the exact payload sent to Python. Verify:
- Teachers have valid subjects array
- Classes have required fields (name, grade, section, student_count)
- Subjects have periods_per_week
- Time slots are properly formatted

## ✅ How to Test the Communication Chain

### Step 1: Start Python Service
```bash
cd timetable-engine
python main_v25.py

# You should see:
# 🚀 TIMETABLE GENERATION API v2.5 - STARTING UP
# INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 2: Test Python Service Directly
```bash
curl http://localhost:8000/docs
# Should return Swagger documentation page
```

### Step 3: Start Backend
```bash
cd backend
npm run start:dev

# You should see:
# [Nest] INFO [NestFactory] Starting Nest application...
# [Nest] INFO Application is running on: http://localhost:5000
```

### Step 4: Test Backend Health
```bash
curl http://localhost:5000/api/v1/schools
# Should return schools list (might be empty)
```

### Step 5: Start Frontend
```bash
cd frontend
npm run dev

# You should see:
# ready - started server on 0.0.0.0:3000
```

### Step 6: Test Frontend
1. Open browser: `http://localhost:3000`
2. Login with credentials
3. Navigate to: Admin → Timetables → Generate
4. Fill form and click "Generate Timetable"

## 🔍 Debugging Tips

### Enable Verbose Logging

**Backend:**
Backend already logs requests/responses extensively. Check terminal output.

**Frontend:**
Open browser DevTools → Console to see:
- Axios request/response interceptors
- API call details
- Error messages

**Python:**
Python service logs are verbose by default. Check terminal output.

### Check Network Tab

1. Open browser DevTools → Network
2. Filter by "Fetch/XHR"
3. Generate timetable
4. Look for:
   - POST to `/api/v1/timetables/generate` (Frontend → Backend)
   - Check status code (200 OK, 400 Bad Request, 500 Server Error)
   - Inspect request payload
   - Inspect response

### Common Error Codes

| Code | Meaning | Likely Cause |
|------|---------|--------------|
| 401 | Unauthorized | No/invalid JWT token |
| 404 | Not Found | Wrong endpoint URL |
| 422 | Validation Error | Invalid data format |
| 500 | Server Error | Backend error, check logs |
| 502 | Bad Gateway | Python service not responding |
| 504 | Gateway Timeout | Python took too long (>120s) |

## 📦 Environment Variables Reference

### Backend (`backend/.env`)
```bash
DATABASE_URL="file:./dev.db"
JWT_SECRET="dev-secret-key-replace-in-production"
PYTHON_TIMETABLE_URL="http://localhost:8000"  # ← IMPORTANT
PORT=5000
NODE_ENV="development"
CORS_ORIGIN="http://localhost:3000"
```

### Frontend (`frontend/.env.local` - optional)
```bash
NEXT_PUBLIC_API_URL="http://localhost:5000/api/v1"
```

## 🎯 Production Checklist

Before deploying:

- [ ] Change JWT_SECRET to a strong random value
- [ ] Update DATABASE_URL to PostgreSQL connection string
- [ ] Configure PYTHON_TIMETABLE_URL to production Python service
- [ ] Set CORS_ORIGIN to production frontend URL
- [ ] Update Next.js rewrites to production backend URL
- [ ] Use HTTPS for all connections
- [ ] Implement rate limiting
- [ ] Enable request logging and monitoring
- [ ] Set up health check endpoints

## 🚀 Quick Start Commands

```bash
# Terminal 1: Start Python Service (v2.5 recommended)
cd timetable-engine && python main_v25.py

# Terminal 2: Start Backend
cd backend && npm run start:dev

# Terminal 3: Start Frontend
cd frontend && npm run dev
```

Now open browser: `http://localhost:3000`

## 📚 Related Files

**Frontend:**
- `frontend/lib/api.ts` - API client configuration
- `frontend/next.config.js` - Next.js proxy setup
- `frontend/app/admin/timetables/generate/page.tsx` - Generation UI

**Backend:**
- `backend/src/modules/timetables/timetables.controller.ts` - API endpoint
- `backend/src/modules/timetables/timetables.service.ts` - Business logic
- `backend/.env` - Environment configuration

**Python:**
- `timetable-engine/main_v25.py` - Latest service (v2.5, RECOMMENDED)
- `timetable-engine/main_v20.py` - Legacy service (v2.0)
- `timetable-engine/src/models_phase1_v25.py` - Data models

## ⚠️ Known Issues

### Python Service Versions
- **v2.5 (Recommended)**: Metadata-driven optimization, language-agnostic preferences
- **v2.0 (Legacy)**: Stable but lacks advanced features

### Frontend-Backend Auth
- JWT tokens are stored in localStorage (consider httpOnly cookies for production)
- No token refresh mechanism (user must re-login after expiry)

### Python Service Performance
- Timeout set to 120 seconds
- Large timetables (40+ classes) may approach this limit
- Consider increasing timeout for very large schools
