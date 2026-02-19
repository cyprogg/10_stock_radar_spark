# 📊 Decision Stream - AI 기반 중기 스윙 투자 시스템

## 프로젝트 개요
**Decision Stream**은 퇴직자 관점에서 설계된 중기 스윙 투자 지원 시스템입니다.

### 핵심 철학
> **"주가는 가치가 아니라 돈이 움직이는 방향으로 간다"**

- ❌ 단기 급등주 추격
- ✅ 중기 (1~3개월) 안정적 스윙
- ✅ 월 1~2회 매매
- ✅ 손절 -8%, 목표 +15~30%
- ⭐ **9요소 통합 프레임워크** (자금 흐름, 사이클, 질, 지배구조, 서사, 리스크, 시간, 가치, 모멘텀)
- 🤖 **5개 AI Agent** (설명 가능한 자동화)

---

## 🚀 핵심 기능

### 1️⃣ AI Agent 시스템 (설명 가능한 자동화)
**5개 전문 Agent가 협력하여 투자 의사결정을 지원합니다:**

| Agent | 역할 | 출력 |
|-------|------|------|
| 🌍 **Market Regime Analyst** | 오늘 장이 어떤 장인지 판단 | RISK_ON / RISK_OFF |
| 🔍 **Sector Scout** | 섹터별 자금 흐름 랭킹 | SURGE 섹터 Top 10 |
| 🎯 **Stock Screener** | 종목 분류 (Leader/Follower/No-Go) | 9요소 점수 + 모멘텀 품질 |
| 📋 **Trade Plan Builder** | 매매 계획 자동 생성 | 진입/손절/목표/포지션 |
| 😈 **Devil's Advocate** | 반대 의견 자동 제시 | 왜 틀릴 수 있는지 |

**핵심 원칙:**
- 모든 판단에는 **근거**가 있다
- 모든 근거에는 **반대 의견**이 있다
- 모든 점수는 **0~100**으로 통일
- 모든 데이터에는 **출처**가 있다

📘 **상세 설계**: [AI_AGENT_ARCHITECTURE.md](AI_AGENT_ARCHITECTURE.md)

---

### 1.5️⃣ Seamless Trade Plan 통합 🆕
**간단한 미리보기 → 상세 시뮬레이션으로 매끄럽게 연결됩니다:**

**Step 1: 메인 대시보드 (index.html)**
- 종목 선택 → 간단한 Trade Plan 미리보기
- 투자기간 (단기/중기) & 리스크 성향 (보수/중립/공격) 선택
- 실시간 업데이트: 선택 변경 시 즉시 반영

**Step 2: 상세 시뮬레이션 (trade_plan_simulation.html)**
- "📊 상세 시뮬레이션 열기" 버튼 클릭
- **자동으로 전달되는 정보:**
  - 선택한 종목 (섹터, 티커, 종목명, 현재가)
  - 투자 설정 (기간, 리스크 성향)
  - 시장 구분 (KR/US 자동 판단)
- **데이터 재입력 불필요** → 사용자는 전략 세부 조정에만 집중
- 시뮬레이션 완료 후 "← 메인으로 돌아가기" 버튼으로 복귀

**설계 철학:**
- ✅ 마찰 없는 사용자 경험 (Frictionless UX)
- ✅ 단계적 의사결정 지원 (Progressive Disclosure)
- ✅ 데이터 일관성 유지 (Single Source of Truth)
- ✅ 학습 흐름 최적화 (Simulation Training)

**💡 두 체크리스트의 차이점:**
- **index.html (5개)**: Safety Checklist - "사면 안 되는 이유가 있는가?" (빠른 스크리닝)
- **simulation.html (7개)**: 7요소 체크리스트 - "이 전략이 타당한가?" (전략 검증)

📘 **상세 비교**: [CHECKLIST_COMPARISON.md](CHECKLIST_COMPARISON.md) - 두 체크리스트의 역할과 차이

---

### 1.6️⃣ Why Drawer + Devil's Advocate 🆕
**점수 클릭 → 근거와 반대의견 즉시 확인:**

**Why Drawer (점수 투명성)**
- 종목 선택 후 4개 점수 카드 표시 (자금 흐름, 가격 구조, 서사, 리스크)
- 점수 클릭 → 모달 팝업
- **3가지 지지 근거** + 출처 링크 + 기여도
- **2가지 반대 의견** (Devil's Advocate)
- **신뢰도 자동 계산** (반대의견 심각도 반영)

**Devil's Advocate (비판적 사고)**
- "모든 점수에는 반대 의견이 존재한다"
- 확증 편향 방지 → 양면 검토
- 자동 생성 로직: 각 점수 유형별 2가지 카운터
- 심각도 등급: Low / Medium / High

**핵심 가치:**
- ✅ 투명성: 모든 점수는 설명 가능
- ✅ 균형성: 긍정 + 부정 병렬 표시
- ✅ 신뢰성: 출처 + 신뢰도 표시
- ✅ 의사결정 품질: 양면 검토 후 판단

📘 **상세 가이드**:
- [WHY_DRAWER_DESIGN.md](WHY_DRAWER_DESIGN.md) - 설계 문서
- [WHY_DRAWER_COMPLETE.md](WHY_DRAWER_COMPLETE.md) - 구현 완료 보고서

---

### 2️⃣ 9요소 통합 프레임워크
**밸류에이션과 모멘텀을 넘어, 입체적 시장 분석:**

1. ⭐ **자금 흐름** (최우선) - 기관/외국인 순매수, 거래대금 증가
2. 🔄 **사이클** - 경기/산업/정책 사이클 위치
3. 💎 **기업의 질** - 부채 구조, 현금흐름, 원가 전가력
4. 👔 **지배구조** - 자사주 매입, 주주환원, 대주주 지분
5. 📖 **서사** - 미래 가능성, 시장 이해도, 글로벌 담론
6. ⚠️ **하방 리스크** - 최악의 경우 얼마나 잃을 수 있나
7. ⏰ **시간 적합성** - 기업 시간표와 내 투자 기간 정합성
8. 💰 **가치** - PER, PBR 등 전통적 밸류에이션 (기본)
9. 🚀 **모멘텀 품질** - **진짜 vs 가짜 모멘텀 구분**

> **"혼자 오르는 종목은 위험, 같이 오르는 종목은 돈 냄새"**

📘 **상세 가이드**:
- [INVESTMENT_FRAMEWORK_9_FACTORS.md](INVESTMENT_FRAMEWORK_9_FACTORS.md) - 투자 철학
- [ALGORITHM_9_FACTORS_INTEGRATION.md](ALGORITHM_9_FACTORS_INTEGRATION.md) - 기술 구현
- [MOMENTUM_QUALITY_FRAMEWORK.md](MOMENTUM_QUALITY_FRAMEWORK.md) - 모멘텀 품질
- [TRADING_CHECKLIST_SHORT_MID_TERM.md](TRADING_CHECKLIST_SHORT_MID_TERM.md) - 매매 체크리스트

---

### 3️⃣ No-Go 시스템 (시스템 신뢰도 향상)
**핵심 6개 규칙으로 위험 종목 자동 회피:**

1. 🔥 단일 기사 급등 + 거래대금 폭증
2. 📉 갭 상승 후 장대 음봉
3. 📈 테마 내 5번째 이후 급등주
4. 🏃 개인 순매수 80%↑ + 기관 이탈
5. ⚠️ 핵심 이평(20/60) 동시 이탈
6. ❌ 손절선 설정 불가

**→ 하나라도 해당 시 No-Go 자동 이동**

---

### 4️⃣ DS-Anchor 자동 방송 시스템
**매일 시장 분석을 자동으로 유튜브 영상으로 제작합니다!**

- ✅ 대본 자동 생성 (API)
- ✅ 음성 합성 (edge-tts)
- ✅ 대시보드 스크린샷
- ✅ 영상 합성 (FFmpeg)
- ✅ 유튜브 업로드 준비

**빠른 시작:**
```bash
cd backend
bash setup_ds_anchor.sh      # 초기 설정
python test_ds_anchor.py      # 시스템 테스트
python ds_anchor_auto.py KR   # 한국장 실행
python ds_anchor_auto.py US   # 미국장 실행
```

📘 **상세 가이드**: [backend/DS_ANCHOR_GUIDE.md](backend/DS_ANCHOR_GUIDE.md)

---

### 5️⃣ 월 9,900원 현실형 운영
**무료 데이터만으로 충분합니다!**

**한국 시장:**
- ✅ Yahoo Finance (실시간 종가, .KS suffix) - 무료 15분 지연
- ✅ KRX 투자자별 매매동향 (외국인/기관/개인) - 무료
- ✅ 뉴스 필터 ([news_filter.html](news_filter.html)) - 소음/가치 자동 분류 완성
- OpenDART API (공시, 실적) - 무료
- 네이버 금융 뉴스 (크롤링) - 무료

**미국 시장:**
- ✅ Yahoo Finance (실시간 종가, 거래량) - 무료 15분 지연
- Alpha Vantage Free (재무제표) - 무료
- FRED API (금리, VIX) - 무료

**비용 분석:**
- 데이터 비용: ₩0
- 서버 비용: ₩6,500/월 (Railway Hobby)
- 구독료: ₩9,900/월
- **순이익: ₩3,400/월**

📘 **상세 분석**: [DATA_COST_ANALYSIS.md](DATA_COST_ANALYSIS.md)

---

## 🏗️ 시스템 구조

```
decision-stream/
├── index.html                    # 메인 대시보드 (간단한 Trade Plan 미리보기)
├── trade_plan_simulation.html    # 🆕 상세 시뮬레이션 (seamless 통합)
├── backend/
│   ├── server.py                # FastAPI 서버
│   ├── server_v2.py             # 간소화 버전
│   ├── scheduler.py             # 데이터 수집 스케줄러
│   ├── services/
│   │   ├── nh_investment_api.py       # NH투자증권 API
│   │   ├── us_stock_service.py        # 미국 주식 서비스
│   │   └── technical_analysis_service.py  # 기술적 분석
│   ├── agents/                  # ⭐ AI Agent 시스템
│   │   ├── market_regime.py    # Agent 1: Market Regime Analyst
│   │   ├── sector_scout.py     # Agent 2: Sector Scout
│   │   ├── stock_screener.py   # Agent 3: Stock Screener
│   │   ├── trade_plan_builder.py  # Agent 4: Trade Plan Builder
│   │   └── devils_advocate.py  # Agent 5: Devil's Advocate
│   ├── scoring/                 # 점수 엔진 (0~100 통일)
│   │   ├── flow_score.py       # 자금 흐름 점수
│   │   ├── structure_score.py  # 가격 구조 점수
│   │   ├── narrative_score.py  # 서사 점수
│   │   ├── risk_score.py       # 리스크 점수
│   │   └── momentum_quality.py # 모멘텀 품질 (진짜 vs 가짜)
│   ├── nogo/                    # No-Go 시스템
│   │   ├── nogo_rules.py       # 핵심 6개 규칙
│   │   ├── momentum_validator.py  # 모멘텀 진위 판별
│   │   └── theme_tracker.py    # 테마 피로도 추적
│   ├── data/                    # 데이터 수집 (무료 소스)
│   │   ├── krx_collector.py    # KRX 투자자별 매매
│   │   ├── dart_collector.py   # OpenDART 공시
│   │   ├── yahoo_collector.py  # Yahoo Finance EOD
│   │   └── cache_manager.py    # Redis 캐싱
│   ├── ds_anchor_auto.py        # DS-Anchor 자동 실행
│   ├── ds_anchor_kr.py          # 한국 시장 앵커
│   ├── ds_anchor_us.py          # 미국 시장 앵커
│   └── ...
├── docs/                         # 문서 (50+ 파일)
│   ├── ALGORITHM_DESIGN.md       # 알고리즘 설계
│   ├── INVESTMENT_FRAMEWORK_9_FACTORS.md  # ⭐ 9요소 철학
│   ├── ALGORITHM_9_FACTORS_INTEGRATION.md # ⭐ 9요소 통합
│   ├── MOMENTUM_QUALITY_FRAMEWORK.md      # ⭐ 모멘텀 품질
│   ├── TRADING_CHECKLIST_SHORT_MID_TERM.md # ⭐ 매매 체크리스트
│   ├── AI_AGENT_ARCHITECTURE.md           # ⭐ AI Agent 설계
│   ├── MVP_ROADMAP.md                     # ⭐ MVP 4주 로드맵
│   ├── DATA_COST_ANALYSIS.md              # ⭐ 데이터 비용 분석
│   └── ...
├── requirements.txt              # Python 의존성
└── Procfile                      # Railway 배포
```

---

## 🎯 핵심 특징

### Decision Stream Engine (3단계 흐름)
```
Level 1: Market Regime
    ↓
    Risk-On / Risk-Off 판단
    ↓
Level 2: Sector Heatmap
    ↓
    SURGE 섹터 자동 선별
    ↓
Level 3: Stock Funnel
    ↓
    Leader / Follower / No-Go 분류
    ↓
Level 4: Watch & Checklist
    ↓
    9요소 체크 + Devil's Advocate
    ↓
Level 5: Trade Plan (간단 미리보기)
    ↓
    진입/손절/목표/포지션 자동 생성
    ↓
    📊 상세 시뮬레이션 (trade_plan_simulation.html)
    ↓
    시뮬레이션 학습 + 차트 연동
```

### 핵심 메시지 (10가지)
1. 자금 흐름 읽기 (⭐ 최우선)
2. 사이클 이해
3. 질이 속도 결정
4. 지배구조가 수익의 절반
5. 서사가 없으면 리레이팅 없음
6. 하방 체크
7. 시간표 일치
8. 가치는 기본
9. **혼자 오르면 위험, 같이 오르면 돈 냄새**
10. 계좌를 지키며 반복

---

## 🚀 빠른 시작

### 1) 로컬 실행 (개발 모드)

**백엔드 서버 시작:**
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn server_v2:app --reload --host 0.0.0.0 --port 8126
```

**프론트엔드 접속:**
- 브라우저에서 `http://127.0.0.1:8126/` 열기
- 또는 `index.html` 직접 열기 (file://)

### 2) 실제 데이터 확인
```bash
# Market Regime API
curl "http://127.0.0.1:8126/api/agent/market-regime?key=ds-test-2026"

# Sector Heatmap
curl "http://127.0.0.1:8126/api/agent/sectors?key=ds-test-2026"

# 주가 차트 (한화에어로스페이스)
curl "http://127.0.0.1:8126/api/chart/012450"

# 주가 차트 (NVIDIA)
curl "http://127.0.0.1:8126/api/chart/NVDA"
```

### 3) DS-Anchor 자동 방송 (선택)
```bash
cd backend
bash setup_ds_anchor.sh
python test_ds_anchor.py
python ds_anchor_auto.py KR
```

### 4) 배포 (Railway + Vercel)
상세 가이드: [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)

---

## 📚 문서

### 핵심 문서
- [AI_AGENT_ARCHITECTURE.md](AI_AGENT_ARCHITECTURE.md) - 5개 AI Agent 설계 ✅
- [MVP_ROADMAP.md](MVP_ROADMAP.md) - 4주 개발 로드맵 ✅
- [DATA_COST_ANALYSIS.md](DATA_COST_ANALYSIS.md) - 월 9,900원 운영 가능성 ✅
- [SAAS_PRODUCTION_ROADMAP.md](SAAS_PRODUCTION_ROADMAP.md) - 🆕 SaaS 상용화 로드맵 (3개월)
- [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - 배포 체크리스트
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - 배포 가이드

### 투자 프레임워크
- [INVESTMENT_FRAMEWORK_9_FACTORS.md](INVESTMENT_FRAMEWORK_9_FACTORS.md)
- [ALGORITHM_9_FACTORS_INTEGRATION.md](ALGORITHM_9_FACTORS_INTEGRATION.md)
- [MOMENTUM_QUALITY_FRAMEWORK.md](MOMENTUM_QUALITY_FRAMEWORK.md)
- [TRADING_CHECKLIST_SHORT_MID_TERM.md](TRADING_CHECKLIST_SHORT_MID_TERM.md)

### 알고리즘 설계
- [ALGORITHM_DESIGN.md](ALGORITHM_DESIGN.md)
- [RISK_ON_ALGORITHM.md](RISK_ON_ALGORITHM.md)
- [WATCH_CHECKLIST_DESIGN.md](WATCH_CHECKLIST_DESIGN.md)
- [FOLLOWER_TO_LEADER_ALGORITHM.md](FOLLOWER_TO_LEADER_ALGORITHM.md)

### DS-Anchor
- [backend/DS_ANCHOR_GUIDE.md](backend/DS_ANCHOR_GUIDE.md)
- [DS_ANCHOR_UPDATE.md](DS_ANCHOR_UPDATE.md)
- [DS_ANCHOR_COMPLETION.md](DS_ANCHOR_COMPLETION.md)

---

## 💡 사용 방법

### 1단계: 투자 설정 (2개만)
```
투자 기간: 단기 (1~2주) / 중기 (1~3개월)
리스크 성향: 보수 / 중립 / 공격
```

### 2단계: 시장 확인
```
Market Regime → Risk-On / Risk-Off
```

### 3단계: 섹터 선택
```
Sector Heatmap → SURGE 섹터 클릭
```

### 4단계: 종목 선택
```
Stock Funnel → Leader / Follower 클릭
```

### 5단계: 체크리스트 확인
```
Watch & Checklist → 9요소 점수 + Devil's Advocate
```

### 6단계: 매매 계획
```
Trade Plan Builder → 진입/손절/목표/포지션 확인
```

### 7단계: 확정
```
"확정" 버튼 클릭
```

---

## 🎯 개발 로드맵

### MVP (4주)
- [x] 9요소 통합 프레임워크
- [x] 모멘텀 품질 판별
- [x] No-Go 시스템 설계
- [x] DS-Anchor 자동 방송
- [ ] 5개 AI Agent 구현
- [ ] 데이터 파이프라인 구축
- [ ] API 서버 완성
- [ ] UI 통합

### V2 (차별화)
- [ ] 조건 알림 (Slack/Email)
- [ ] 성과 기록 추적
- [ ] 실시간 미국 데이터
- [ ] 포트폴리오 리밸런싱

---

## 📊 현재 상태 (2026-02-19)

**완료 ✅:**
- ✅ 9요소 투자 프레임워크 (문서 + 구현)
- ✅ 5개 AI Agent 시스템 (완전 작동)
- ✅ MVP 로드맵 (4주) - **완료**
- ✅ 데이터 비용 분석 (₩9,900 가능성)
- ✅ DS-Anchor 자동 방송 (KR/US)
- ✅ 모멘텀 품질 프레임워크
- ✅ 단기/중기 매매 체크리스트
- ✅ No-Go 시스템 설계
- ✅ **Yahoo Finance 실시간 데이터 통합** (한국/미국)
- ✅ **Mock → 실제 데이터 전환 완료**
- ✅ **주가 자동 업데이트 시스템**
- ✅ **GitHub 저장소 생성 및 배포 준비**
- ✅ **SaaS 상용화 로드맵 작성**

**완성된 UI 페이지 ✅:**
- ✅ [index.html](index.html) - 메인 대시보드 (Market Regime, Sectors, Stock Funnel)
- ✅ [trade_plan_simulation.html](trade_plan_simulation.html) - 트레이드 플랜 시뮬레이션
- ✅ [news_filter.html](news_filter.html) - 뉴스 소음/가치 필터링 (5개 체크리스트, 0~100점)
- ✅ [user_guide.html](user_guide.html) - 사용자 가이드

**운영 중 🚀:**
- 🚀 Market Regime AI 분석 (실시간)
- 🚀 Sector Heatmap (5개 섹터 자동 랭킹)
- 🚀 Stock Funnel (Leader/Follower/No-Go 자동 분류)
- 🚀 Market Intelligence (AI 시장 해설 생성)
- 🚀 주가 데이터 (Yahoo Finance, 자동 업데이트)

**다음 단계 📅:**
- 📅 Railway + Vercel 배포
- 📅 Supabase Auth (회원가입/로그인)
- 📅 Stripe 결제 시스템
- 📅 Beta 테스트 (50명)
- 📅 정식 런칭

---

## 📝 최근 업데이트

### v5.0 (2026-02-19) 🆕 **실제 데이터 전환 완료**
**주요 개선사항:**

1. **Yahoo Finance 실시간 데이터 통합**
   - 한국 주식: .KS suffix (005930.KS)
   - 미국 주식: 직접 티커 (AAPL, NVDA)
   - 15분 지연 데이터 (무료)
   - 자동 통화 감지 (KRW/USD)

2. **Mock → AI Agent 실제 데이터 전환**
   - Market Regime: `/api/agent/market-regime` (AI 분석)
   - Sector Heatmap: `/api/agent/sectors` (5개 섹터 실시간 랭킹)
   - Stock Funnel: `/api/agent/funnel` (Leader/Follower 자동 분류)
   - Market Intelligence: `/api/agent/market-intelligence` (AI 해설)

3. **주가 자동 업데이트 시스템**
   - 페이지 로드시 자동 업데이트 (12개 종목)
   - Yahoo Finance `/api/chart/{ticker}` 호출
   - 실패 시 캐시된 가격 사용 (Graceful degradation)
   - Console 로그: "✅ Updated 12/12 stock prices"

4. **GitHub 저장소 생성**
   - Repository: https://github.com/cyprogg/10_stock_radar_spark
   - 174개 파일 업로드 완료
   - 배포 준비 완료 (Railway + Vercel)

5. **SaaS 상용화 준비**
   - [SAAS_PRODUCTION_ROADMAP.md](SAAS_PRODUCTION_ROADMAP.md) 작성
   - 7단계 로드맵 (3개월)
   - 예상 수익: ₩2,440,000/월
   - 초기 비용: $10-30/월

**기술 변경사항:**
- ✅ `USE_MOCK_DATA = false` (실제 API 사용)
- ✅ API 포트 변경: 8125 → 8126
- ✅ `/regime` → `/api/agent/market-regime`
- ✅ `/sectors` → `/api/agent/sectors`
- ✅ `/funnel` → `/api/agent/funnel`
- ✅ `/market_intelligence` → `/api/agent/market-intelligence`
- ✅ 무한 재귀 방지 (fetchJSON fallback)
- ✅ file:// 프로토콜 지원

**테스트 완료:**
- ✅ 한화에어로스페이스: 1,149,000원 (Yahoo Finance)
- ✅ 삼성바이오로직스: 1,720,000원 (Yahoo Finance)
- ✅ LMT: $649.81 (Yahoo Finance)
- ✅ NVIDIA: $187.98 (Yahoo Finance)
- ✅ 삼성전자: 190,000원 (Yahoo Finance)
- ✅ Market Regime: RISK_ON (AI 분석)
- ✅ Sectors: 5개 섹터 랭킹 (AI 분석)

**배포 준비:**
- ✅ GitHub 저장소 생성
- ✅ DEPLOYMENT_CHECKLIST.md 완성
- ⏳ Railway 배포 대기
- ⏳ Vercel 배포 대기

---

### v4.0 (2026-01-27)
**주요 개선사항:**

1. **UI 헤더 변경**
   - 제목: "📊 Decision Stream v4.0" 표시
   - 오른쪽 상단 β v1.0 pill 제거 (클린한 UI)

2. **JavaScript 구문 오류 수정**
   - 문제: `DOMContentLoaded` 이벤트 리스너 내부 잘못된 객체 리터럴
   - 증상: "Unexpected token ':'" 에러, 데이터 로딩 실패
   - 해결: 이벤트 리스너를 정상 코드로 수정 (`change` 이벤트 연결)
   - 결과: 모든 데이터 정상 로딩 ✅

3. **Why Drawer + Devil's Advocate 통합 완료**
   - 4개 점수 클릭 시 근거/반대의견 모달 표시
   - 3가지 지지 근거 + 출처 링크 + 기여도
   - 2가지 자동 생성 반대 의견 (심각도별)
   - 신뢰도 자동 계산 (반대의견 반영)

4. **Trade Plan Seamless Integration**
   - index.html → trade_plan_simulation.html 완벽 연동
   - 9개 URL 파라미터 자동 전달
   - 데이터 재입력 불필요
   - "← 메인으로 돌아가기" 버튼 추가

**문서 업데이트:**
- ✅ [SYNTAX_ERROR_FIX.md](SYNTAX_ERROR_FIX.md) - 구문 오류 수정 보고서
- ✅ [WHY_DRAWER_COMPLETE.md](WHY_DRAWER_COMPLETE.md) - Why Drawer 구현 완료
- ✅ [TRADE_PLAN_INTEGRATION.md](TRADE_PLAN_INTEGRATION.md) - Trade Plan 통합 가이드
- ✅ [CHECKLIST_COMPARISON.md](CHECKLIST_COMPARISON.md) - 두 체크리스트 비교

**테스트 완료:**
- ✅ Playwright Console Capture - 구문 오류 없음
- ✅ 데이터 로딩: Regime, Sectors, Funnel 정상
- ✅ Why Drawer 모달 동작 확인
- ✅ Trade Plan 실시간 업데이트 정상

---

## 🔗 관련 링크

- **프로젝트**: [GitHub Repository](https://github.com/cyprogg/10_stock_radar_spark)
- **문서**: [전체 문서 목록](./) (50+ 파일)
- **배포**: Railway (백엔드) + Vercel (프론트엔드) 준비 완료
- **데이터**: Yahoo Finance (무료 15분 지연)
- **API**: FastAPI (port 8126)

---

## 📞 Contact

프로젝트에 대한 문의나 피드백은 이슈를 통해 남겨주세요.

---

## ⚖️ License

MIT License

---

## 🙏 Acknowledgments

**핵심 철학:**
> "선동 앱이 아니라 판단 도구"  
> 모든 추천에는 근거와 반대 의견이 있다.  
> 모든 점수에는 출처가 있다.  
> 사용자는 "확정"만 한다.

**Happy Trading! 🚀**
