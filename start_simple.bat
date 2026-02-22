@echo off
setlocal enabledelayedexpansion

REM Use the virtual environment's Python directly
set PYTHON=%cd%\backend\venv\Scripts\python.exe

echo Checking Python version...
%PYTHON% --version

cd backend

echo.
echo Testing FastAPI import...
%PYTHON% -c "from server_v2 import app; print('✅ FastAPI loaded successfully')"
if errorlevel 1 (
    echo ❌ ERROR loading FastAPI
    pause
    exit /b 1
)

echo.
echo Starting server on http://localhost:8000...
%PYTHON% -m uvicorn server_v2:app --host 0.0.0.0 --port 8000 --log-level info

pause
