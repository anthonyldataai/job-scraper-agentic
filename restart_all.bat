@echo off
REM Restart All Services Script
REM This script stops and restarts both frontend and backend

echo ========================================
echo   Job Scraper - Full Restart
echo ========================================
echo.

REM Kill existing processes
echo Stopping all existing processes...
FOR /F "tokens=2" %%i IN ('tasklist ^| findstr "node.exe python.exe"') DO (
    taskkill /PID %%i /F 2>nul
)

echo Waiting for processes to terminate...
timeout /t 3 /nobreak >nul

echo.
echo Starting backend API server...
cd /d c:\AI\job_scraper
start "Job Scraper Backend" cmd /k "python -m uvicorn backend.api:app --reload --host 0.0.0.0 --port 8000"

echo Waiting for backend to initialize...
timeout /t 3 /nobreak >nul

echo.
echo Starting frontend development server...
cd /d c:\AI\job_scraper\frontend
start "Job Scraper Frontend" cmd /k "npm run dev"

echo.
echo ========================================
echo All services restarted successfully!
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo ========================================
pause
