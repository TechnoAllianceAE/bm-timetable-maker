@echo off
echo ========================================
echo Stopping All Services
echo ========================================
echo.

echo [1/3] Stopping Python Timetable Engine (Port 8000)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
    if !errorlevel! equ 0 (
        echo   - Killed process %%a
    )
)

echo [2/3] Stopping Backend API (Port 5000)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5000" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
    if !errorlevel! equ 0 (
        echo   - Killed process %%a
    )
)

echo [3/3] Stopping Frontend UI (Port 3000)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":3000" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
    if !errorlevel! equ 0 (
        echo   - Killed process %%a
    )
)

echo.
echo Waiting for processes to terminate...
timeout /t 3 >nul

echo.
echo ========================================
echo Verifying Service Status...
echo ========================================
echo.

set ALL_STOPPED=1

netstat -ano | findstr ":8000" | findstr "LISTENING" >nul
if %errorlevel% equ 0 (
    echo [FAIL] Python Engine: Still running on port 8000
    set ALL_STOPPED=0
) else (
    echo [OK] Python Engine: Port 8000 is free
)

netstat -ano | findstr ":5000" | findstr "LISTENING" >nul
if %errorlevel% equ 0 (
    echo [FAIL] Backend API: Still running on port 5000
    set ALL_STOPPED=0
) else (
    echo [OK] Backend API: Port 5000 is free
)

netstat -ano | findstr ":3000" | findstr "LISTENING" >nul
if %errorlevel% equ 0 (
    echo [FAIL] Frontend UI: Still running on port 3000
    set ALL_STOPPED=0
) else (
    echo [OK] Frontend UI: Port 3000 is free
)

echo.
echo ========================================
if %ALL_STOPPED% equ 1 (
    echo All services stopped successfully!
) else (
    echo Warning: Some services may still be running
)
echo ========================================
echo.
echo Press any key to exit...
pause >nul
