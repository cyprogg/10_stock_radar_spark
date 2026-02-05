# 📊 Decision Stream - 중기 스윙 투자 시스템

## 프로젝트 개요
**Decision Stream**은 퇴직자 관점에서 설계된 중기 스윙 투자 지원 시스템입니다.

### 핵심 철학
- ❌ 단기 급등주 추격
- ✅ 중기 (1~3개월) 안정적 스윙
- ✅ 월 1~2회 매매
- ✅ 손절 -8%, 목표 +15~30%

---

## 🏗️ 시스템 구조

```
decision-stream/
├── home.html                       # 프로젝트 홈 (시작점)
├── market_driven_plan.html         # 🆕 시장 분석 기반 매매 계획 (추천!)
├── trade_plan_simulation.html      # 매매 계획 시뮬레이션 트레이닝
├── chart_analysis.html             # 📊 기술적 분석 차트
├── index.html                      # Decision Stream 통합 대시보드
├── backend/
│   ├── server.py                   # FastAPI 서버 (API 엔드포인트)
│   ├── .env                        # API 키 저장 (Git 제외)
│   ├── requirements.txt
│   └── services/
│       ├── korea_investment_api.py    # 한국투자증권 API
│       ├── us_stock_service.py        # 미국 주식 API
│       └── technical_analysis_service.py  # 고급 TA 분석
├── screener/
│   ├── main_monthly.py             # 월 1회 스크리너 (MVP)
│   ├── requirements.txt
│   └── data/
│       ├── raw/                    # 표준 CSV
│       │   ├── universe.csv
│       │   ├── news_events.csv
│       │   ├── prices_daily.csv
│       │   ├── flows_daily.csv
│       │   └── index_kospi.csv
│       ├── hts_raw/                # HTS 원본 CSV
│       │   ├── prices/
│       │   └── flows/
│       └── output/                 # 스크리너 결과
│           └── candidates_YYYYMM.csv
├── tools/
│   ├── convert_hts_prices.py      # 키움/미래 일봉 변환
│   └── convert_hts_flows.py       # 키움/미래 수급 변환
├── README.md                       # 프로젝트 개요
├── QUICKSTART.md                   # 상세 실행 가이드
├── TRADE_PLAN_GUIDE.md             # 매매 계획 트레이닝 가이드
├── MARKET_ANALYSIS_GUIDE.md        # 시장 분석 해석 가이드
├── CHART_INTEGRATION_COMPLETE.md   # 📊 차트 분석 통합 가이드
└── STOCK_DATA_COLLECTION_GUIDE.md  # 주식 데이터 수집 가이드
```

---

## 🎯 주요 기능

### 1) 🆕 Market-Driven Trade Plan (추천!)
- **시장 상황 기반 자동 전략 추천**
- Market Regime 분석 (RISK_ON/OFF)
- Sector Heatmap (SURGE 자금 흐름)
- Stock Funnel (Leader/Follower 자동 분류)
- 최적 타이밍 및 전략 자동 제시

📘 **상세 가이드**: [MARKET_ANALYSIS_GUIDE.md](MARKET_ANALYSIS_GUIDE.md)

### 2) Market Regime
- **RISK_ON / RISK_OFF** 판단
- 20일 이평선 + 변동성 기반

### 3) Sector Heatmap
- 자금 흐름 분석 (SURGE / NORMAL)
- 방위산업 · 에너지 · 신기술

### 4) Stock Funnel
- **Leader**: 선도주 (매수 후보)
- **Follower**: 추종주 (관찰)
- **No-Go**: 리스크 높음 (회피)

### 5) Watchlist & Checklist
- 8개 항목 체크
- ✔ 6개 이상 → 매수 후보

### 6) Market Intelligence
- AI 기반 시장 해설 생성

### 7) Trade Plan Simulation Training
- **안전한 시뮬레이션 환경**: 실제 자금 투입 전 연습
- **7요소 체크리스트**: 수급, 정책/테마, 시장 사이클, 기업 질, 서사, 하방 리스크, 시간 적합성
- **🆕 3가지 진입 전략**: 즉시 매수(100%) / 조정 대기(98%) / 깊은 조정(95%)
- **자동 포지션 계산**: 진입가, 손절가, 목표가, 매수 수량
- **리스크 관리**: 보수/중립/공격 성향별 파라미터
- **🆕 통화 자동 전환**: 미국 주식($) / 한국 주식(₩) 자동 구분
- **성과 추적**: 승률, 평균 수익률, 손익비 통계
- **실전 전환 가이드**: 30회 시뮬레이션 후 체크리스트

📘 **상세 가이드**: 
- [TRADE_PLAN_GUIDE.md](TRADE_PLAN_GUIDE.md) - 기본 사용법
- [ENTRY_STRATEGY_UPDATE.md](ENTRY_STRATEGY_UPDATE.md) - 🆕 진입 전략 가이드

### 8) 📊 차트 분석 (Technical Analysis)
- **120일 가격 차트**: 이동평균선 (MA5, MA20, MA60)
- **기술적 지표**: RSI, MACD, 추세 분석
- **지지선/저항선**: 자동 계산
- **캔들 패턴 인식**: 골든크로스, 역망치형 등
- **매매 추천**: BUY/SELL/HOLD/NEUTRAL
- **Trade Plan 연동**: 시뮬레이션에서 바로 차트 확인
- **한국투자증권 API**: 실시간 데이터 연동 준비 완료

📘 **상세 가이드**: [CHART_INTEGRATION_COMPLETE.md](CHART_INTEGRATION_COMPLETE.md)

---

## 🚀 Quick Start

### 1. 백엔드 서버 실행
```bash
cd backend
pip install -r requirements.txt
python server.py
```

### 2. 프론트엔드 열기

**🆕 Market-Driven Trade Plan (추천 시작점!):**
```bash
open market_driven_plan.html
# 시장 분석 → 섹터 선택 → 종목 선택 → 매매 계획 자동 생성
```

**Trade Plan Simulation (연습용):**
```bash
open trade_plan_simulation.html
# 실제 자금 투입 전 30회 이상 시뮬레이션 권장
```

**Decision Stream Dashboard (실시간 분석):**
```bash
open index.html
# 또는 브라우저에서 index.html 파일 직접 열기
```

### 3. 월간 스크리너 실행 (선택사항)
```bash
cd screener
pip install -r requirements.txt
python main_monthly.py
```

**📘 상세 가이드**: 
- 시장 분석 해석: [MARKET_ANALYSIS_GUIDE.md](MARKET_ANALYSIS_GUIDE.md)
- 전체 시스템: [QUICKSTART.md](QUICKSTART.md)
- 매매 계획 트레이닝: [TRADE_PLAN_GUIDE.md](TRADE_PLAN_GUIDE.md)
- 빠른 참조: [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
- 구현 요약: [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)

---

## 📋 HTS CSV 다운로드 가이드

### 키움증권 (영웅문4)
1. **일봉**: `[0600] 일별주가` → CSV 저장
2. **수급**: `[0450] 투자자별 매매동향` → CSV 저장

### 미래에셋
1. **일봉**: `주식 → 일별시세` → CSV 저장
2. **수급**: `투자자별 매매동향` → CSV 저장

### 저장 위치
```
screener/data/hts_raw/prices/  ← 일봉 CSV
screener/data/hts_raw/flows/   ← 수급 CSV
```

---

## 🔄 월간 운용 루틴 (30분)

### 월초 (1~5일)
1. HTS에서 CSV 다운로드
2. 변환 스크립트 실행
3. 뉴스 CSV 입력 (10줄)
4. 스크리너 실행 → 후보 3개

### 월중 (6~20일)
- 조정 후 진입 (분할 2회)
- 주 1회 점검

### 월말 (21~말일)
- +15% → 30% 익절
- +25% → 추가 30% 익절
- 잔량 → 20일선 이탈 시 정리

---

## 📊 API 엔드포인트

### Decision Stream Dashboard

#### Market Regime
```http
GET /regime?key=ds-test-2026
```
**Response:**
```json
{
  "state": "RISK_ON",
  "risk_score": 7.2,
  "playbook": "공격적 진입",
  "drivers": ["금리 안정", "외국인 순매수"]
}
```

#### Sector Heatmap
```http
GET /sectors?key=ds-test-2026
```

#### Stock Funnel
```http
GET /funnel?sector=방산&key=ds-test-2026
```

#### Checklist
```http
GET /checklist?ticker=012450&sector=방산&key=ds-test-2026
```

### 🆕 Trade Plan Simulation

#### 매매 계획 생성
```http
POST /trade_plan/generate?key=ds-test-2026
Content-Type: application/json

{
  "market": "KR",
  "sector": "반도체",
  "ticker": "005930",
  "name": "삼성전자",
  "current_price": 75000,
  "period": "중기",
  "risk": "중립",
  "capital": 5000000
}
```

#### 섹터별 종목 조회
```http
GET /trade_plan/stocks?sector=반도체&key=ds-test-2026
```

#### 시뮬레이션 통계
```http
GET /trade_plan/stats?key=ds-test-2026
```

### 📊 차트 분석 API

#### 종목 차트 분석
```http
GET /api/chart/{ticker}?key=ds-test-2026
```
**Response:**
```json
{
  "ticker": "012450",
  "dates": ["2024-09-01", "2024-09-02", ...],
  "prices": [183000, 185000, ...],
  "ma5": [180000, 181000, ...],
  "ma20": [175000, 178000, ...],
  "ma60": [170000, 172000, ...],
  "indicators": {
    "rsi": 65.5,
    "macd": "매수",
    "short_trend": "상승",
    "mid_trend": "상승",
    "support": 180000,
    "resistance": 190000,
    "patterns": ["골든크로스"]
  },
  "signal": "BUY",
  "recommendation": "매수 신호 - 과매도 구간에서 반등 시작",
  "summary": "012450 종목은 현재 상승 추세입니다..."
}
```

#### 실시간 현재가
```http
GET /api/price/{ticker}?key=ds-test-2026
```

---
```

#### 시뮬레이션 통계
```http
GET /trade_plan/stats?key=ds-test-2026
```

---

## 🎓 투자 원칙

### ✅ 해야 할 것
- 정책·예산·계약 **확정** 뉴스만 추종
- 조정 후 진입
- 분할 익절 (계좌로 수익 옮기기)
- 손절 -8% 엄수

### ❌ 하지 말아야 할 것
- 뉴스 당일 추격 매수
- 급등주 추격
- 테마 과열 진입
- 손절 미루기

### 🆕 시뮬레이션 학습 단계

**초급 (1-10회)**: 프레임워크 이해 및 기본 절차 숙지
- 보수적 리스크로만 시뮬레이션
- 7요소 체크리스트 의미 완전 이해
- 손절가 엄수 연습

**중급 (11-30회)**: 리스크 관리 및 포지션 사이징 숙달
- 목표: 승률 50% 이상, 손익비 1.8:1 이상
- 중립 리스크 도입
- 익절 전략 비교 (1차 vs 1차+2차)

**고급 (31회+)**: 실전 준비
- 목표: 승률 55% 이상, 손익비 2.2:1 이상
- 공격적 리스크 도입 (조건: 총점 80점 이상)
- 2차 진입 및 트레일링 스톱 활용

**실전 전환 체크리스트**: [TRADE_PLAN_GUIDE.md](TRADE_PLAN_GUIDE.md) 참고

---

## 📈 시뮬레이션 결과

### 한 달 평균 (1억 원 기준)
- **종목**: 3개
- **실현 수익**: +3.78%
- **손절**: 1종목 (-8%)
- **익절**: 2종목 (+15~22%)

### 연간 목표
- **수익률**: 8~15%
- **최대 낙폭**: -10% 이내
- **매매 빈도**: 연 12~24회

---

## 🛠️ 기술 스택

- **Frontend**: HTML, CSS, Vanilla JavaScript
- **Backend**: Python FastAPI
- **Data**: CSV (HTS), Pandas
- **Scoring**: Rule-based Algorithm

---

## 📞 문의 및 기여

이 시스템은 **교육 및 연구 목적**입니다.
- 특정 종목 추천 아님
- 투자 손실 책임은 사용자에게 있음

---

## 📜 라이선스

MIT License - 자유롭게 사용·수정 가능
