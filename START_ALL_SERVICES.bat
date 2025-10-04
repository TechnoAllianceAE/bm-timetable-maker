@echo off
echo ========================================
echo Starting All Services
echo ========================================
echo.

echo [1/3] Starting Python Timetable Engine (v2.5)...
start "Python Engine" cmd /k "cd timetable-engine && python main_v25.py"
timeout /t 3 >nul

echo [2/3] Starting Backend (NestJS)...
start "Backend API" cmd /k "cd backend && npm run start:dev"
timeout /t 5 >nul

echo [3/3] Starting Frontend (Next.js)...
start "Frontend UI" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================
echo All services starting!
echo ========================================
echo.
echo Python Engine:  http://localhost:8000/docs
echo Backend API:    http://localhost:5000/api/v1
echo Frontend UI:    http://localhost:3000
echo.
echo Press any key to exit this window...
pause >nul
