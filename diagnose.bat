@echo off
REM 문제 진단 스크립트
echo.
echo ============================================
echo  Stock Radar Spark - 진단 도구
echo ============================================
echo.

REM 1. Python 확인
echo [1] Python 확인 중...
python --version
if errorlevel 1 (
    echo ❌ Python을 찾을 수 없습니다
    echo 해결: https://www.python.org 에서 Python 3.10+ 설치
    echo 설치 시 "Add Python to PATH" 반드시 체크!
) else (
    echo ✅ Python 설치됨
)
echo.

REM 2. 폴더 구조 확인
echo [2] 폴더 구조 확인 중...
if exist "backend\server_v2.py" (
    echo ✅ backend/server_v2.py 파일 OK
) else (
    echo ❌ backend/server_v2.py 파일 없음
    echo 현재 디렉토리: %cd%
    echo 이 폴더에서 실행해야 함: c:\10_stock_radar_spark\
)
echo.

if exist "backend\requirements.txt" (
    echo ✅ backend/requirements.txt 파일 OK
) else (
    echo ❌ backend/requirements.txt 파일 없음
)
echo.

REM 3. 가상 환경 확인
echo [3] 가상 환경 확인 중...
if exist "backend\venv\" (
    echo ✅ 가상 환경 폴더 존재
    if exist "backend\venv\Scripts\activate.bat" (
        echo ✅ activate.bat 파일 OK
    ) else (
        echo ❌ activate.bat 파일 없음 - 가상 환경 재생성 필요
    )
) else (
    echo ⚠️  가상 환경 폴더 없음 (처음 실행 시 자동 생성됨)
)
echo.

REM 4. 포트 확인
echo [4] 포트 8000 확인 중...
netstat -ano | findstr ":8000" >nul 2>&1
if errorlevel 1 (
    echo ✅ 포트 8000 사용 가능
) else (
    echo ⚠️  포트 8000이 이미 사용 중입니다
    echo 다른 앱 중지 또는 포트 확인:
    echo    netstat -ano | findstr 8000
)
echo.

REM 5. .env 파일 확인
echo [5] 환경 설정 파일 확인 중...
if exist ".env" (
    echo ✅ .env 파일 존재
) else (
    echo ℹ️  .env 파일 없음 (기본값 사용됨)
)
echo.

echo ============================================
echo 진단 완료!
echo ============================================
echo.
echo 다음 단계:
echo 1. 위의 모든 항목이 ✅ 또는 ℹ️ 이어야 함
echo 2. ❌ 항목이 있으면 해당 해결 방법 실행
echo 3. 그 후 start_backend.bat 다시 실행
echo.
pause
