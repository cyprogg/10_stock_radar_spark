# 📊 Decision Stream - 중기 스윙 투자 시스템

## 프로젝트 개요
**Decision Stream**은 퇴직자 관점에서 설계된 중기 스윙 투자 지원 시스템입니다.

### 핵심 철학
- ❌ 단기 급등주 추격
- ✅ 중기 (1~3개월) 안정적 스윙
- ✅ 월 1~2회 매매
- ✅ 손절 -8%, 목표 +15~30%

---

## 🚀 새로운 기능: DS-Anchor 자동 방송 시스템

**매일 시장 분석을 자동으로 유튜브 영상으로 제작합니다!**

### 주요 기능
- ✅ 대본 자동 생성 (API)
- ✅ 음성 합성 (edge-tts)
- ✅ 대시보드 스크린샷
- ✅ 영상 합성 (FFmpeg)
- ✅ 유튜브 업로드 준비

### 빠른 시작
```bash
cd backend
bash setup_ds_anchor.sh      # 초기 설정
python test_ds_anchor.py      # 시스템 테스트
python ds_anchor_auto.py KR   # 한국장 실행
python ds_anchor_auto.py US   # 미국장 실행
```

📘 **상세 가이드**: [backend/DS_ANCHOR_GUIDE.md](backend/DS_ANCHOR_GUIDE.md)

---

## 🏗️ 시스템 구조

```
decision-stream/
├── index.html                      # Decision Stream 통합 대시보드
├── user_guide.html                 # 📚 사용 가이드
├── youtube_script_generator.html   # 🎬 유튜브 대본 생성기
├── news_filter.html                # 📰 뉴스 필터링 도구
├── chart_analysis.html             # 📊 기술적 분석 차트
├── trade_plan_simulation.html      # 매매 계획 시뮬레이션
├── algorithm_structure.html        # 🧠 알고리즘 구조 시각화
│
├── backend/
│   ├── server.py                   # FastAPI 메인 서버
│   ├── server_v2.py                # 개선된 API 서버 (권장)
│   ├── scheduler.py                # 주가 자동 업데이트
│   │
│   ├── ds_anchor_auto.py           # 🎬 멀티 마켓 자동 방송 (메인)
│   ├── ds_anchor_kr.py             # 한국장 전용
│   ├── ds_anchor_us.py             # 미국장 전용
│   ├── capture_dashboard.py        # 대시보드 스크린샷
│   ├── make_video.sh               # 영상 합성
│   ├── upload_youtube.py           # 유튜브 업로드
│   ├── test_ds_anchor.py           # 시스템 테스트
│   ├── setup_ds_anchor.sh          # 초기 설정 스크립트
│   │
│   ├── DS_ANCHOR_GUIDE.md          # 자동 방송 가이드
│   ├── .env                        # API 키 저장 (Git 제외)
│   ├── requirements.txt
│   └── services/
│       ├── korea_investment_api.py
│       ├── us_stock_service.py
│       └── technical_analysis_service.py
│
├── docs/
│   ├── ALGORITHM_DESIGN.md         # 알고리즘 설계 문서
│   ├── RISK_ON_ALGORITHM.md        # Risk-On 판정 알고리즘
│   ├── WATCH_CHECKLIST_DESIGN.md   # Watch & Checklist 설계
│   └── FOLLOWER_TO_LEADER_ALGORITHM.md  # Leader 승격 알고리즘
│
├── screener/
│   ├── main_monthly.py             # 월 1회 스크리너
│   └── data/
│       ├── raw/                    # 표준 CSV
│       ├── hts_raw/                # HTS 원본 CSV
│       └── output/                 # 스크리너 결과
│
├── tools/
│   ├── convert_hts_prices.py
│   └── convert_hts_flows.py
│
├── README.md                       # 📘 프로젝트 개요 (현재 문서)
├── QUICKSTART.md                   # 상세 실행 가이드
├── TRADE_PLAN_GUIDE.md
├── MARKET_ANALYSIS_GUIDE.md
└── STOCK_DATA_COLLECTION_GUIDE.md
```

---

## 🎯 주요 기능

### 1) 📊 Market Regime (시장 상태)
- **Risk-On / Risk-Off 판정**
- 3가지 기준 (Breadth / Volatility / Theme)
- 2개 이상 충족 시 Risk-On
- **핵심 메시지**: "사도 죽지 않을 확률이 높다"

### 2) 🔥 Sector Heatmap (섹터 분석)
- 자금 흐름 실시간 추적
- **SURGE**: 자금 집중 (70점 이상)
- **NORMAL**: 일반 상태
- 섹터별 Duration (지속 기간) 표시

### 3) 🎯 Stock Funnel (종목 분류)
- **Leader**: 섹터 선도주 (자금 집중)
- **Follower**: 미래 Leader 후보 (매집 기회)
- **No-Go**: 구조적 리스크 (회피)

### 4) ✅ Watch & Checklist
- **"사면 안 되는 이유" 체크**
- 5가지 Safety Checklist
- Strong / Medium / Weak 판정

### 5) 🧠 Market Intelligence
- 전문가급 자동 시장 해설
- 자금 흐름 맵 분석
- 실전 투자 전략 제시

### 6) 🎬 유튜브 대본 자동 생성
- 버튼 한 번으로 대본 생성
- 제목 / 썸네일 / 대본 / 타임스탬프 / 해시태그
- 10분 분량 전문가급 콘텐츠

### 7) 📰 뉴스 필터링
- 중기 스윙 관점 뉴스 해석
- 5문장 체크리스트
- 단기 소음 vs 중기 가치 구분

### 8) 📊 Trade Plan Simulation
- 안전한 시뮬레이션 환경
- 7요소 체크리스트
- 자동 포지션 계산
- 성과 추적

---

## 🚀 빠른 시작

### 1. API 서버 실행

```bash
cd backend

# 패키지 설치
pip install -r requirements.txt

# 서버 실행 (개선 버전 권장)
python server_v2.py
```

서버 주소: `http://127.0.0.1:8125`

### 2. 대시보드 접속

브라우저에서 `index.html` 열기:
- Market Regime
- Sector Heatmap
- Stock Funnel
- Market Intelligence

### 3. DS-Anchor 자동 방송 (선택)

```bash
cd backend

# 초기 설정
bash setup_ds_anchor.sh

# 시스템 테스트
python test_ds_anchor.py

# 실행
python ds_anchor_auto.py KR    # 한국장
python ds_anchor_auto.py US    # 미국장
```

### 4. Cron 자동 실행 (선택)

```bash
# crontab 편집
crontab -e

# 한국장: 매일 오후 6시
0 18 * * * cd /path/to/backend && python ds_anchor_auto.py KR >> logs/kr.log 2>&1

# 미국장: 매일 새벽 7시 (ET 오후 5시)
0 7 * * * cd /path/to/backend && python ds_anchor_auto.py US >> logs/us.log 2>&1
```

---

## 📊 알고리즘 구조

Decision Stream은 4단계 의사결정 흐름을 따릅니다:

```
1. Market Regime
   ↓ (시장 진입 가능 여부)
2. Sector Heatmap
   ↓ (자금이 어디로 가는가)
3. Stock Funnel
   ↓ (어떤 종목이 후보인가)
4. Watch & Checklist
   ↓ (지금 행동해도 되는가)
5. Action (Buy / Watch / Skip)
```

### 핵심 알고리즘

1. **Risk-On 판정**: Breadth + Volatility + Theme (2/3 이상)
2. **Sector Scoring**: Flow(30%) + Structure(25%) + Narrative(25%) - Risk(20%)
3. **Follower → Leader 승격**: Sector Gate + Structure + Flow + Checklist + Confirm
4. **Checklist**: 5가지 Safety 체크 (사면 안 되는 이유)

📘 **상세 문서**:
- [ALGORITHM_DESIGN.md](ALGORITHM_DESIGN.md)
- [RISK_ON_ALGORITHM.md](RISK_ON_ALGORITHM.md)
- [WATCH_CHECKLIST_DESIGN.md](WATCH_CHECKLIST_DESIGN.md)
- [FOLLOWER_TO_LEADER_ALGORITHM.md](FOLLOWER_TO_LEADER_ALGORITHM.md)

---

## 🎬 DS-Anchor 자동 방송

### 전체 흐름

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

### 생성 파일

```
backend/output/
├── dashboard_20260126.png      # 대시보드 스크린샷
├── voice.mp3                   # 음성 파일
└── ds_anchor_20260126.mp4      # 최종 영상
```

### 예상 소요 시간

- 대본 생성: 1~2초
- 음성 합성: 30~60초
- 스크린샷: 3~5초
- 영상 합성: 10~30초
- **총 소요 시간: 약 1~3분**

📘 **상세 가이드**: [backend/DS_ANCHOR_GUIDE.md](backend/DS_ANCHOR_GUIDE.md)

---

## 📝 주요 문서

| 문서 | 설명 |
|------|------|
| [README.md](README.md) | 프로젝트 개요 (현재 문서) |
| [QUICKSTART.md](QUICKSTART.md) | 상세 실행 가이드 |
| [TRADE_PLAN_GUIDE.md](TRADE_PLAN_GUIDE.md) | 매매 계획 트레이닝 |
| [MARKET_ANALYSIS_GUIDE.md](MARKET_ANALYSIS_GUIDE.md) | 시장 분석 해석 |
| [ALGORITHM_DESIGN.md](ALGORITHM_DESIGN.md) | 알고리즘 설계 |
| [RISK_ON_ALGORITHM.md](RISK_ON_ALGORITHM.md) | Risk-On 판정 |
| [WATCH_CHECKLIST_DESIGN.md](WATCH_CHECKLIST_DESIGN.md) | Checklist 설계 |
| [FOLLOWER_TO_LEADER_ALGORITHM.md](FOLLOWER_TO_LEADER_ALGORITHM.md) | Leader 승격 |
| [backend/DS_ANCHOR_GUIDE.md](backend/DS_ANCHOR_GUIDE.md) | 자동 방송 가이드 |

---

## 🛠️ 기술 스택

### Frontend
- HTML5 / CSS3 / JavaScript
- Chart.js (차트 시각화)
- Font Awesome (아이콘)

### Backend
- **FastAPI** (API 서버)
- Python 3.9+
- Uvicorn (ASGI 서버)

### DS-Anchor 자동화
- **Playwright** (대시보드 캡처)
- **edge-tts** (음성 합성)
- **FFmpeg** (영상 합성)
- **YouTube Data API v3** (업로드)

### 데이터
- yfinance (미국 주식)
- 한국투자증권 API (한국 주식)
- RESTful Table API (데이터 저장)

---

## 📈 시스템 특징

### ✅ 장점
1. **중기 스윙 특화**: 퇴직자 맞춤 전략
2. **자금 흐름 추적**: 돈이 어디로 가는지 직접 표시
3. **자동화**: 매일 대본 → 음성 → 영상 자동 생성
4. **통계 기반**: 감정 아닌 데이터 중심
5. **교육 콘텐츠**: 왜 이 종목인지 설명

### ⚠️ 현재 상태
- ✅ Mock 데이터로 전체 시스템 구현 완료
- ✅ 알고리즘 문서화 완료
- ✅ DS-Anchor 자동 방송 시스템 완성
- 🔄 실제 증권사 API 연동 대기
- 🔄 실시간 주가 데이터 연동 대기
- 🔄 YouTube API 연동 대기

---

## 🎯 로드맵

### Phase 1: 기반 시스템 (완료 ✅)
- [x] Market Regime 알고리즘
- [x] Sector Heatmap
- [x] Stock Funnel
- [x] Watch & Checklist
- [x] Market Intelligence
- [x] 유튜브 대본 생성
- [x] 뉴스 필터링
- [x] DS-Anchor 자동 방송

### Phase 2: 데이터 연동 (진행 중 🔄)
- [ ] 한국투자증권 API 연동
- [ ] yfinance 실시간 데이터
- [ ] 거래량/순매수 데이터 수집
- [ ] 뉴스 크롤링

### Phase 3: 고도화 (대기 ⏳)
- [ ] YouTube API 자동 업로드
- [ ] 실시간 알림 시스템
- [ ] 모바일 앱 (PWA)
- [ ] 백테스팅 시스템

---

## 👥 사용자 가이드

### 초보자
1. `index.html` 열기
2. Market Regime 확인
3. SURGE 섹터 찾기
4. Follower 종목 관찰
5. `user_guide.html`에서 자세한 가이드 확인

### 중급자
1. `news_filter.html`로 뉴스 분석
2. `chart_analysis.html`로 기술적 분석
3. `trade_plan_simulation.html`로 연습
4. Watch & Checklist 활용

### 고급자
1. DS-Anchor 자동 방송 설정
2. Cron으로 자동 실행
3. 알고리즘 문서 읽고 커스터마이징
4. API 서버 개선

---

## 🔐 보안 및 주의사항

### API 키 관리
```bash
# .env 파일 생성
cd backend
cp .env.example .env

# 본인의 API 키 입력
KIS_APP_KEY=your_app_key
KIS_APP_SECRET=your_app_secret
```

### 투자 주의사항
⚠️ **이 시스템은 투자 참고 도구이며, 투자 판단은 본인의 책임입니다.**

- 손절 규칙을 반드시 지키세요 (-8%)
- 포지션 크기를 관리하세요 (총 자산의 20~30%)
- 모의 투자로 충분히 연습하세요

---

## 📞 문제 해결

### API 서버가 실행되지 않음
```bash
cd backend
python server_v2.py
```

### 대시보드가 비어있음
- API 서버 실행 확인
- 브라우저 콘솔 (F12) 확인
- Mock 데이터 모드 확인

### DS-Anchor 오류
```bash
cd backend
python test_ds_anchor.py
```

### FFmpeg 설치
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg
```

---

## 🎉 완성!

**Decision Stream**은 중기 스윙 투자를 위한 완전한 시스템입니다.

### 핵심 메시지
- 🎯 **시장이 말하는 것을 들으세요**
- 📊 **자금 흐름을 따라가세요**
- 🛡️ **"사면 안 되는 이유"를 체크하세요**
- 🎬 **매일 자동으로 콘텐츠가 생성됩니다**

---

## 📧 연락처

문제가 있거나 개선 제안이 있으시면 이슈를 등록해주세요.

**Happy Trading! 📈**
