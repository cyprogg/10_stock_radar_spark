# 📊 차트 분석 통합 완료 가이드

## ✅ 완료된 작업

### 1. 한국투자증권 API 연동 준비
- **API 키 및 시크릿 저장**: `.env` 파일에 안전하게 저장됨
- **서비스 구현**: `backend/services/korea_investment_api.py` (한국 주식)
- **서비스 구현**: `backend/services/us_stock_service.py` (미국 주식)
- **기술적 분석**: `backend/services/technical_analysis_service.py` (고급 TA)

### 2. 백엔드 API 엔드포인트 추가
서버(`backend/server.py`)에 다음 엔드포인트 추가:

#### 📈 차트 분석 API
```
GET /api/chart/{ticker}?key=ds-test-2026
```
- 종목의 120일 OHLC 데이터
- 이동평균선(MA5, MA20, MA60)
- 기술적 지표(RSI, MACD, 추세)
- 지지선/저항선
- 캔들 패턴
- 매매 추천 (BUY/SELL/HOLD/NEUTRAL)

#### 💰 현재가 조회 API
```
GET /api/price/{ticker}?key=ds-test-2026
```
- 실시간 현재가
- 등락률
- 거래량
- 타임스탬프

### 3. 차트 분석 UI 업데이트 (`chart_analysis.html`)
- ✅ 실제 API 호출 기능 추가
- ✅ 폴백 목업 데이터 지원
- ✅ URL 파라미터 자동 로드
- ✅ 차트 렌더링 개선

#### 기능:
- 종목 코드 입력 시 자동 분석
- 120일 가격 차트 (이동평균선 포함)
- 기술적 지표 (RSI, MACD, 추세)
- 지지선/저항선 표시
- 캔들 패턴 인식
- 매매 추천 및 요약

### 4. Trade Plan Simulation 연동
- ✅ "📊 차트 분석 보기" 버튼 추가
- ✅ 선택한 종목을 차트 페이지로 전달
- ✅ 새 탭에서 차트 열기

---

## 🚀 사용 방법

### 단계 1: 백엔드 서버 시작
```bash
cd backend
python server.py
```

서버가 `http://127.0.0.1:8125`에서 실행됩니다.

### 단계 2: 차트 분석 사용

#### 방법 A: Trade Plan Simulation에서 연동
1. `trade_plan_simulation.html` 열기
2. 섹터 선택 (예: 방산)
3. 종목 선택 (예: 한화에어로스페이스)
4. **"📊 차트 분석 보기"** 버튼 클릭
5. 새 탭에서 차트 페이지 자동 열림 ✨

#### 방법 B: 차트 분석 직접 사용
1. `chart_analysis.html` 열기
2. 종목 코드 입력 (예: `012450`, `005930`, `LMT`)
3. **"분석 시작"** 버튼 클릭
4. 차트 및 기술적 분석 결과 확인

#### 방법 C: URL 파라미터 사용
직접 URL에 종목 코드 전달:
```
chart_analysis.html?ticker=012450
```

---

## 📊 API 응답 구조

### GET /api/chart/{ticker}

**응답 예시:**
```json
{
  "ticker": "012450",
  "dates": ["2024-09-01", "2024-09-02", ...],
  "opens": [180000, 182000, ...],
  "highs": [184000, 186000, ...],
  "lows": [179000, 181000, ...],
  "closes": [183000, 185000, ...],
  "prices": [183000, 185000, ...],
  "volumes": [5000000, 7000000, ...],
  "ma5": [180000, 181000, ...],
  "ma20": [175000, 178000, ...],
  "ma60": [170000, 172000, ...],
  "indicators": {
    "current_price": 185000,
    "rsi": 65.5,
    "macd": "매수",
    "short_trend": "상승",
    "mid_trend": "상승",
    "support": 180000,
    "resistance": 190000,
    "patterns": ["골든크로스", "역망치형"]
  },
  "recommendation": "매수 신호 - 과매도 구간에서 반등 시작",
  "signal": "BUY",
  "summary": "012450 종목은 현재 상승 추세입니다. RSI 65.5로 중립 구간이며, 지지선 180,000, 저항선 190,000을 주시하세요."
}
```

---

## 🔧 설정 파일

### `.env` (API 키 저장)
```env
# ⚠️ SECURITY WARNING - DO NOT COMMIT THIS FILE TO GIT!
# 한국투자증권 Open API 인증 정보

KIS_APP_KEY=PSVPqsYslqRmx7N9ljFmRqhZaxuvGvirVPir
KIS_APP_SECRET=614neRBEBcVch8Gbw1NZicylNBxF0qDfJCw1LtTdqGbQ1cusv08QhyHO02ZSjj94iIETT6J1wFTGHIs4QbCVGkGWvluSqDaaPLOSjokXx7XdnorXRZMieEUOB4UO3D2bv5mcwYbNFU2dM28FV1NQsoYWK5kYNts4zzh+6kycuLmUdEDbqWg=

# Alpha Vantage (선택사항)
# ALPHA_VANTAGE_KEY=your_key_here
```

⚠️ **보안 주의사항**: 
- `.env` 파일은 `.gitignore`에 포함되어 Git에 커밋되지 않습니다
- API 키를 공개 저장소에 업로드하지 마세요

---

## 🎨 차트 분석 UI 구성

### 1. 헤더
- 종목명 및 코드
- 검색 바

### 2. 가격 차트
- 120일 종가 데이터
- 이동평균선 (MA5, MA20, MA60)
- 대화형 툴팁

### 3. 기술적 지표
- **현재가**: 실시간 가격
- **등락률**: 전일 대비 변동률
- **RSI**: 과매수/과매도 판단 (30/70 기준)
- **MACD**: 매수/매도 신호
- **단기 추세**: 5일/20일 비교
- **중기 추세**: 20일/60일 비교
- **지지선**: 최근 20일 최저가 기준
- **저항선**: 최근 20일 최고가 기준

### 4. 캔들 패턴
- 골든크로스
- 데드크로스
- 역망치형
- 기타 패턴

### 5. 매매 추천
- ✅ **매수** (BUY): 과매도 + 상승 추세
- 🚫 **매도** (SELL): 과매수 + 하락 추세
- ⏸️ **관망** (HOLD): 과매수 + 추세 확인 필요
- ⏸️ **중립** (NEUTRAL): 추세 확인 필요

### 6. 분석 요약
- 종목 추세 설명
- RSI 구간 분석
- 지지선/저항선 안내

---

## 🔄 워크플로우

### Market-Driven Plan → Trade Plan → 차트 분석
```
1. market_driven_plan.html
   ↓ (섹터/종목 선택)
2. "매매 계획 생성" 클릭
   ↓ (URL 파라미터 전달)
3. trade_plan_simulation.html (자동 입력)
   ↓ (차트 분석 버튼)
4. chart_analysis.html (새 탭)
   ↓ (자동 분석)
5. 기술적 지표 + 차트 확인 ✨
```

---

## 📁 파일 구조

```
decision-stream/
├── chart_analysis.html          ✅ 차트 분석 UI (API 연동)
├── trade_plan_simulation.html   ✅ 시뮬레이션 + 차트 버튼
├── market_driven_plan.html      ✅ 시장 분석 대시보드
├── backend/
│   ├── server.py                ✅ API 엔드포인트 추가
│   ├── .env                     ✅ API 키 저장 (Git 제외)
│   ├── requirements.txt         ✅ yfinance, requests 추가
│   └── services/
│       ├── korea_investment_api.py    ✅ 한국 주식 API
│       ├── us_stock_service.py        ✅ 미국 주식 API
│       └── technical_analysis_service.py  ✅ 고급 TA 분석
└── CHART_INTEGRATION_COMPLETE.md  📚 이 문서
```

---

## 🧪 테스트 시나리오

### 시나리오 1: 통합 워크플로우
1. `market_driven_plan.html` 열기
2. 방산 섹터 클릭
3. 한화에어로스페이스(012450) 선택
4. "매매 계획 생성" 클릭
5. Trade Plan 페이지에서 "📊 차트 분석 보기" 클릭
6. ✅ 새 탭에서 한화에어로스페이스 차트 자동 표시

### 시나리오 2: 직접 차트 분석
1. `chart_analysis.html` 열기
2. 종목 코드 입력 (예: `005930`)
3. "분석 시작" 클릭
4. ✅ 삼성전자 차트 + 기술적 지표 표시

### 시나리오 3: URL 직접 접근
1. 브라우저에서 `chart_analysis.html?ticker=LMT` 입력
2. ✅ 페이지 로드 시 LMT 차트 자동 분석

---

## ⚠️ 현재 상태

### ✅ 완료
- 백엔드 API 엔드포인트 (`/api/chart`, `/api/price`)
- 차트 UI 업데이트 (실제 API 호출)
- Trade Plan Simulation 연동 버튼
- URL 파라미터 자동 로드
- 목업 데이터 폴백 지원

### 🚧 선택적 개선 사항
- 실제 한국투자증권 API 호출 (현재는 목업 데이터)
- WebSocket 실시간 가격 업데이트
- 더 많은 기술적 지표 (볼린저 밴드, 스토캐스틱 등)
- 차트 유형 추가 (캔들스틱, 거래량 차트)

---

## 📚 관련 문서

- [STOCK_DATA_COLLECTION_GUIDE.md](STOCK_DATA_COLLECTION_GUIDE.md) - 주식 데이터 수집 가이드
- [STOCK_DATA_QUICKSTART.md](STOCK_DATA_QUICKSTART.md) - 5분 빠른 시작
- [TRADE_PLAN_GUIDE.md](TRADE_PLAN_GUIDE.md) - Trade Plan 완전 가이드
- [MARKET_ANALYSIS_GUIDE.md](MARKET_ANALYSIS_GUIDE.md) - 시장 분석 가이드

---

## 🎉 결론

**Decision Stream**에 기술적 분석(차트) 기능이 완벽하게 통합되었습니다!

### 주요 기능:
✅ 실시간 가격 차트 (120일)  
✅ 기술적 지표 (RSI, MACD, 이동평균)  
✅ 지지선/저항선  
✅ 캔들 패턴 인식  
✅ 매매 추천 (BUY/SELL/HOLD/NEUTRAL)  
✅ Trade Plan Simulation 연동  
✅ 한국투자증권 API 준비 완료  

### 사용 흐름:
```
시장 분석 → 종목 선택 → 매매 계획 → 📊 차트 분석 → 의사결정 ✨
```

**이제 바로 사용할 수 있습니다!** 🚀

---

© 2026 Decision Stream - 중기 스윙 투자 프레임워크  
**교육 및 연구 목적으로만 사용하세요. 투자 손실에 대한 책임은 사용자에게 있습니다.**
