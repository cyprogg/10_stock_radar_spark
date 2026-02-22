@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

echo.
echo ============================================
echo  패키지 설치 중 (처음 1회만 수행)
echo ============================================
echo.

REM 가상 환경 생성 및 활성화
echo [1] 가상 환경 설정 중...
if not exist "backend\venv" (
    echo   가상 환경 생성 중...
    python -m venv backend\venv
    if errorlevel 1 (
        echo ❌ 가상 환경 생성 실패
        pause
        exit /b 1
    )
)
echo ✅ 가상 환경 OK
echo.

REM 가상 환경 활성화
echo [2] 가상 환경 활성화 중...
call backend\venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ 활성화 실패
    pause
    exit /b 1
)
echo ✅ 활성화 완료
echo.

REM 업그레이드 pip
echo [3] pip 업그레이드 중...
python -m pip install --upgrade pip setuptools wheel >nul 2>&1
echo ✅ pip 준비 완료
echo.

REM 패키지 설치
echo [4] 패키지 설치 중 (5-10분 소요)...
echo    설치 중: fastapi, uvicorn, sqlalchemy, pydantic, python-dotenv, 등...
echo.
cd backend
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ 패키지 설치 실패!
    echo 다음 명령으로 수동 설치 시도:
    echo   pip install -r backend\requirements.txt
    echo.
    pause
    exit /b 1
)
echo.
echo ✅ 모든 패키지 설치 완료!
echo.

REM 설치 확인
echo [5] 설치 확인 중...
python -c "import fastapi; import uvicorn; import sqlalchemy; import pydantic; print('✅ FastAPI, Uvicorn, SQLAlchemy, Pydantic 확인됨')"
if errorlevel 1 (
    echo ❌ 일부 모듈 확인 실패
    pause
    exit /b 1
)
echo.

echo ============================================
echo  ✅ 준비 완료! 이제 서버를 시작할 수 있습니다
echo ============================================
echo.
echo 다음 명령으로 서버 시작:
echo   .\run_server.bat
echo.
pause
