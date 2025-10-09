@echo off
REM Status Check Script for Windows
REM Checks status of Backend (NestJS), Frontend (Next.js), and Timetable Engine (Python)

echo ==================================
echo Service Status Check
echo ==================================
echo.

set RUNNING_COUNT=0
set TOTAL_COUNT=3

REM 1. Check Timetable Engine (Python - Port 8000)
echo [1/3] Timetable Engine (Python FastAPI)
netstat -ano | findstr :8000 | findstr LISTENING >nul
if %errorlevel% equ 0 (
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do set TIMETABLE_PID=%%a
    echo [92m^✓ Timetable Engine[0m
    echo   Status: [92mRUNNING[0m
    echo   Port: 8000
    echo   PID: !TIMETABLE_PID!
    echo   URL: http://localhost:8000
    set /a RUNNING_COUNT+=1
) else (
    echo [91m^✗ Timetable Engine[0m
    echo   Status: [91mSTOPPED[0m
    echo   Port: 8000
    echo   URL: http://localhost:8000
)
echo.

REM 2. Check Backend (NestJS - Port 5000)
echo [2/3] Backend (NestJS)
netstat -ano | findstr :5000 | findstr LISTENING >nul
if %errorlevel% equ 0 (
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5000 ^| findstr LISTENING') do set BACKEND_PID=%%a
    echo [92m^✓ Backend API[0m
    echo   Status: [92mRUNNING[0m
    echo   Port: 5000
    echo   PID: !BACKEND_PID!
    echo   URL: http://localhost:5000
    set /a RUNNING_COUNT+=1
) else (
    echo [91m^✗ Backend API[0m
    echo   Status: [91mSTOPPED[0m
    echo   Port: 5000
    echo   URL: http://localhost:5000
)
echo.

REM 3. Check Frontend (Next.js - Port 3000)
echo [3/3] Frontend (Next.js)
netstat -ano | findstr :3000 | findstr LISTENING >nul
if %errorlevel% equ 0 (
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000 ^| findstr LISTENING') do set FRONTEND_PID=%%a
    echo [92m^✓ Frontend[0m
    echo   Status: [92mRUNNING[0m
    echo   Port: 3000
    echo   PID: !FRONTEND_PID!
    echo   URL: http://localhost:3000
    set /a RUNNING_COUNT+=1
) else (
    echo [91m^✗ Frontend[0m
    echo   Status: [91mSTOPPED[0m
    echo   Port: 3000
    echo   URL: http://localhost:3000
)
echo.

REM Summary
echo ==================================
if %RUNNING_COUNT% equ %TOTAL_COUNT% (
    echo [92mAll Services Running (%RUNNING_COUNT%/%TOTAL_COUNT%)[0m
) else if %RUNNING_COUNT% equ 0 (
    echo [91mAll Services Stopped (%RUNNING_COUNT%/%TOTAL_COUNT%)[0m
) else (
    echo [93mPartial Services Running (%RUNNING_COUNT%/%TOTAL_COUNT%)[0m
)
echo ==================================
echo.

REM Show saved PIDs if file exists
if exist .service_pids (
    echo Saved PIDs in .service_pids:
    type .service_pids
    echo.
)

REM Show available commands
echo Available commands:
echo   START_ALL_SERVICES.bat  - Start all services
echo   STOP_ALL_SERVICES.bat   - Stop all services
echo   STATUS_ALL_SERVICES.bat - Check service status
echo.

REM Show logs info if services are running
if %RUNNING_COUNT% gtr 0 (
    echo View logs in the logs/ directory:
    netstat -ano | findstr :8000 | findstr LISTENING >nul
    if %errorlevel% equ 0 echo   logs\timetable-engine.log
    netstat -ano | findstr :5000 | findstr LISTENING >nul
    if %errorlevel% equ 0 echo   logs\backend.log
    netstat -ano | findstr :3000 | findstr LISTENING >nul
    if %errorlevel% equ 0 echo   logs\frontend.log
    echo.
)

pause
