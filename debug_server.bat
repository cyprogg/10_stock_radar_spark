@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

echo.
echo ========== DEBUG 모드 ==========
echo.

REM 가상 환경 활성화
echo [1] 가상 환경 활성화...
if exist "backend\venv\Scripts\activate.bat" (
    call backend\venv\Scripts\activate.bat
    echo ✅ 완료
) else (
    echo ❌ 가상 환경 없음 - 생성 중...
    python -m venv backend\venv
    call backend\venv\Scripts\activate.bat
    echo 패키지 설치 중...
    pip install -r backend\requirements.txt
)
echo.

REM Python 경로 확인
echo [2] Python 경로 확인...
where python
echo.

REM 모듈 임포트 테스트
echo [3] 모듈 임포트 테스트...
cd backend
python -c "from server_v2 import app; print('✅ server_v2 임포트 성공')" 2>&1
if errorlevel 1 (
    echo ❌ server_v2 임포트 실패 - 자세한 오류:
    python -c "import server_v2"
) 
echo.

REM 데이터베이스 테스트
echo [4] 데이터베이스 테스트...
python -c "from database import init_db; init_db(); print('✅ 데이터베이스 초기화 완료')" 2>&1
echo.

REM 포트 확인
echo [5] 포트 8000 상태...
netstat -ano | findstr ":8000"
if errorlevel 1 (
    echo ✅ 포트 8000 사용 가능
) else (
    echo ❌ 포트 8000 이미 사용 중
)
echo.

echo ========== 준비 완료 ==========
echo.
pause
