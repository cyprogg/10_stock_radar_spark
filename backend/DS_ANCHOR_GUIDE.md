# DS-Anchor 자동 방송 시스템 가이드

## 📋 개요

Decision Stream의 시장 분석 결과를 자동으로 유튜브 영상으로 제작하여 업로드하는 완전 자동화 시스템입니다.

## 🎯 전체 흐름

```
1. 대본 생성 (API)
   ↓
2. 음성 합성 (edge-tts)
   ↓
3. 대시보드 캡처 (Playwright)
   ↓
4. 영상 합성 (FFmpeg)
   ↓
5. 유튜브 업로드 (YouTube API)
```

## 📦 사전 준비

### 1. Python 패키지 설치

```bash
cd backend
pip install -r requirements.txt

# Playwright 브라우저 설치
playwright install chromium
```

### 2. 시스템 패키지 설치

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install -y ffmpeg
```

#### macOS
```bash
brew install ffmpeg
```

#### Windows
```
FFmpeg 공식 사이트에서 다운로드: https://ffmpeg.org/download.html
```

### 3. 디렉토리 생성

```bash
mkdir -p output
```

## 🚀 사용법

### 기본 실행 (한국장)

```bash
cd backend
python ds_anchor_auto.py
```

또는

```bash
python ds_anchor_auto.py KR
```

### 미국장 실행

```bash
python ds_anchor_auto.py US
```

## 📂 프로젝트 구조

```
backend/
├── ds_anchor_auto.py         # 멀티 마켓 자동화 (메인)
├── ds_anchor_kr.py            # 한국장 전용
├── ds_anchor_us.py            # 미국장 전용
├── capture_dashboard.py       # 대시보드 스크린샷
├── make_video.sh              # 영상 합성 스크립트
├── upload_youtube.py          # 유튜브 업로드
└── output/                    # 생성 파일 저장
    ├── dashboard_YYYYMMDD.png
    ├── voice.mp3
    └── ds_anchor_YYYYMMDD.mp4
```

## 🛠️ 각 스크립트 설명

### 1. ds_anchor_auto.py (통합 자동화)

**특징:**
- KR/US 마켓 모두 지원
- 휴장일 자동 확인
- 재시도 로직 (최대 3회)

**설정:**
```python
MAX_RETRY = 3          # 최대 재시도 횟수
RETRY_WAIT = 60        # 재시도 간격 (초)
```

**한국 휴장일:**
- 2026-01-01 (신정)
- 2026-02-11 (설 예시)

**미국 휴장일:**
- 2026-01-01 (New Year's Day)
- 2026-07-04 (Independence Day)
- NYSE 캘린더 자동 확인 (exchange-calendars)

### 2. capture_dashboard.py (스크린샷)

**기능:**
- http://127.0.0.1:8125 접속
- 1920x1080 해상도 캡처
- output/dashboard_YYYYMMDD.png 저장

**실행:**
```bash
python capture_dashboard.py
```

### 3. make_video.sh (영상 합성)

**기능:**
- 대시보드 이미지 + 음성을 MP4로 합성
- H.264 코덱 (유튜브 호환)
- 음성 길이만큼 영상 생성

**실행:**
```bash
bash make_video.sh
```

### 4. upload_youtube.py (업로드)

**현재 상태:**
- 준비 완료 (실제 업로드는 수동)
- YouTube API 연동 필요

**향후 구현 필요:**
1. Google Cloud Console 설정
2. YouTube Data API v3 활성화
3. OAuth 2.0 클라이언트 ID 생성
4. `client_secrets.json` 파일 준비

## ⏰ 자동 실행 설정 (Cron)

### 한국장 (매일 오후 6시)

```bash
# crontab 편집
crontab -e

# 추가
0 18 * * * cd /path/to/backend && python ds_anchor_auto.py KR >> logs/kr.log 2>&1
```

### 미국장 (매일 오후 5시 ET = 한국시간 새벽 7시)

```bash
0 7 * * * cd /path/to/backend && python ds_anchor_auto.py US >> logs/us.log 2>&1
```

## 🔍 로그 확인

실행 중 로그는 실시간으로 출력됩니다:

```
[KR][18:00:01] DS-Anchor START | Market: 한국 | Date: 2026-01-26
[KR][18:00:01] 🎬 시도 1/3
[KR][18:00:02] 1️⃣ 대본 생성 중...
[KR][18:00:03]    ✅ 대본 저장 완료 (2456 글자)
[KR][18:00:04] 2️⃣ 음성 생성 중...
[KR][18:00:45]    ✅ 음성 생성 완료
[KR][18:00:46] 3️⃣ 대시보드 캡처 중...
[KR][18:00:49]    ✅ 대시보드 캡처 완료
[KR][18:00:50] 4️⃣ 영상 합성 중...
[KR][18:01:05]    ✅ 영상 합성 완료
[KR][18:01:06] 5️⃣ 유튜브 업로드 중...
[KR][18:01:07]    ✅ 유튜브 업로드 완료
[KR][18:01:08] 🎉 한국 방송 완료!
```

## 🚨 문제 해결

### 1. API 서버가 실행되지 않음

```bash
# 서버 실행 확인
curl http://127.0.0.1:8125/regime?key=ds-test-2026

# 서버 실행
cd backend
python server_v2.py
```

### 2. Playwright 오류

```bash
# 브라우저 재설치
playwright install chromium
```

### 3. FFmpeg 오류

```bash
# FFmpeg 설치 확인
ffmpeg -version

# 없으면 설치
# Ubuntu: sudo apt install ffmpeg
# macOS: brew install ffmpeg
```

### 4. edge-tts 오류

```bash
# 재설치
pip install --upgrade edge-tts

# 음성 목록 확인
edge-tts --list-voices | grep ko-KR
```

## 📊 생성 파일

### 1. script.txt
```
오늘의 시장 분석입니다.
현재 시장은 RISK_ON 상태이며...
(약 2000~3000자)
```

### 2. output/voice.mp3
- 한국어 음성 (InJoon 목소리)
- 속도: -5%
- 피치: -5Hz
- 길이: 약 3~5분

### 3. output/dashboard_YYYYMMDD.png
- 해상도: 1920x1080
- 형식: PNG
- 용량: 약 500KB~1MB

### 4. output/ds_anchor_YYYYMMDD.mp4
- 코덱: H.264
- 해상도: 1920x1080
- 오디오: AAC 192k
- 용량: 약 5~15MB

## 🎬 영상 메타데이터

### 제목 형식
```
2026년 01월 26일 📈 시장 분석 | Decision Stream
```

### 설명
```
2026년 01월 26일 Decision Stream 시장 분석

📊 오늘의 시장 분석
✅ 섹터 흐름 분석
🎯 주목 종목 리스트
⚠️ 투자 전략 가이드

🔔 구독과 좋아요는 큰 힘이 됩니다!

#주식 #투자 #시장분석 #DecisionStream
```

## 🔐 보안

### API 키
```python
ACCESS_KEY = "ds-test-2026"
```

**주의:** 프로덕션 환경에서는 `.env` 파일로 관리하세요.

```bash
# .env
API_URL=http://127.0.0.1:8125
ACCESS_KEY=your-secret-key
```

## 📈 성능

### 예상 소요 시간
- 대본 생성: 1~2초
- 음성 합성: 30~60초
- 대시보드 캡처: 3~5초
- 영상 합성: 10~30초
- 유튜브 업로드: 10~60초

**총 소요 시간: 약 1~3분**

## 🎯 확장 기능

### 1. 썸네일 자동 생성
```python
# 대시보드 스크린샷에 텍스트 오버레이
from PIL import Image, ImageDraw, ImageFont

def add_thumbnail_text(image_path):
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)
    # 텍스트 추가
    img.save("thumbnail.jpg")
```

### 2. 타임스탬프 자동 생성
```python
# 대본에서 섹션별 타임스탬프 추출
def generate_timestamps(script):
    timestamps = []
    # 섹션 감지 및 시간 계산
    return timestamps
```

### 3. 다국어 지원
```python
# 영어 음성 추가
VOICES = {
    "KR": "ko-KR-InJoonNeural",
    "US": "en-US-GuyNeural",  # 영어 목소리
}
```

## 📞 지원

문제가 발생하면:
1. 로그 확인
2. `output/` 디렉토리 확인
3. API 서버 상태 확인
4. 시스템 패키지 설치 확인

## 🎉 완성!

이제 Decision Stream의 시장 분석이 매일 자동으로 영상으로 만들어집니다! 🚀
