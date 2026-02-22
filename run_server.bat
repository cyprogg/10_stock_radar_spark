@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

echo.
echo ============================================
echo  Stock Radar Spark - Backend 시작
echo  Beta Tester Edition (5명 제한)
echo  2026.02.21
echo ============================================
echo.

REM 현재 디렉토리 확인
echo 현재 디렉토리: %cd%
echo.

REM Python 확인
echo [Step 1] Python 확인 중...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python을 찾을 수 없습니다
    echo.
    echo 해결 방법:
    echo - Python 3.10+ 설치: https://www.python.org
    echo - 설치 시 "Add Python to PATH" 체크
    echo - 클릭: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)
python --version
echo ✅ Python 설치됨
echo.

REM 폴더 확인
echo [Step 2] 폴더 확인 중...
if not exist "backend\server_v2.py" (
    echo ❌ backend\server_v2.py 를 찾을 수 없습니다
    echo.
    echo 현재 위치에서 실행하세요:
    echo c:\10_stock_radar_spark\
    echo.
    pause
    exit /b 1
)
echo ✅ backend 폴더 OK
echo.

REM 가상 환경 생성
echo [Step 3] 가상 환경 설정 중...
if not exist "backend\venv" (
    echo   - 가상 환경 생성 (처음 1회만 시간 걸림)...
    call python -m venv backend\venv
    if errorlevel 1 (
        echo ❌ 가상 환경 생성 실패
        pause
        exit /b 1
    )
)
echo ✅ 가상 환경 OK
echo.

REM 가상 환경 활성화
echo [Step 4] 가상 환경 활성화 중...
call backend\venv\Scripts\activate.bat
echo ✅ 가상 환경 활성화 완료
echo.

REM 패키지 설치
echo [Step 5] 패키지 확인 중...
if not exist "backend\venv\Lib\site-packages\fastapi" (
    echo   - 패키지 설치 중 (5-10분 소요)...
    pip install -r backend\requirements.txt
    if errorlevel 1 (
        echo ❌ 패키지 설치 실패
        echo 다시 시도하세요: pip install -r backend\requirements.txt
        pause
        exit /b 1
    )
)
echo ✅ 패키지 OK
echo.

REM 데이터베이스 초기화
echo [Step 6] 데이터베이스 초기화 중...
python -c "from database import init_db; init_db()"
echo ✅ 데이터베이스 OK
echo.

REM 포트 확인
echo [Step 7] 포트 8000 확인 중...
netstat -ano | findstr ":8000" >nul 2>&1
if not errorlevel 1 (
    echo ⚠️  포트 8000이 이미 사용 중입니다!
    echo.
    echo 해결 방법:
    echo 1. 이전 서버 중지: Ctrl+C
    echo 2. 또는 다른 포트 사용: python -m uvicorn server_v2:app --port 8001
    echo.
    pause
    exit /b 1
)
echo ✅ 포트 8000 사용 가능
echo.

REM 서버 시작
echo ============================================
echo  🚀 서버 시작 중...
echo ============================================
echo.
echo 📍 접속 URL:
echo    - 프론트엔드: http://localhost:8000
echo    - API 문서: http://localhost:8000/docs
echo    - 상태 확인: http://localhost:8000/api/status
echo.
echo 💡 팁:
echo    - Ctrl+C로 서버 중지
echo    - 새 터미널에서 테스트 명령 실행 가능
echo.
echo ============================================
echo.

cd backend
python -m uvicorn server_v2:app --reload --host 0.0.0.0 --port 8000 --log-level info

echo.
echo ❌ 서버가 중지되었습니다
echo.
pause
