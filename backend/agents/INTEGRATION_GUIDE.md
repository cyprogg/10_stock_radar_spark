# AI Agent 통합 가이드

## 📋 전체 파이프라인 사용 후 다음 단계

Agent Orchestrator의 전체 파이프라인을 선택한 후, 다음 3단계를 진행하세요:

---

## 🎯 Step 1: 데이터 준비 (필수)

Agent가 작동하려면 4가지 데이터가 필요합니다:

### 1-1. Market Data (시장 데이터)
```python
market_data = {
    # VIX & 변동성
    "vix": 15.2,                    # ← Yahoo Finance에서 수집
    "vkospi": 18.5,                 # ← KRX에서 수집
    
    # 코스피 지수
    "kospi": 2650,                  # ← KRX에서 수집
    "kospi_vs_ma20": 1.02,          # ← 계산 필요 (현재가 / 20일 이평)
    "kospi_vs_ma60": 1.05,          # ← 계산 필요 (현재가 / 60일 이평)
    "kospi_from_high": -5.2,        # ← 계산 필요 (고점 대비 %)
    
    # 미국 지수
    "sp500": 5200,                  # ← Yahoo Finance
    "sp500_vs_ma20": 1.03,          # ← 계산 필요
    "sp500_vs_ma60": 1.08,          # ← 계산 필요
    
    # 시장 폭
    "kospi_advancers": 650,         # ← KRX (상승 종목 수)
    "kospi_decliners": 500,         # ← KRX (하락 종목 수)
    "breadth_ratio": 1.3,           # ← 계산 (상승/하락)
    
    # 금리 & 환율 (선택)
    "us_10y": 4.25,                 # ← FRED API
    "usd_krw": 1320                 # ← Yahoo Finance
}
```

**데이터 소스:**
- **무료:** KRX 정보데이터시스템, Yahoo Finance, FRED
- **지연:** 20분 지연 데이터 사용 (무료)
- **주기:** 일 1회 업데이트 권장

### 1-2. Sectors Data (섹터 데이터)
```python
sectors_data = [
    {
        "sector": "방산",
        "volume_change_20d": 2.5,      # 거래대금 20일 변화율 (배수)
        "foreign_net_buy_5d": 150,     # 외국인 5일 순매수 (억)
        "inst_net_buy_5d": 200,        # 기관 5일 순매수 (억)
        "price_change_20d": 15.2,      # 20일 수익률 (%)
        "ma20_slope": 0.8,             # 20일선 기울기
        "new_high_stocks": 3,          # 신고가 종목 수
        "news_count_7d": 25,           # 7일 뉴스 건수
        "policy_keywords": ["수출", "계약"],
        "disclosure_count": 2,         # 공시 건수
        "duration": 14                 # 테마 지속 일수
    },
    # ... 다른 섹터들
]
```

**계산 방법:**
- 섹터별로 속한 종목들의 데이터를 집계
- 예: "방산" 섹터 = 한화에어로스페이스 + LIG넥스원 + ...

### 1-3. Stocks Data (종목 데이터)
```python
stocks_data = [
    {
        "ticker": "012450",
        "name": "한화에어로스페이스",
        "sector": "방산",
        
        # 가격 정보
        "current_price": 350000,
        "support_levels": [340000, 330000],    # 지지선
        "resistance_levels": [360000, 370000], # 저항선
        "ma20": 345000,
        "ma60": 340000,
        "atr_20d": 15000,            # ATR (평균 진폭)
        "volatility": 4.5,           # 일간 변동성 (%)
        
        # 9요소 점수
        "flow_score": 85,            # 자금 흐름
        "cycle_fit": True,           # 사이클 적합
        "quality_score": 90,         # 품질
        "governance_score": 80,      # 지배구조
        "narrative_score": 75,       # 서사
        "risk_score": 15,            # 리스크 (낮을수록 좋음)
        "time_fit": True,            # 타이밍
        "value_score": 70,           # 밸류에이션
        
        # 모멘텀 품질
        "momentum_quality": {
            "sector_sync": True,           # 섹터 동반 상승
            "inst_participation": True,    # 기관 참여
            "news_type": "fundamental",    # fundamental | rumor | single
            "group_rally": True            # 그룹 랠리
        },
        
        # No-Go 체크
        "gap_up_with_distribution": False,
        "single_rumor": False,
        "late_theme": False,
        "no_structure": False,
        "retail_dominance": 0.3        # 개인 비중 (0~1)
    },
    # ... 다른 종목들
]
```

### 1-4. User Profile (사용자 프로필)
```python
user_profile = {
    "period": "단기",              # "단기" 또는 "중기"
    "risk_profile": "중립",        # "보수", "중립", "공격"
    "account_size": 10000000      # 계좌 크기 (원) - 선택 사항
}
```

---

## 🔧 Step 2: 데이터 수집기 구현

기존 서비스를 활용하여 데이터 수집기를 만드세요:

### 파일: `backend/services/agent_data_provider.py` (생성 필요)

```python
from typing import Dict, List, Any
import yfinance as yf
from datetime import datetime, timedelta
from .scoring_engine import calculate_flow_score
from .technical_analysis_service import calculate_technical_indicators

class AgentDataProvider:
    """Agent를 위한 데이터 제공자"""
    
    def get_market_data(self) -> Dict[str, Any]:
        """시장 데이터 수집"""
        # VIX
        vix = yf.Ticker("^VIX").history(period="1d")['Close'].iloc[-1]
        
        # 코스피 (Yahoo Finance: ^KS11)
        kospi = yf.Ticker("^KS11")
        kospi_hist = kospi.history(period="3mo")
        current_kospi = kospi_hist['Close'].iloc[-1]
        ma20 = kospi_hist['Close'].rolling(20).mean().iloc[-1]
        ma60 = kospi_hist['Close'].rolling(60).mean().iloc[-1]
        
        # S&P 500
        sp500 = yf.Ticker("^GSPC")
        sp500_hist = sp500.history(period="3mo")
        current_sp500 = sp500_hist['Close'].iloc[-1]
        sp500_ma20 = sp500_hist['Close'].rolling(20).mean().iloc[-1]
        sp500_ma60 = sp500_hist['Close'].rolling(60).mean().iloc[-1]
        
        return {
            "vix": vix,
            "kospi": current_kospi,
            "kospi_vs_ma20": current_kospi / ma20,
            "kospi_vs_ma60": current_kospi / ma60,
            "kospi_from_high": ((current_kospi / kospi_hist['Close'].max()) - 1) * 100,
            "sp500": current_sp500,
            "sp500_vs_ma20": current_sp500 / sp500_ma20,
            "sp500_vs_ma60": current_sp500 / sp500_ma60,
            "breadth_ratio": 1.2,  # KRX API 연동 필요
            "kospi_advancers": 0,  # KRX API 연동 필요
            "kospi_decliners": 0   # KRX API 연동 필요
        }
    
    def get_sectors_data(self, tickers_by_sector: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """섹터별 데이터 수집"""
        sectors_data = []
        
        for sector, tickers in tickers_by_sector.items():
            # 섹터 내 종목들의 데이터 집계
            sector_data = self._aggregate_sector_data(sector, tickers)
            sectors_data.append(sector_data)
        
        return sectors_data
    
    def get_stocks_data(self, tickers: List[str]) -> List[Dict[str, Any]]:
        """종목 데이터 수집"""
        stocks_data = []
        
        for ticker in tickers:
            stock_data = self._get_stock_data(ticker)
            if stock_data:
                stocks_data.append(stock_data)
        
        return stocks_data
    
    def _aggregate_sector_data(self, sector: str, tickers: List[str]) -> Dict[str, Any]:
        """섹터 데이터 집계"""
        # 구현 필요
        pass
    
    def _get_stock_data(self, ticker: str) -> Dict[str, Any]:
        """개별 종목 데이터 수집"""
        # 구현 필요
        pass
```

---

## 🌐 Step 3: API 엔드포인트 추가

`backend/server_v2.py`에 API 엔드포인트를 추가하세요:

```python
from agents.orchestrator import AgentOrchestrator
from services.agent_data_provider import AgentDataProvider

# Initialize
orchestrator = AgentOrchestrator()
data_provider = AgentDataProvider()

@app.post("/api/agent/analyze")
async def run_agent_analysis(request: Request):
    """전체 Agent 분석 실행"""
    body = await request.json()
    
    # 1. 데이터 수집
    market_data = data_provider.get_market_data()
    
    # 2. 종목 리스트 (사용자 입력 또는 기본값)
    tickers = body.get("tickers", ["005930", "000660", "035720"])
    
    # 섹터별 분류 (간단한 예시)
    tickers_by_sector = {
        "반도체": ["005930", "000660"],
        "IT": ["035720"]
    }
    
    sectors_data = data_provider.get_sectors_data(tickers_by_sector)
    stocks_data = data_provider.get_stocks_data(tickers)
    
    # 3. 사용자 프로필
    user_profile = {
        "period": body.get("period", "단기"),
        "risk_profile": body.get("risk_profile", "중립"),
        "account_size": body.get("account_size", 0)
    }
    
    # 4. Agent 실행
    result = orchestrator.run_full_analysis(
        market_data,
        sectors_data,
        stocks_data,
        user_profile
    )
    
    return result

@app.post("/api/agent/quick-analyze")
async def run_quick_analysis(request: Request):
    """단일 종목 빠른 분석"""
    body = await request.json()
    ticker = body.get("ticker")
    
    if not ticker:
        return JSONResponse(status_code=400, content={"error": "ticker required"})
    
    # 데이터 수집
    market_data = data_provider.get_market_data()
    stock_data = data_provider.get_stocks_data([ticker])[0]
    
    user_profile = {
        "period": body.get("period", "단기"),
        "risk_profile": body.get("risk_profile", "중립"),
        "account_size": body.get("account_size", 0)
    }
    
    # 빠른 분석 실행
    result = orchestrator.run_quick_analysis(
        market_data,
        stock_data,
        user_profile
    )
    
    return result
```

---

## 🖥️ Step 4: 프론트엔드 호출

HTML/JavaScript에서 API 호출:

```javascript
// 전체 분석
async function runFullAnalysis() {
    const response = await fetch('/api/agent/analyze?key=ds-test-2026', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            tickers: ['005930', '000660', '035720'],
            period: '단기',
            risk_profile: '중립',
            account_size: 10000000
        })
    });
    
    const result = await response.json();
    
    // 결과 표시
    console.log('시장 상태:', result.market_regime.state);
    console.log('Playbook:', result.market_regime.playbook);
    console.log('상위 섹터:', result.ranked_sectors);
    console.log('추천 종목:', result.recommendations);
}

// 단일 종목 분석
async function analyzeStock(ticker) {
    const response = await fetch('/api/agent/quick-analyze?key=ds-test-2026', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            ticker: ticker,
            period: '단기',
            risk_profile: '중립'
        })
    });
    
    const result = await response.json();
    
    // 결과 표시
    displayStockAnalysis(result);
}
```

---

## 📊 Step 5: 결과 활용

분석 결과를 다음과 같이 활용하세요:

### 5-1. 시장 상태 확인
```javascript
if (result.market_regime.state === "RISK_ON") {
    // 공격적 매수 전략
    showPlaybook(result.market_regime.playbook);
} else {
    // 방어적 전략
    showWarning("방어 모드 진입");
}
```

### 5-2. 섹터 로테이션
```javascript
const topSectors = result.ranked_sectors.slice(0, 3);
topSectors.forEach(sector => {
    console.log(`${sector.sector}: ${sector.flow_score}점 (${sector.signal})`);
});
```

### 5-3. 종목 필터링
```javascript
const leaders = result.screened_stocks.leaders;
leaders.forEach(stock => {
    if (stock.action === "BUY_NOW") {
        addToWatchlist(stock);
    }
});
```

### 5-4. 매매 계획 실행
```javascript
result.recommendations.forEach(rec => {
    const tradePlan = rec.trade_plan;
    
    console.log(`진입: ${tradePlan.entry.pullback.toLocaleString()}원`);
    console.log(`손절: ${tradePlan.stop_loss.toLocaleString()}원`);
    console.log(`목표: ${tradePlan.targets.conservative.toLocaleString()}원`);
    
    // 알림 설정
    setAlert(rec.ticker, tradePlan.entry.pullback);
});
```

### 5-5. 반론 검토
```javascript
rec.devil_advocate.counter_arguments.forEach(counter => {
    if (counter.severity === "high") {
        showWarning(`⚠️ ${counter.category}: ${counter.point}`);
    }
});
```

---

## ⏱️ 실행 주기 권장

### 일일 1회 (09:00~09:30)
1. 시장 상태 분석 (Market Regime)
2. 섹터 랭킹 업데이트
3. 관심 종목 재분석

### 실시간 (필요시)
- 특정 종목 빠른 분석 (`quick-analyze`)
- 신규 종목 스크리닝

---

## 🎯 요약: 당신이 할 일

1. ☑️ **데이터 수집기 구현** (`agent_data_provider.py`)
2. ☑️ **API 엔드포인트 추가** (`server_v2.py`)
3. ☑️ **프론트엔드 연결** (버튼 클릭 → API 호출)
4. ☑️ **결과 UI 디자인** (표, 차트, 알림)
5. ☑️ **스케줄러 설정** (매일 아침 자동 실행)

---

## 📝 다음 문서

- [DATA_COLLECTION_GUIDE.md](DATA_COLLECTION_GUIDE.md) - 데이터 수집 상세 가이드
- [API_REFERENCE.md](API_REFERENCE.md) - API 명세서
- [UI_INTEGRATION_GUIDE.md](UI_INTEGRATION_GUIDE.md) - UI 통합 가이드

---

**질문이 있으시면 언제든 물어보세요!** 🚀
