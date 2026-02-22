@echo off
setlocal enabledelayedexpansion
REM Stock Radar Spark - Backend 시작 스크립트
REM 일회용 설정 및 서버 시작

echo.
echo ============================================
echo  Stock Radar Spark - Backend 시작
echo  Beta Tester Edition (5명 제한)
echo  2026.02.21
echo ============================================
echo.

REM 0. Python 설치 확인
echo 확인 중: Python 설치...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ❌ 오류: Python이 설치되지 않았거나 PATH에 없습니다
    echo.
    echo 해결 방법:
    echo 1. https://www.python.org 에서 Python 3.10+ 설치
    echo 2. 설치 시 "Add Python to PATH" 체크
    echo 3. 이 창을 닫고 다시 시도
    echo.
    pause
    exit /b 1
)
echo ✅ Python 설치 확인 완료
python --version

REM 1. 백엔드 디렉토리 확인
if not exist "backend\server_v2.py" (
    echo.
    echo ❌ 오류: backend 디렉토리를 찾을 수 없습니다
    echo 현재 디렉토리: %cd%
    echo.
    echo 대신 이 폴더에서 실행하세요:
    echo c:\10_stock_radar_spark\
    echo.
    pause
    exit /b 1
)

echo ✅ 백엔드 디렉토리 확인 완료

REM 2. 가상 환경 확인 및 생성
if not exist "backend\venv" (
    echo 🔧 Python 가상 환경 생성 중...
    pushd backend
    python -m venv venv
    if errorlevel 1 (
        echo.
        echo ❌ 가상 환경 생성 실패
        echo 해결 방법:
        echo 1. Python 재설치 (https://www.python.org)
        echo 2. 또는 이 명령을 PowerShell에서 실행:
        echo    python -m venv backend\venv
        echo.
        popd
        pause
        exit /b 1
    )
    popd
    echo ✅ 가상 환경 생성 완료
) else (
    echo ✅ 가상 환경이 이미 존재합니다
)

REM 3. 가상 환경 활성화
echo 🔄 가상 환경 활성화 중...
call backend\venv\Scripts\activate.bat
if errorlevel 1 (
    echo.
    echo ❌ 가상 환경 활성화 실패
    echo.
    pause
    exit /b 1
)
echo ✅ 가상 환경 활성화 완료

REM 4. 패키지 설치 (처음 1회만)
if not exist "backend\venv\Lib\site-packages\fastapi" (
    echo 📦 패키지 설치 중 (첫 실행, 5-10분 소요)...
    pushd backend
    pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo ❌ 패키지 설치 실패
        echo 해결 방법:
        echo 1. 인터넷 연결 확인
        echo 2. 다시 시도
        echo.
        popd
        pause
        exit /b 1
    )
    popd
    echo ✅ 패키지 설치 완료
) else (
    echo ✅ 패키지가 이미 설치되어 있습니다
)

REM 5. 데이터베이스 초기화
echo 💾 데이터베이스 초기화 중...
pushd backend
python -c "from database import init_db; init_db()"
if errorlevel 1 (
    echo ⚠️  데이터베이스 초기화 중 경고 발생 (무시해도 됨)
) else (
    echo ✅ 데이터베이스 초기화 완료
)
popd

REM 6. 환경 변수 확인
echo 🔐 환경 변수 확인 중...
if not exist ".env" (
    echo ⚠️  .env 파일이 없습니다. 기본값으로 시작합니다.
)

REM 7. 서버 시작
echo.
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
echo    - 터미널 닫기 전에 서버를 반드시 중지해주세요
echo.
echo ============================================
echo.

pushd backend

REM 개발 서버 (자동 리로드, 1 워커)
python -m uvicorn server_v2:app --reload --host 0.0.0.0 --port 8000 --log-level info

if errorlevel 1 (
    echo.
    echo ❌ 서버 시작 실패
    echo.
    echo 문제 해결:
    echo 1. 인터넷 연결 확인
    echo 2. 포트 8000이 사용 중인지 확인
    echo    netstat -ano ^| findstr 8000
    echo 3. Python 버전 확인
    echo    python --version
    echo.
    popd
    pause
    exit /b 1
)

popd

pause
