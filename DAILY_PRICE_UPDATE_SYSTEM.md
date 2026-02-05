# 📅 매일 종가 자동 업데이트 시스템

## 🎯 요구사항

**중기 스윙 투자 특성:**
- 투자 기간: 1-3개월
- 매매 빈도: 월 1-2회
- **실시간 시세 불필요** → 일일 종가면 충분

**업데이트 시간:**
- 매일 **오후 6시** (한국 시간 기준)
- 한국 주식: 장 마감 후 (15:30 마감)
- 미국 주식: 전일 종가 (한국 시간 05:00 마감)

---

## 🏗️ 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────┐
│                 매일 오후 6시 (자동)                     │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
         ┌────────────────────────────┐
         │  백엔드 스케줄러 (APScheduler) │
         │  - 매일 18:00 실행            │
         └────────────┬───────────────┘
                      │
         ┌────────────┴────────────┐
         │                         │
         ▼                         ▼
┌─────────────────┐      ┌──────────────────┐
│ 한국투자증권 API │      │ Yahoo Finance API│
│ (한국 주식)      │      │ (미국 주식)       │
└────────┬────────┘      └────────┬─────────┘
         │                         │
         └────────────┬────────────┘
                      │
                      ▼
         ┌────────────────────────────┐
         │  stock_prices.json 생성    │
         │  {                         │
         │    "lastUpdate": "...",    │
         │    "prices": {...}         │
         │  }                         │
         └────────────┬───────────────┘
                      │
                      ▼
         ┌────────────────────────────┐
         │  프론트엔드 (HTML/JS)       │
         │  - JSON 파일 로드           │
         │  - 종목 선택 시 주가 표시   │
         └────────────────────────────┘
```

---

## 📋 구현 계획 (3단계)

### Phase 1: 백엔드 - 주가 조회 함수 구현 (30분)

#### 1.1 한국 주식 종가 조회 (한국투자증권 API)
```python
# backend/services/korea_investment_api.py

import os
import requests
from dotenv import load_dotenv

load_dotenv()

KIS_APP_KEY = os.getenv('KIS_APP_KEY')
KIS_APP_SECRET = os.getenv('KIS_APP_SECRET')
KIS_BASE_URL = 'https://openapi.koreainvestment.com:9443'

def get_kr_stock_price(ticker: str) -> float:
    """한국 주식 현재가 조회"""
    
    # 1. 토큰 발급
    token_url = f"{KIS_BASE_URL}/oauth2/tokenP"
    token_data = {
        "grant_type": "client_credentials",
        "appkey": KIS_APP_KEY,
        "appsecret": KIS_APP_SECRET
    }
    token_response = requests.post(token_url, json=token_data)
    access_token = token_response.json()['access_token']
    
    # 2. 현재가 조회
    price_url = f"{KIS_BASE_URL}/uapi/domestic-stock/v1/quotations/inquire-price"
    headers = {
        "authorization": f"Bearer {access_token}",
        "appkey": KIS_APP_KEY,
        "appsecret": KIS_APP_SECRET,
        "tr_id": "FHKST01010100"
    }
    params = {
        "fid_cond_mrkt_div_code": "J",
        "fid_input_iscd": ticker
    }
    
    response = requests.get(price_url, headers=headers, params=params)
    data = response.json()
    
    if data.get('rt_cd') == '0':
        price = int(data['output']['stck_prpr'])  # 현재가
        return price
    else:
        raise Exception(f"주가 조회 실패: {data.get('msg1')}")
```

#### 1.2 미국 주식 종가 조회 (Yahoo Finance)
```python
# backend/services/us_stock_service.py

import yfinance as yf

def get_us_stock_price(ticker: str) -> float:
    """미국 주식 현재가 조회 (Yahoo Finance)"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1d")
        
        if not hist.empty:
            price = hist['Close'].iloc[-1]
            return round(float(price), 2)
        else:
            raise Exception(f"주가 데이터 없음: {ticker}")
    except Exception as e:
        print(f"미국 주식 조회 실패 ({ticker}): {e}")
        return None
```

---

### Phase 2: 백엔드 - 스케줄러 구현 (20분)

#### 2.1 APScheduler 설치
```bash
pip install apscheduler
```

#### 2.2 스케줄러 구현
```python
# backend/scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import json
from services.korea_investment_api import get_kr_stock_price
from services.us_stock_service import get_us_stock_price

# 모든 종목 리스트
STOCK_LIST = {
    "US": [
        {"ticker": "LMT", "name": "Lockheed Martin"},
        {"ticker": "JNJ", "name": "Johnson & Johnson"}
    ],
    "KR": [
        {"ticker": "012450", "name": "한화에어로스페이스"},
        {"ticker": "079550", "name": "LIG넥스원"},
        {"ticker": "005930", "name": "삼성전자"},
        {"ticker": "000660", "name": "SK하이닉스"},
        {"ticker": "207940", "name": "삼성바이오로직스"},
        {"ticker": "068270", "name": "셀트리온"},
        {"ticker": "373220", "name": "LG에너지솔루션"},
        {"ticker": "096770", "name": "SK이노베이션"},
        {"ticker": "051910", "name": "LG화학"},
        {"ticker": "326030", "name": "SK바이오팜"},
        {"ticker": "005380", "name": "현대자동차"},
        {"ticker": "000270", "name": "기아"},
        {"ticker": "012330", "name": "현대모비스"},
        {"ticker": "009830", "name": "한화솔루션"},
        {"ticker": "011170", "name": "롯데케미칼"},
        {"ticker": "009540", "name": "한국조선해양"},
        {"ticker": "010140", "name": "삼성중공업"},
        {"ticker": "042660", "name": "한화오션"},
        {"ticker": "042700", "name": "한미반도체"}
    ]
}

def update_stock_prices():
    """모든 종목의 종가를 조회하여 JSON 파일에 저장"""
    print(f"[{datetime.now()}] 주가 업데이트 시작...")
    
    prices = {}
    
    # 미국 주식 조회
    for stock in STOCK_LIST["US"]:
        ticker = stock["ticker"]
        try:
            price = get_us_stock_price(ticker)
            if price:
                prices[ticker] = price
                print(f"✅ {ticker}: ${price}")
        except Exception as e:
            print(f"❌ {ticker} 조회 실패: {e}")
    
    # 한국 주식 조회
    for stock in STOCK_LIST["KR"]:
        ticker = stock["ticker"]
        try:
            price = get_kr_stock_price(ticker)
            if price:
                prices[ticker] = price
                print(f"✅ {ticker}: ₩{price:,}")
        except Exception as e:
            print(f"❌ {ticker} 조회 실패: {e}")
    
    # JSON 파일로 저장
    data = {
        "lastUpdate": datetime.now().isoformat(),
        "updateTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "prices": prices
    }
    
    with open('stock_prices.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"[{datetime.now()}] 주가 업데이트 완료! ({len(prices)}개 종목)")

def start_scheduler():
    """스케줄러 시작"""
    scheduler = BackgroundScheduler()
    
    # 매일 오후 6시 실행
    scheduler.add_job(
        update_stock_prices,
        'cron',
        hour=18,
        minute=0,
        id='daily_price_update'
    )
    
    scheduler.start()
    print("✅ 스케줄러 시작: 매일 오후 6시에 주가 업데이트")
    
    # 즉시 한 번 실행 (테스트용)
    # update_stock_prices()
```

#### 2.3 서버에서 스케줄러 실행
```python
# backend/server.py

from fastapi import FastAPI
from scheduler import start_scheduler

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    """서버 시작 시 스케줄러 시작"""
    start_scheduler()

# ... 기존 코드 ...
```

---

### Phase 3: 프론트엔드 - JSON 로드 및 표시 (20분)

#### 3.1 stock_prices.json 로드
```javascript
// trade_plan_simulation.html

let cachedPrices = null;
let lastPriceUpdate = null;

async function loadStockPrices() {
    try {
        const response = await fetch('stock_prices.json');
        const data = await response.json();
        cachedPrices = data.prices;
        lastPriceUpdate = data.updateTime;
        
        console.log(`✅ 주가 데이터 로드 완료 (${lastPriceUpdate})`);
        updatePriceUpdateBadge(lastPriceUpdate);
        
        return cachedPrices;
    } catch (error) {
        console.error('주가 데이터 로드 실패:', error);
        return null;
    }
}

function updatePriceUpdateBadge(updateTime) {
    // 헤더에 업데이트 시간 표시
    const badge = document.getElementById('price-update-badge');
    if (badge) {
        badge.textContent = `주가 업데이트: ${updateTime}`;
    }
}
```

#### 3.2 STOCK_DATABASE에 JSON 데이터 적용
```javascript
// 페이지 로드 시 JSON 데이터로 주가 업데이트
document.addEventListener('DOMContentLoaded', async function() {
    // JSON 파일에서 주가 로드
    const prices = await loadStockPrices();
    
    if (prices) {
        // STOCK_DATABASE 업데이트
        for (const sector in STOCK_DATABASE) {
            STOCK_DATABASE[sector].forEach(stock => {
                if (prices[stock.ticker]) {
                    stock.price = prices[stock.ticker];
                    console.log(`📊 ${stock.name}: ${stock.price}`);
                }
            });
        }
    }
    
    // 기존 초기화 로직
    loadSimulationHistory();
    setupEventListeners();
    loadURLParameters();
});
```

#### 3.3 UI에 업데이트 시간 표시
```html
<!-- trade_plan_simulation.html 헤더에 추가 -->
<header>
    <div class="header-content">
        <h1>📊 Trade Plan Simulation Training</h1>
        <div style="display: flex; gap: 10px; align-items: center;">
            <span id="price-update-badge" class="badge info" style="font-size: 11px;">
                주가 로딩 중...
            </span>
            <a href="index.html" class="btn-secondary" style="padding: 8px 16px;">홈으로</a>
        </div>
    </div>
</header>

<style>
.badge.info {
    background: rgba(66, 153, 225, 0.2);
    border: 1px solid rgba(66, 153, 225, 0.5);
    color: #90cdf4;
    padding: 4px 10px;
    border-radius: 12px;
    font-weight: 500;
}
</style>
```

---

## 🚀 배포 및 실행

### 1. 필요한 패키지 설치
```bash
cd backend
pip install -r requirements.txt
pip install apscheduler yfinance python-dotenv
```

### 2. requirements.txt 업데이트
```txt
fastapi==0.104.1
uvicorn==0.24.0
python-dotenv==1.0.0
apscheduler==3.10.4
yfinance==0.2.32
requests==2.31.0
```

### 3. 서버 실행
```bash
cd backend
python server.py
```

**출력 예시:**
```
✅ 스케줄러 시작: 매일 오후 6시에 주가 업데이트
INFO:     Uvicorn running on http://127.0.0.1:8125
```

### 4. 수동 업데이트 (테스트용)
```bash
# Python 콘솔에서
from scheduler import update_stock_prices
update_stock_prices()
```

**출력 예시:**
```
[2026-01-21 18:00:00] 주가 업데이트 시작...
✅ LMT: $581.25
✅ JNJ: $215.50
✅ 012450: ₩185,300
✅ 079550: ₩544,500
...
[2026-01-21 18:00:15] 주가 업데이트 완료! (21개 종목)
```

---

## 📊 stock_prices.json 예시

```json
{
  "lastUpdate": "2026-01-21T18:00:00.123456",
  "updateTime": "2026-01-21 18:00:00",
  "prices": {
    "LMT": 581.25,
    "JNJ": 215.50,
    "012450": 185300,
    "079550": 544500,
    "005930": 75200,
    "000660": 142500,
    "207940": 851000,
    "068270": 175800
  }
}
```

---

## ⚙️ 설정 옵션

### 업데이트 시간 변경
```python
# backend/scheduler.py
scheduler.add_job(
    update_stock_prices,
    'cron',
    hour=18,      # 오후 6시
    minute=0,     # 0분
    id='daily_price_update'
)
```

### 업데이트 주기 변경 (예: 매시간)
```python
scheduler.add_job(
    update_stock_prices,
    'interval',
    hours=1,
    id='hourly_price_update'
)
```

---

## 🔍 장점

✅ **중기 스윙에 최적화**
- 일일 종가만 사용 → 과도한 업데이트 불필요
- 서버 부하 최소화

✅ **완전 자동화**
- 매일 오후 6시 자동 실행
- 수동 개입 불필요

✅ **신뢰성**
- 한국투자증권 공식 API (한국 주식)
- Yahoo Finance (미국 주식, 무료)

✅ **사용자 경험**
- 항상 최신 종가 표시
- 업데이트 시간 표시로 신뢰도 상승

✅ **유지보수 편의**
- JSON 파일로 캐싱 → 빠른 로딩
- API 장애 시 이전 데이터 사용 가능

---

## 📅 타임라인

| 단계 | 작업 | 소요 시간 | 상태 |
|------|------|-----------|------|
| 1 | 한국투자증권 API 함수 구현 | 15분 | ⏳ |
| 2 | Yahoo Finance API 함수 구현 | 10분 | ⏳ |
| 3 | APScheduler 설정 | 15분 | ⏳ |
| 4 | JSON 저장 로직 구현 | 10분 | ⏳ |
| 5 | 프론트엔드 JSON 로드 | 15분 | ⏳ |
| 6 | UI 업데이트 시간 표시 | 10분 | ⏳ |
| 7 | 테스트 및 디버깅 | 15분 | ⏳ |
| **합계** | | **90분** | |

---

## 💡 추가 기능 (선택)

### 1. 수동 업데이트 버튼
```html
<button onclick="refreshPrices()">🔄 주가 새로고침</button>
```

### 2. API 엔드포인트 추가
```python
@app.post("/api/prices/refresh")
async def refresh_prices(key: str = Query(...)):
    verify_key(key)
    update_stock_prices()
    return {"message": "주가 업데이트 완료"}
```

### 3. 업데이트 히스토리
```json
{
  "history": [
    {"date": "2026-01-21", "totalStocks": 21, "success": 21, "failed": 0},
    {"date": "2026-01-20", "totalStocks": 21, "success": 21, "failed": 0}
  ]
}
```

---

## 🎉 결론

**매일 오후 6시 자동 종가 업데이트 시스템:**
- ✅ 중기 스윙 투자에 완벽
- ✅ 완전 자동화
- ✅ 한국투자증권 + Yahoo Finance API
- ✅ 90분 내 구현 가능

**다음 단계:**
구현을 시작할까요? 단계별로 진행하겠습니다! 🚀

---

> **작성일:** 2026-01-21  
> **상태:** 설계 완료 / 구현 대기  
> **예상 소요 시간:** 90분
