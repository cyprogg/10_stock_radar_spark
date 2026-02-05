#!/usr/bin/env python3
"""
DS-Anchor 자동 방송 시스템 (KR 전용)

기능:
- 대본 생성 (API 호출)
- 음성 생성 (edge-tts)
- 대시보드 캡처
- 영상 합성
- 유튜브 업로드

실행: python ds_anchor_kr.py
"""

import sys
import time
import subprocess
import requests
from datetime import datetime

# -----------------------
# KR 전용 설정
# -----------------------
API = "http://127.0.0.1:8125"
ACCESS_KEY = "ds-test-2026"

MARKET = "KR"          # 한국장 고정
MAX_RETRY = 3          # 장애 재시도 횟수
RETRY_WAIT = 60        # 재시도 간격(초)

# 한국 휴장일 (필요 시 확장)
KR_HOLIDAYS = {
    "2026-01-01",  # 신정
    "2026-02-11",  # 설 예시
}

# -----------------------
# Utils
# -----------------------
def today():
    """오늘 날짜 (YYYY-MM-DD)"""
    return datetime.now().strftime("%Y-%m-%d")

def today_compact():
    """오늘 날짜 (YYYYMMDD)"""
    return datetime.now().strftime("%Y%m%d")

def is_holiday():
    """한국 휴장일 확인"""
    return today() in KR_HOLIDAYS

def log(msg):
    """타임스탬프와 함께 로그 출력"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {msg}")

# -----------------------
# Main
# -----------------------
def main():
    log(f"DS-Anchor START | Market: {MARKET} | Date: {today()}")
    
    # 휴장일 체크
    if is_holiday():
        log("⏸️  오늘은 한국 시장 휴장일입니다. 스킵합니다.")
        return 0
    
    # 재시도 루프
    for attempt in range(1, MAX_RETRY + 1):
        log(f"🎬 시도 {attempt}/{MAX_RETRY}")
        
        try:
            # 1. 대본 생성 (API 호출)
            log("1️⃣ 대본 생성 중...")
            url = f"{API}/generate_ds_anchor_script?key={ACCESS_KEY}"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            script = response.json().get("script", "")
            
            if not script:
                raise ValueError("대본이 비어있습니다.")
            
            with open("script.txt", "w", encoding="utf-8") as f:
                f.write(script)
            log(f"   ✅ 대본 저장 완료 ({len(script)} 글자)")
            
            # 2. 음성 생성 (edge-tts)
            log("2️⃣ 음성 생성 중...")
            subprocess.run([
                "edge-tts",
                "--voice", "ko-KR-InJoonNeural",
                "--rate", "-5%",
                "--pitch", "-5Hz",
                "--file", "script.txt",
                "--write-media", "output/voice.mp3"
            ], check=True)
            log("   ✅ 음성 생성 완료 (output/voice.mp3)")
            
            # 3. 대시보드 캡처
            log("3️⃣ 대시보드 캡처 중...")
            subprocess.run(["python", "capture_dashboard.py"], check=True)
            log("   ✅ 대시보드 캡처 완료")
            
            # 4. 영상 합성
            log("4️⃣ 영상 합성 중...")
            subprocess.run(["bash", "make_video.sh"], check=True)
            log("   ✅ 영상 합성 완료")
            
            # 5. 유튜브 업로드
            log("5️⃣ 유튜브 업로드 중...")
            video_path = f"output/ds_anchor_{today_compact()}.mp4"
            subprocess.run(["python", "upload_youtube.py", video_path], check=True)
            log("   ✅ 유튜브 업로드 완료")
            
            # 성공
            log("🎉 모든 작업 완료!")
            return 0
            
        except Exception as e:
            log(f"❌ 오류 발생: {e}")
            
            if attempt < MAX_RETRY:
                log(f"⏳ {RETRY_WAIT}초 후 재시도합니다...")
                time.sleep(RETRY_WAIT)
            else:
                log(f"💥 최대 재시도 횟수({MAX_RETRY})를 초과했습니다.")
                return 1
    
    return 1

if __name__ == "__main__":
    sys.exit(main())
