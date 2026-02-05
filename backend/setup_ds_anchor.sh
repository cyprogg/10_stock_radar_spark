#!/bin/bash
# DS-Anchor 빠른 시작 스크립트
# 모든 의존성을 확인하고 시스템을 실행합니다.

set -e

echo "🚀 DS-Anchor 시스템 시작"
echo ""

# 1. Python 버전 확인
echo "1️⃣ Python 버전 확인..."
python3 --version || {
    echo "❌ Python 3가 설치되어 있지 않습니다."
    exit 1
}

# 2. 필수 패키지 설치
echo ""
echo "2️⃣ Python 패키지 설치..."
pip install -r requirements.txt

# 3. Playwright 설치
echo ""
echo "3️⃣ Playwright 브라우저 설치..."
playwright install chromium

# 4. FFmpeg 확인
echo ""
echo "4️⃣ FFmpeg 확인..."
if command -v ffmpeg &> /dev/null; then
    echo "✅ FFmpeg 설치됨: $(ffmpeg -version | head -n1)"
else
    echo "⚠️  FFmpeg가 설치되어 있지 않습니다."
    echo "   Ubuntu/Debian: sudo apt install ffmpeg"
    echo "   macOS: brew install ffmpeg"
    echo "   Windows: https://ffmpeg.org/download.html"
fi

# 5. edge-tts 확인
echo ""
echo "5️⃣ edge-tts 확인..."
edge-tts --list-voices | grep "ko-KR-InJoonNeural" || {
    echo "⚠️  한국어 음성이 확인되지 않습니다."
}

# 6. 디렉토리 생성
echo ""
echo "6️⃣ 디렉토리 생성..."
mkdir -p output
mkdir -p logs
chmod +x make_video.sh

# 7. API 서버 확인
echo ""
echo "7️⃣ API 서버 확인..."
if curl -s "http://127.0.0.1:8125/regime?key=ds-test-2026" > /dev/null; then
    echo "✅ API 서버 실행 중"
else
    echo "⚠️  API 서버가 실행되지 않았습니다."
    echo "   실행: python server_v2.py"
fi

# 8. 완료
echo ""
echo "✅ 모든 준비가 완료되었습니다!"
echo ""
echo "📋 사용법:"
echo "   한국장: python ds_anchor_auto.py KR"
echo "   미국장: python ds_anchor_auto.py US"
echo ""
echo "⏰ Cron 설정:"
echo "   한국장: 0 18 * * * cd $(pwd) && python ds_anchor_auto.py KR >> logs/kr.log 2>&1"
echo "   미국장: 0 7 * * * cd $(pwd) && python ds_anchor_auto.py US >> logs/us.log 2>&1"
