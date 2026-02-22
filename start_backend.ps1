# Stock Radar Spark - Backend 시작 스크립트 (PowerShell)
# 실행: .\start_backend.ps1 또는 더블클릭

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host " Stock Radar Spark - Backend 시작" -ForegroundColor Green
Write-Host " Beta Tester Edition (5명 제한)" -ForegroundColor Green
Write-Host " 2026.02.21" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# 현재 디렉토리
Write-Host "현재 디렉토리: $(Get-Location)" -ForegroundColor Yellow
Write-Host ""

# Step 1: Python 확인
Write-Host "[Step 1] Python 확인 중..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host $pythonVersion -ForegroundColor Green
    Write-Host "✅ Python 설치됨" -ForegroundColor Green
} catch {
    Write-Host "❌ Python을 찾을 수 없습니다" -ForegroundColor Red
    Write-Host "해결: https://www.python.org 에서 Python 3.10+ 설치" -ForegroundColor Yellow
    Read-Host "아무 키나 누르면 종료합니다"
    exit 1
}
Write-Host ""

# Step 2: 폴더 확인
Write-Host "[Step 2] 폴더 확인 중..." -ForegroundColor Yellow
if (-not (Test-Path "backend\server_v2.py")) {
    Write-Host "❌ backend\server_v2.py 를 찾을 수 없습니다" -ForegroundColor Red
    Write-Host "현재 위치에서 실행하세요: c:\10_stock_radar_spark\" -ForegroundColor Yellow
    Read-Host "아무 키나 누르면 종료합니다"
    exit 1
}
Write-Host "✅ backend 폴더 OK" -ForegroundColor Green
Write-Host ""

# Step 3: 가상 환경 설정
Write-Host "[Step 3] 가상 환경 설정 중..." -ForegroundColor Yellow
if (-not (Test-Path "backend\venv")) {
    Write-Host "  - 가상 환경 생성 (처음 1회만 시간 걸림)..." -ForegroundColor Cyan
    python -m venv backend\venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ 가상 환경 생성 실패" -ForegroundColor Red
        Read-Host "아무 키나 누르면 종료합니다"
        exit 1
    }
}
Write-Host "✅ 가상 환경 OK" -ForegroundColor Green
Write-Host ""

# Step 4: 가상 환경 활성화
Write-Host "[Step 4] 가상 환경 활성화 중..." -ForegroundColor Yellow
& .\backend\venv\Scripts\Activate.ps1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ 가상 환경 활성화 실패" -ForegroundColor Red
    Read-Host "아무 키나 누르면 종료합니다"
    exit 1
}
Write-Host "✅ 가상 환경 활성화 완료" -ForegroundColor Green
Write-Host ""

# Step 5: 패키지 설치
Write-Host "[Step 5] 패키지 확인 중..." -ForegroundColor Yellow
$packagesExists = Test-Path "backend\venv\Lib\site-packages\fastapi"
if (-not $packagesExists) {
    Write-Host "  - 패키지 설치 중 (5-10분 소요)..." -ForegroundColor Cyan
    pip install -r backend\requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ 패키지 설치 실패" -ForegroundColor Red
        Write-Host "다시 시도하세요: pip install -r backend\requirements.txt" -ForegroundColor Yellow
        Read-Host "아무 키나 누르면 종료합니다"
        exit 1
    }
}
Write-Host "✅ 패키지 OK" -ForegroundColor Green
Write-Host ""

# Step 6: 데이터베이스 초기화
Write-Host "[Step 6] 데이터베이스 초기화 중..." -ForegroundColor Yellow
Push-Location backend
python -c "from database import init_db; init_db()"
Pop-Location
Write-Host "✅ 데이터베이스 OK" -ForegroundColor Green
Write-Host ""

# Step 7: 포트 확인
Write-Host "[Step 7] 포트 8000 확인 중..." -ForegroundColor Yellow
$portInUse = netstat -ano | Select-String ":8000"
if ($portInUse) {
    Write-Host "⚠️  포트 8000이 이미 사용 중입니다!" -ForegroundColor Red
    Write-Host ""
    Write-Host "해결 방법:" -ForegroundColor Yellow
    Write-Host "1. 이전 서버 중지: Ctrl+C" -ForegroundColor Cyan
    Write-Host "2. 또는 다른 포트 사용:" -ForegroundColor Cyan
    Write-Host "   python -m uvicorn server_v2:app --port 8001" -ForegroundColor Cyan
    Write-Host ""
    Read-Host "아무 키나 누르면 종료합니다"
    exit 1
}
Write-Host "✅ 포트 8000 사용 가능" -ForegroundColor Green
Write-Host ""

# Step 8: 서버 시작
Write-Host "============================================" -ForegroundColor Cyan
Write-Host " 🚀 서버 시작 중..." -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📍 접속 URL:" -ForegroundColor Green
Write-Host "   - 프론트엔드: http://localhost:8000" -ForegroundColor Cyan
Write-Host "   - API 문서: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "   - 상태 확인: http://localhost:8000/api/status" -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 팁:" -ForegroundColor Yellow
Write-Host "   - Ctrl+C로 서버 중지" -ForegroundColor Cyan
Write-Host "   - 새 PowerShell에서 테스트 명령 실행 가능" -ForegroundColor Cyan
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

Push-Location backend
python -m uvicorn server_v2:app --reload --host 0.0.0.0 --port 8000 --log-level info
Pop-Location

Write-Host ""
Write-Host "❌ 서버가 중지되었습니다" -ForegroundColor Red
Write-Host ""
Read-Host "아무 키나 누르면 종료합니다"
