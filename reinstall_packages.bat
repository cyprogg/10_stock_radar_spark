@echo off
setlocal enabledelayedexpansion

cd /d c:\10_stock_radar_spark

echo.
echo ============================================
echo  패키지 재설치 (가상 환경에 설치)
echo ============================================
echo.

REM 가상 환경의 Python 경로
set VENV_PYTHON=%cd%\backend\venv\Scripts\python.exe

echo [1] Python 경로: %VENV_PYTHON%
%VENV_PYTHON% --version
echo.

echo [2] 패키지 재설치 중 (5-10분 소요)...
echo.

cd backend
%VENV_PYTHON% -m pip install --upgrade pip setuptools wheel
%VENV_PYTHON% -m pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ 설치 실패
    pause
    exit /b 1
)

echo.
echo [3] 설치 확인 중...
%VENV_PYTHON% -c "import fastapi; import uvicorn; print('✅ FastAPI와 Uvicorn 설치 확인됨')"

if errorlevel 1 (
    echo ❌ 확인 실패
    pause
    exit /b 1
)

echo.
echo ✅ 모든 패키지가 올바르게 설치되었습니다!
echo.
pause
