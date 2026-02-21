# Stock Radar Spark - Backend 시작 스크립트 (PowerShell)
# 실행: .\start_backend.ps1
# 또는: powershell -ExecutionPolicy Bypass -File start_backend.ps1

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host " Stock Radar Spark - Backend 시작" -ForegroundColor Green
Write-Host " Beta Tester Edition (5명 제한)" -ForegroundColor Green
Write-Host " 2026.02.21" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# 1. 백엔드 디렉토리 확인
Write-Host "✅ 백엔드 디렉토리 확인 중..." -ForegroundColor Yellow
if (-not (Test-Path "backend\server_v2.py")) {
    Write-Host "❌ 오류: backend\server_v2.py를 찾을 수 없습니다" -ForegroundColor Red
    Write-Host "현재 디렉토리: $(Get-Location)" -ForegroundColor Red
    Read-Host "아무 키나 누르면 종료합니다"
    exit 1
}
Write-Host "✅ 백엔드 디렉토리 확인 완료" -ForegroundColor Green

# 2. 가상 환경 확인 및 생성
if (-not (Test-Path "backend\venv")) {
    Write-Host "🔧 Python 가상 환경 생성 중..." -ForegroundColor Yellow
    Set-Location backend
    
    try {
        python -m venv venv
        Set-Location ..
        Write-Host "✅ 가상 환경 생성 완료" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ 가상 환경 생성 실패: $_" -ForegroundColor Red
        Read-Host "아무 키나 누르면 종료합니다"
        exit 1
    }
} else {
    Write-Host "✅ 가상 환경이 이미 존재합니다" -ForegroundColor Green
}

# 3. 가상 환경 활성화
Write-Host "🔄 가상 환경 활성화 중..." -ForegroundColor Yellow
try {
    & .\backend\venv\Scripts\Activate.ps1
    Write-Host "✅ 가상 환경 활성화 완료" -ForegroundColor Green
}
catch {
    Write-Host "❌ 가상 환경 활성화 실패: $_" -ForegroundColor Red
    Read-Host "아무 키나 누르면 종료합니다"
    exit 1
}

# 4. 패키지 설치 (처음 1회만)
if (-not (Test-Path "backend\venv\Lib\site-packages\fastapi")) {
    Write-Host "📦 패키지 설치 중 (첫 실행, 5-10분 소요)..." -ForegroundColor Yellow
    
    Set-Location backend
    try {
        pip install -r requirements.txt
        Set-Location ..
        Write-Host "✅ 패키지 설치 완료" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ 패키지 설치 실패: $_" -ForegroundColor Red
        Read-Host "아무 키나 누르면 종료합니다"
        exit 1
    }
} else {
    Write-Host "✅ 패키지가 이미 설치되어 있습니다" -ForegroundColor Green
}

# 5. 데이터베이스 초기화
Write-Host "💾 데이터베이스 초기화 중..." -ForegroundColor Yellow

Set-Location backend
try {
    python -c "from database import init_db; init_db()"
    Write-Host "✅ 데이터베이스 초기화 완료" -ForegroundColor Green
}
catch {
    Write-Host "⚠️  데이터베이스 초기화 중 경고 (무시해도 됨): $_" -ForegroundColor Yellow
}
Set-Location ..

# 6. 환경 변수 확인
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  .env 파일이 없습니다. 기본값으로 시작합니다." -ForegroundColor Yellow
}

# 7. 서버 시작
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host " 🚀 서버 시작 중..." -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📍 접속 URL:" -ForegroundColor Cyan
Write-Host "   - 프론트엔드: http://localhost:8000" -ForegroundColor Green
Write-Host "   - API 문서: http://localhost:8000/docs" -ForegroundColor Green
Write-Host "   - 상태 확인: http://localhost:8000/api/status" -ForegroundColor Green
Write-Host ""
Write-Host "💡 팁:" -ForegroundColor Cyan
Write-Host "   - Ctrl+C로 서버 중지" -ForegroundColor Green
Write-Host "   - 창 닫기 전에 서버를 반드시 중지해주세요" -ForegroundColor Green
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

Set-Location backend

try {
    python -m uvicorn server_v2:app --reload --host 0.0.0.0 --port 8000 --log-level info
}
catch {
    Write-Host ""
    Write-Host "❌ 서버 시작 실패: $_" -ForegroundColor Red
    Read-Host "아무 키나 누르면 종료합니다"
    exit 1
}
