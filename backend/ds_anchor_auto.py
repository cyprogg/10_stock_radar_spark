#!/usr/bin/env python3
"""
DS-Anchor 멀티 마켓 자동 방송 시스템

사용법:
    python ds_anchor_auto.py         # 기본값: KR
    python ds_anchor_auto.py KR      # 한국장
    python ds_anchor_auto.py US      # 미국장

기능:
- 마켓별 휴장일 자동 확인
- 대본 생성 → 음성 → 영상 → 유튜브 자동화
- 재시도 로직 (최대 3회)
"""

import sys
import time
import subprocess
import requests
from datetime import datetime
from zoneinfo import ZoneInfo

try:
    import exchange_calendars as xcals
    CALENDAR_AVAILABLE = True
except ImportError:
    CALENDAR_AVAILABLE = False

# -----------------------
# 공통 설정
# -----------------------
API = "http://127.0.0.1:8125"
ACCESS_KEY = "ds-test-2026"
MAX_RETRY = 3
RETRY_WAIT = 60  # 초

# -----------------------
# 마켓별 설정
# -----------------------
KR_HOLIDAYS = {
    "2026-01-01",  # 신정
    "2026-02-11",  # 설 예시
}

US_HOLIDAYS = {
    "2026-01-01",  # New Year's Day
    "2026-07-04",  # Independence Day
}

MARKET_CONFIG = {
    "KR": {
        "name": "한국",
        "timezone": "Asia/Seoul",
        "holidays": KR_HOLIDAYS,
        "voice": "ko-KR-InJoonNeural",
    },
    "US": {
        "name": "미국",
        "timezone": "America/New_York",
        "holidays": US_HOLIDAYS,
        "voice": "ko-KR-InJoonNeural",  # 한국어 목소리 유지
        "calendar": "XNYS",  # NYSE
    }
}

# -----------------------
# Utils
# -----------------------
def today(market="KR"):
    """오늘 날짜 (YYYY-MM-DD)"""
    tz = MARKET_CONFIG[market]["timezone"]
    return datetime.now(ZoneInfo(tz)).strftime("%Y-%m-%d")

def today_compact(market="KR"):
    """오늘 날짜 (YYYYMMDD)"""
    tz = MARKET_CONFIG[market]["timezone"]
    return datetime.now(ZoneInfo(tz)).strftime("%Y%m%d")

def is_holiday(market="KR"):
    """휴장일 확인"""
    config = MARKET_CONFIG[market]
    date_str = today(market)
    
    # 고정 휴일 체크
    if date_str in config["holidays"]:
        return True
    
    # US만 거래소 캘린더 체크
    if market == "US" and CALENDAR_AVAILABLE and "calendar" in config:
        try:
            cal = xcals.get_calendar(config["calendar"])
            return not cal.is_session(date_str)
        except Exception as e:
            print(f"⚠️  캘린더 확인 오류: {e}")
            return False
    
    return False

def is_market_closed(market="US"):
    """시장 종료 확인 (US만 사용)"""
    if market != "US":
        return True  # KR은 항상 종료된 것으로 간주
    
    tz = MARKET_CONFIG[market]["timezone"]
    now = datetime.now(ZoneInfo(tz))
    return now.hour >= 16  # 16:00 ET 이후

def log(market, msg):
    """타임스탬프와 함께 로그 출력"""
    tz = MARKET_CONFIG[market]["timezone"]
    timestamp = datetime.now(ZoneInfo(tz)).strftime("%H:%M:%S")
    print(f"[{market}][{timestamp}] {msg}")

# -----------------------
# Main
# -----------------------
def main(market="KR"):
    """자동 방송 메인 로직"""
    
    if market not in MARKET_CONFIG:
        print(f"❌ 지원하지 않는 마켓: {market}")
        print("   사용 가능: KR, US")
        return 1
    
    config = MARKET_CONFIG[market]
    log(market, f"DS-Anchor START | Market: {config['name']} | Date: {today(market)}")
    
    # 휴장일 체크
    if is_holiday(market):
        log(market, f"⏸️  오늘은 {config['name']} 시장 휴장일입니다. 스킵합니다.")
        return 0
    
    # US는 장 종료 확인
    if market == "US" and not is_market_closed(market):
        log(market, "⏸️  아직 장이 종료되지 않았습니다. 16:00 ET 이후 실행하세요.")
        return 0
    
    # 재시도 루프
    for attempt in range(1, MAX_RETRY + 1):
        log(market, f"🎬 시도 {attempt}/{MAX_RETRY}")
        
        try:
            # 1. 대본 생성
            log(market, "1️⃣ 대본 생성 중...")
            url = f"{API}/generate_ds_anchor_script?key={ACCESS_KEY}"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            script = response.json().get("script", "")
            
            if not script:
                raise ValueError("대본이 비어있습니다.")
            
            with open("script.txt", "w", encoding="utf-8") as f:
                f.write(script)
            log(market, f"   ✅ 대본 저장 완료 ({len(script)} 글자)")
            
            # 2. 음성 생성
            log(market, "2️⃣ 음성 생성 중...")
            subprocess.run([
                "edge-tts",
                "--voice", config["voice"],
                "--rate", "-5%",
                "--pitch", "-5Hz",
                "--file", "script.txt",
                "--write-media", "output/voice.mp3"
            ], check=True)
            log(market, "   ✅ 음성 생성 완료")
            
            # 3. 대시보드 캡처
            log(market, "3️⃣ 대시보드 캡처 중...")
            subprocess.run(["python", "capture_dashboard.py"], check=True)
            log(market, "   ✅ 대시보드 캡처 완료")
            
            # 4. 영상 합성
            log(market, "4️⃣ 영상 합성 중...")
            subprocess.run(["bash", "make_video.sh"], check=True)
            log(market, "   ✅ 영상 합성 완료")
            
            # 5. 유튜브 업로드
            log(market, "5️⃣ 유튜브 업로드 중...")
            video_path = f"output/ds_anchor_{today_compact(market)}.mp4"
            subprocess.run(["python", "upload_youtube.py", video_path], check=True)
            log(market, "   ✅ 유튜브 업로드 완료")
            
            # 성공
            log(market, f"🎉 {config['name']} 방송 완료!")
            return 0
            
        except Exception as e:
            log(market, f"❌ 오류 발생: {e}")
            
            if attempt < MAX_RETRY:
                log(market, f"⏳ {RETRY_WAIT}초 후 재시도합니다...")
                time.sleep(RETRY_WAIT)
            else:
                log(market, f"💥 최대 재시도 횟수({MAX_RETRY})를 초과했습니다.")
                return 1
    
    return 1

if __name__ == "__main__":
    # 커맨드라인 인수로 마켓 선택
    market = sys.argv[1].upper() if len(sys.argv) > 1 else "KR"
    sys.exit(main(market))
