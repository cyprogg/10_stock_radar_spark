# 📊 합법적인 주식 시세 수집 가이드

## ⚖️ 법적 고려사항

### ✅ 합법적인 방법
1. **공식 API 사용** (가장 안전)
2. **증권사 HTS/MTS에서 제공하는 CSV 다운로드** (수동, 안전)
3. **무료 공개 데이터 API** (제한적이지만 합법)
4. **라이선스 구매** (전문 트레이더용)

### ❌ 불법/위험한 방법
- 무단 크롤링/스크래핑 (저작권 침해)
- API 약관 위반 (과도한 요청)
- 재배포 금지 데이터 재판매

---

## 🇰🇷 한국 주식 시세 수집

### 방법 1: 증권사 HTS CSV 다운로드 (✅ 가장 안전)

#### 키움증권 (영웅문4)
```
1. 일봉 데이터
   - [0600] 종목별일별시세 → CSV 저장
   - 포함 데이터: 날짜, 종가, 시가, 고가, 저가, 거래량

2. 수급 데이터
   - [0450] 투자자별매매동향 → CSV 저장
   - 포함 데이터: 외국인/기관 매매량

장점:
✓ 100% 합법 (증권사 제공 기능)
✓ 정확한 데이터
✓ 수수료 무료 (계좌 보유 시)

단점:
✗ 수동 작업 필요 (월 1회)
✗ 실시간 아님 (하루 1회 업데이트)
```

#### 미래에셋증권
```
1. 일봉 데이터
   - 주식 → 일별시세 → CSV 저장

2. 수급 데이터
   - 투자자별 매매동향 → CSV 저장

장점/단점: 키움과 동일
```

---

### 방법 2: 한국투자증권 Open API (✅ 무료)

```python
# 한국투자증권 Open API
# https://apiportal.koreainvestment.com/

import requests

# 1. 회원가입 및 API 신청 (무료)
# 2. 앱 키(App Key) 및 앱 시크릿(App Secret) 발급

APP_KEY = "발급받은_앱_키"
APP_SECRET = "발급받은_앱_시크릿"
URL_BASE = "https://openapi.koreainvestment.com:9443"

# Access Token 발급
def get_access_token():
    url = f"{URL_BASE}/oauth2/tokenP"
    headers = {"content-type": "application/json"}
    data = {
        "grant_type": "client_credentials",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()['access_token']

# 주식 현재가 조회
def get_stock_price(ticker):
    token = get_access_token()
    url = f"{URL_BASE}/uapi/domestic-stock/v1/quotations/inquire-price"
    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {token}",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
        "tr_id": "FHKST01010100"
    }
    params = {
        "FID_COND_MRKT_DIV_CODE": "J",
        "FID_INPUT_ISCD": ticker
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json()

# 사용 예시
price_data = get_stock_price("005930")  # 삼성전자
print(price_data)
```

**특징:**
- ✅ 무료 (일 500회 제한)
- ✅ 실시간 가능 (WebSocket 지원)
- ✅ 공식 API (100% 합법)
- ⚠️ 회원가입 및 인증 필요

**신청 방법:**
1. https://apiportal.koreainvestment.com/ 접속
2. 회원가입 (증권 계좌 불필요)
3. API 신청 → 앱 키 발급
4. 일 500회 무료 사용

---

### 방법 3: 한국거래소(KRX) 공개 데이터 (✅ 무료)

```python
# KRX 정보데이터시스템
# http://data.krx.co.kr/

import requests
import pandas as pd

def get_krx_stock_data(date):
    """
    KRX에서 전종목 일별 시세 가져오기
    """
    url = "http://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd"
    
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "http://data.krx.co.kr/contents/MDC/MDI/mdiLoader"
    }
    
    data = {
        "bld": "dbms/MDC/STAT/standard/MDCSTAT01501",
        "mktId": "STK",  # 코스피
        "trdDd": date,  # YYYYMMDD
        "share": "1",
        "csvxls_isNo": "false"
    }
    
    response = requests.post(url, headers=headers, data=data)
    result = response.json()
    
    df = pd.DataFrame(result['OutBlock_1'])
    return df

# 사용 예시
df = get_krx_stock_data("20240121")
print(df.head())
```

**특징:**
- ✅ 완전 무료
- ✅ 전종목 데이터
- ✅ 공식 출처 (100% 합법)
- ⚠️ 실시간 아님 (장 종료 후 업데이트)
- ⚠️ 일별 데이터만 제공

---

### 방법 4: FinanceDataReader (✅ 오픈소스)

```python
# FinanceDataReader - 한국 금융 데이터 오픈소스
# https://github.com/FinanceData/FinanceDataReader

pip install finance-datareader

import FinanceDataReader as fdr

# 삼성전자 일봉 데이터
df = fdr.DataReader('005930', '2024-01-01', '2024-01-21')
print(df)

# 코스피 지수
kospi = fdr.DataReader('KS11', '2024-01-01')
print(kospi)

# 전종목 리스트
stocks = fdr.StockListing('KRX')
print(stocks)
```

**특징:**
- ✅ 완전 무료
- ✅ 설치 간단 (pip install)
- ✅ 오픈소스 (MIT 라이선스)
- ✅ KRX 공식 데이터 활용
- ⚠️ 실시간 아님 (일봉 데이터)

**데이터 출처:**
- KRX (한국거래소) 공개 데이터
- 네이버 금융 (공개 데이터만)
- Yahoo Finance (미국 주식)

---

## 🇺🇸 미국 주식 시세 수집

### 방법 1: Yahoo Finance API (✅ 무료)

```python
# yfinance - Yahoo Finance 공식 파이썬 라이브러리
pip install yfinance

import yfinance as yf

# Apple 주식 데이터
aapl = yf.Ticker("AAPL")

# 현재가
print(aapl.info['currentPrice'])

# 일봉 데이터
df = aapl.history(period="1mo")
print(df)

# 여러 종목 한번에
tickers = yf.Tickers("AAPL MSFT GOOGL")
print(tickers.tickers['AAPL'].info)
```

**특징:**
- ✅ 완전 무료
- ✅ 실시간 가능 (15분 지연)
- ✅ Yahoo Finance 공식 라이브러리
- ✅ 제한 없음

---

### 방법 2: Alpha Vantage API (✅ 무료)

```python
# Alpha Vantage - 전문 금융 데이터 API
# https://www.alphavantage.co/

import requests

API_KEY = "발급받은_API_키"  # 무료 신청

def get_stock_price(symbol):
    url = f"https://www.alphavantage.co/query"
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": symbol,
        "apikey": API_KEY
    }
    response = requests.get(url, params=params)
    return response.json()

# 사용 예시
data = get_stock_price("AAPL")
print(data)
```

**특징:**
- ✅ 무료 (일 25회 제한)
- ✅ 실시간
- ✅ 공식 API
- ⚠️ API 키 필요 (무료 신청)

**신청 방법:**
1. https://www.alphavantage.co/support/#api-key 접속
2. 이메일 입력 → API 키 발급
3. 일 25회 무료 사용 (유료 플랜도 있음)

---

### 방법 3: IEX Cloud API (✅ 무료)

```python
# IEX Cloud - 미국 주식 데이터 전문
# https://iexcloud.io/

import requests

API_TOKEN = "발급받은_토큰"

def get_stock_quote(symbol):
    url = f"https://cloud.iexapis.com/stable/stock/{symbol}/quote"
    params = {"token": API_TOKEN}
    response = requests.get(url, params=params)
    return response.json()

# 사용 예시
quote = get_stock_quote("AAPL")
print(f"가격: ${quote['latestPrice']}")
```

**특징:**
- ✅ 무료 (월 50,000 크레딧)
- ✅ 실시간
- ✅ 공식 API
- ⚠️ 회원가입 필요

---

## 🎯 Decision Stream 통합 권장 방법

### 한국 주식 (추천 순서)

#### 1순위: 한국투자증권 Open API
```python
# backend/services/kr_stock_service.py

import requests
import os

class KoreaInvestmentAPI:
    def __init__(self):
        self.app_key = os.getenv('KIS_APP_KEY')
        self.app_secret = os.getenv('KIS_APP_SECRET')
        self.base_url = "https://openapi.koreainvestment.com:9443"
        self.token = None
    
    def get_token(self):
        url = f"{self.base_url}/oauth2/tokenP"
        data = {
            "grant_type": "client_credentials",
            "appkey": self.app_key,
            "appsecret": self.app_secret
        }
        response = requests.post(url, json=data)
        self.token = response.json()['access_token']
        return self.token
    
    def get_current_price(self, ticker):
        if not self.token:
            self.get_token()
        
        url = f"{self.base_url}/uapi/domestic-stock/v1/quotations/inquire-price"
        headers = {
            "authorization": f"Bearer {self.token}",
            "appkey": self.app_key,
            "appsecret": self.app_secret,
            "tr_id": "FHKST01010100"
        }
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": ticker
        }
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        
        return {
            'ticker': ticker,
            'price': float(data['output']['stck_prpr']),
            'change': float(data['output']['prdy_ctrt']),
            'volume': int(data['output']['acml_vol'])
        }

# 사용
api = KoreaInvestmentAPI()
price = api.get_current_price('005930')
print(price)
```

#### 2순위: HTS CSV 다운로드 (수동)
```python
# tools/convert_hts_prices.py (이미 구현됨)

import pandas as pd

def load_kiwoom_prices(file_path):
    """
    키움 HTS에서 다운로드한 CSV 읽기
    """
    df = pd.read_csv(file_path, encoding='cp949')
    df.columns = ['date', 'open', 'high', 'low', 'close', 'volume']
    return df

# 사용
df = load_kiwoom_prices('data/hts_raw/prices/005930.csv')
```

#### 3순위: FinanceDataReader
```python
# backend/services/fdr_service.py

import FinanceDataReader as fdr

def get_stock_data(ticker, start_date, end_date):
    df = fdr.DataReader(ticker, start_date, end_date)
    return df.to_dict('records')

# 사용
data = get_stock_data('005930', '2024-01-01', '2024-01-21')
```

---

### 미국 주식 (추천 순서)

#### 1순위: yfinance
```python
# backend/services/us_stock_service.py

import yfinance as yf

def get_us_stock_price(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    
    return {
        'ticker': ticker,
        'price': info.get('currentPrice', 0),
        'change': info.get('regularMarketChangePercent', 0),
        'volume': info.get('volume', 0)
    }

# 사용
price = get_us_stock_price('AAPL')
print(price)
```

#### 2순위: Alpha Vantage
```python
# backend/services/alpha_vantage_service.py

import requests
import os

class AlphaVantageAPI:
    def __init__(self):
        self.api_key = os.getenv('ALPHA_VANTAGE_KEY')
        self.base_url = "https://www.alphavantage.co/query"
    
    def get_quote(self, symbol):
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": self.api_key
        }
        response = requests.get(self.base_url, params=params)
        data = response.json()['Global Quote']
        
        return {
            'ticker': symbol,
            'price': float(data['05. price']),
            'change': float(data['10. change percent'].replace('%', '')),
            'volume': int(data['06. volume'])
        }
```

---

## 🔧 Decision Stream 통합 예시

### FastAPI 서버에 실시간 가격 엔드포인트 추가

```python
# backend/server.py

from fastapi import FastAPI, Query
from services.kr_stock_service import KoreaInvestmentAPI
from services.us_stock_service import get_us_stock_price

app = FastAPI()

kr_api = KoreaInvestmentAPI()

@app.get("/price/{ticker}")
def get_stock_price(
    ticker: str,
    market: str = Query(..., description="KR or US"),
    key: str = Query(...)
):
    """
    실시간 주가 조회
    """
    verify_key(key)
    
    if market == "KR":
        return kr_api.get_current_price(ticker)
    elif market == "US":
        return get_us_stock_price(ticker)
    else:
        raise HTTPException(status_code=400, detail="Invalid market")

# 사용 예시:
# GET /price/005930?market=KR&key=ds-test-2026
# GET /price/AAPL?market=US&key=ds-test-2026
```

### 프론트엔드에서 실시간 가격 업데이트

```javascript
// trade_plan_simulation.html

async function updateRealTimePrice(ticker, market) {
    const response = await fetch(
        `http://127.0.0.1:8125/price/${ticker}?market=${market}&key=ds-test-2026`
    );
    const data = await response.json();
    
    // 현재가 업데이트
    document.getElementById('current-price').value = data.price;
    
    return data;
}

// 사용
updateRealTimePrice('005930', 'KR');
```

---

## 📋 데이터 수집 비교표

| 방법 | 한국 주식 | 미국 주식 | 실시간 | 무료 | 합법성 |
|------|-----------|-----------|--------|------|--------|
| **HTS CSV** | ✅ | ❌ | ❌ | ✅ | ✅✅✅ |
| **한국투자증권 API** | ✅ | ❌ | ✅ | ✅ (500회/일) | ✅✅✅ |
| **FinanceDataReader** | ✅ | ✅ | ❌ | ✅ | ✅✅✅ |
| **yfinance** | ❌ | ✅ | ⚠️ (15분 지연) | ✅ | ✅✅✅ |
| **Alpha Vantage** | ❌ | ✅ | ✅ | ✅ (25회/일) | ✅✅✅ |
| **IEX Cloud** | ❌ | ✅ | ✅ | ✅ (50K/월) | ✅✅✅ |

---

## 🎯 최종 추천 방안

### Decision Stream 프로젝트용

```
한국 주식:
1. 일상 운용: HTS CSV 다운로드 (월 1회, 안전)
2. 실시간 필요 시: 한국투자증권 Open API (무료 500회)

미국 주식:
1. 일상 운용: yfinance (완전 무료)
2. 실시간 필요 시: Alpha Vantage (무료 25회)

통합:
- 백엔드 서버에 두 API 모두 통합
- 프론트엔드에서 필요할 때만 호출
- 대부분은 목업 데이터 사용 (개발/학습용)
```

---

## ⚠️ 주의사항

### 법적 리스크 회피
1. ✅ **공식 API 사용** (가장 안전)
2. ✅ **약관 준수** (호출 제한 지키기)
3. ✅ **재배포 금지 데이터 확인**
4. ❌ **무단 크롤링 금지**
5. ❌ **API 키 공개 금지** (환경변수 사용)

### API 키 관리

```bash
# .env 파일 (절대 Git에 커밋하지 말 것!)
KIS_APP_KEY=your_korea_investment_app_key
KIS_APP_SECRET=your_korea_investment_secret
ALPHA_VANTAGE_KEY=your_alpha_vantage_key
IEX_TOKEN=your_iex_token
```

```python
# backend/server.py
import os
from dotenv import load_dotenv

load_dotenv()

KIS_APP_KEY = os.getenv('KIS_APP_KEY')
```

---

## 📞 다음 단계

1. **한국투자증권 API 신청** (무료)
   - https://apiportal.koreainvestment.com/
   
2. **Alpha Vantage API 키 발급** (무료)
   - https://www.alphavantage.co/support/#api-key

3. **백엔드 서버에 통합**
   - `backend/services/` 디렉토리에 서비스 추가
   - FastAPI 엔드포인트 구현

4. **프론트엔드 연동**
   - 실시간 가격 업데이트 기능 추가

**합법적이고 안전하게 데이터를 수집하세요! 📊✅**
