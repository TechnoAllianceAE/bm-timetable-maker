@echo off
echo ========================================
echo Starting All Services
echo ========================================
echo.

echo [1/3] Starting Python Timetable Engine (v2.5)...
start "Python Engine" cmd /k "cd timetable-engine && py main_v25.py"
echo Waiting for Python Engine to start...
timeout /t 5 >nul

echo [2/3] Starting Backend (NestJS)...
start "Backend API" cmd /k "cd backend && npm run start:dev"
echo Waiting for Backend to start...
timeout /t 8 >nul

echo [3/3] Starting Frontend (Next.js)...
start "Frontend UI" cmd /k "cd frontend && npm run dev"
echo Waiting for Frontend to start...
timeout /t 5 >nul

echo.
echo ========================================
echo Checking Service Status...
echo ========================================
echo.

netstat -ano | findstr ":8000" >nul
if %errorlevel% equ 0 (
    echo [OK] Python Engine:  http://localhost:8000/docs
) else (
    echo [FAIL] Python Engine: Port 8000 not active
)

netstat -ano | findstr ":5000" >nul
if %errorlevel% equ 0 (
    echo [OK] Backend API:     http://localhost:5000/api/v1
) else (
    echo [FAIL] Backend API: Port 5000 not active
)

netstat -ano | findstr ":3000" >nul
if %errorlevel% equ 0 (
    echo [OK] Frontend UI:     http://localhost:3000
) else (
    echo [FAIL] Frontend UI: Port 3000 not active
)

echo.
echo ========================================
echo Startup Complete!
echo ========================================
echo.
echo Press any key to exit this window...
pause >nul
