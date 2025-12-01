@echo off
REM Restart Backend Script
REM This script stops and restarts the FastAPI backend server

echo ========================================
echo   Job Scraper - Backend Restart
echo ========================================
echo.

REM Kill existing Python processes for this project
echo Stopping existing backend processes...
FOR /F "tokens=2" %%i IN ('tasklist ^| findstr "python.exe"') DO (
    taskkill /PID %%i /F 2>nul
)

echo Waiting for processes to terminate...
timeout /t 2 /nobreak >nul

echo.
echo Starting backend API server...
cd /d c:\AI\job_scraper
start "Job Scraper Backend" cmd /k "python -m uvicorn backend.api:app --reload --host 0.0.0.0 --port 8000"

echo.
echo ========================================
echo Backend restarted successfully!
echo API running at http://localhost:8000
echo ========================================
pause
