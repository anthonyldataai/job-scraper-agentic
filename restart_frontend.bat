@echo off
REM Restart Frontend Script
REM This script stops and restarts the Vite development server

echo ========================================
echo   Job Scraper - Frontend Restart
echo ========================================
echo.

REM Kill existing Node processes for this project
echo Stopping existing frontend processes...
FOR /F "tokens=2" %%i IN ('tasklist ^| findstr "node.exe"') DO (
    taskkill /PID %%i /F 2>nul
)

echo Waiting for processes to terminate...
timeout /t 2 /nobreak >nul

echo.
echo Starting frontend development server...
cd /d c:\AI\job_scraper\frontend
start "Job Scraper Frontend" cmd /k "npm run dev"

echo.
echo ========================================
echo Frontend restarted successfully!
echo Check the new window for the dev server
echo ========================================
pause
