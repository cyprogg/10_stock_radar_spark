@echo off
REM Stock Radar Spark - Backend 시작 스크립트
REM 일회용 설정 및 서버 시작

echo.
echo ============================================
echo  Stock Radar Spark - Backend 시작
echo  Beta Tester Edition (5명 제한)
echo  2026.02.21
echo ============================================
echo.

REM 1. 백엔드 디렉토리 확인
if not exist "backend\server_v2.py" (
    echo ❌ 오류: backend 디렉토리를 찾을 수 없습니다
    echo 현재 디렉토리: %cd%
    pause
    exit /b 1
)

echo ✅ 백엔드 디렉토리 확인 완료

REM 2. 가상 환경 확인 및 생성
if not exist "backend\venv" (
    echo 🔧 Python 가상 환경 생성 중...
    cd backend
    python -m venv venv
    if errorlevel 1 (
        echo ❌ 가상 환경 생성 실패
        pause
        exit /b 1
    )
    cd..
    echo ✅ 가상 환경 생성 완료
) else (
    echo ✅ 가상 환경이 이미 존재합니다
)

REM 3. 가상 환경 활성화
echo 🔄 가상 환경 활성화 중...
call backend\venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ 가상 환경 활성화 실패
    pause
    exit /b 1
)
echo ✅ 가상 환경 활성화 완료

REM 4. 패키지 설치 (처음 1회만)
if not exist "backend\venv\Lib\site-packages\fastapi" (
    echo 📦 패키지 설치 중 (첫 실행, 5-10분 소요)...
    cd backend
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ 패키지 설치 실패
        pause
        exit /b 1
    )
    cd..
    echo ✅ 패키지 설치 완료
) else (
    echo ✅ 패키지가 이미 설치되어 있습니다
)

REM 5. 데이터베이스 초기화
echo 💾 데이터베이스 초기화 중...
cd backend
python -c "from database import init_db; init_db()"
if errorlevel 1 (
    echo ⚠️  데이터베이스 초기화 중 경고 발생 (무시해도 됨)
) else (
    echo ✅ 데이터베이스 초기화 완료
)
cd..

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

cd backend

REM 개발 서버 (자동 리로드, 1 워커)
python -m uvicorn server_v2:app --reload --host 0.0.0.0 --port 8000 --log-level info

if errorlevel 1 (
    echo.
    echo ❌ 서버 시작 실패
    pause
    exit /b 1
)

pause
