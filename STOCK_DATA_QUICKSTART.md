# 📊 주식 시세 수집 완료 - 빠른 시작 가이드

## ✅ 준비 완료 사항

1. ✅ **한국 주식 데이터 수집 서비스** (`backend/services/nh_investment_api.py`)
2. ✅ **미국 주식 데이터 수집 서비스** (`backend/services/us_stock_service.py`)
3. ✅ **상세 가이드 문서** (`STOCK_DATA_COLLECTION_GUIDE.md`)
4. ✅ **requirements.txt 업데이트**

---

## 🚀 즉시 시작 (가장 쉬운 방법)

### Step 1: yfinance로 미국 주식 시작 (설정 불필요!)

```bash
# 패키지 설치
cd backend
pip install -r requirements.txt

# 테스트
python services/us_stock_service.py
```

**결과:**
```
==================================================
예제 1: Apple 현재가 조회 (yfinance)
==================================================
종목명: Apple Inc.
현재가: $185.50
등락률: +1.20%
거래량: 45,678,900주
시가총액: $2,900,000,000,000
```

---

### Step 2: NH투자증권 API 신청 (무료)

1. **회원가입**
   - https://securities.nhqv.com 접속
   - 회원가입 및 API 신청

2. **API 신청**
   - 로그인 → "API 신청" 메뉴
   - "앱 등록" → 앱 이름 입력 (예: Decision Stream)
   - **앱 키(App Key)** 및 **앱 시크릿(App Secret)** 발급

3. **환경변수 설정**
```bash
# backend/.env 파일 생성
NH_APP_KEY=발급받은_앱_키_입력
NH_APP_SECRET=발급받은_앱_시크릿_입력
```

4. **테스트**
```bash
cd backend
python services/nh_investment_api.py
```

**결과:**
```
==================================================
예제 1: 삼성전자 현재가 조회
==================================================
종목명: 삼성전자
현재가: 75,000원
등락률: +1.50%
거래량: 12,345,678주
```

---

## 📋 무료 API 신청 링크

| API | 신청 링크 | 무료 한도 | 실시간 |
|-----|-----------|----------|--------|
| **NH투자증권** | https://securities.nhqv.com | 요청시 확인 | ✅ |
| **yfinance** | 설치만 하면 됨 | 무제한 | ⚠️ (15분 지연) |
| **Alpha Vantage** | https://www.alphavantage.co/support/#api-key | 25회/일 | ✅ |
| **IEX Cloud** | https://iexcloud.io/console/ | 50,000/월 | ✅ |

---

## 🎯 Decision Stream 통합 방법

### 방법 1: FastAPI 서버에 엔드포인트 추가

```python
# backend/server.py

from services.nh_investment_api import NHInvestmentAPI
from services.us_stock_service import USStockService

# 인스턴스 생성
kr_api = NHInvestmentAPI()
us_service = USStockService()

@app.get("/api/price/{ticker}")
def get_real_time_price(
    ticker: str,
    market: str = Query(..., description="KR or US"),
    key: str = Query(...)
):
    """
    실시간 주가 조회
    """
    verify_key(key)
    
    try:
        if market == "KR":
            data = kr_api.get_current_price(ticker)
        elif market == "US":
            data = us_service.get_current_price(ticker)
        else:
            raise HTTPException(400, "Invalid market")
        
        return data
    except Exception as e:
        raise HTTPException(500, str(e))
```

### 방법 2: 프론트엔드에서 호출

```javascript
// trade_plan_simulation.html

async function updateRealTimePrice(ticker, market) {
    try {
        const response = await fetch(
            `http://127.0.0.1:8125/api/price/${ticker}?market=${market}&key=ds-test-2026`
        );
        const data = await response.json();
        
        // UI 업데이트
        document.getElementById('current-price').value = data.price;
        document.getElementById('price-change').textContent = 
            `${data.change > 0 ? '+' : ''}${data.change.toFixed(2)}%`;
        
        return data;
    } catch (error) {
        console.error('가격 조회 실패:', error);
        alert('실시간 가격 조회에 실패했습니다.');
    }
}

// 종목 선택 시 자동 호출
document.getElementById('stock').addEventListener('change', function() {
    const ticker = this.value;
    const market = document.querySelector('input[name="market"]:checked').value;
    
    if (ticker) {
        updateRealTimePrice(ticker, market);
    }
});
```

---

## 🧪 테스트 시나리오

### 시나리오 1: 한국 주식 (한화에어로스페이스)

```bash
# backend/services/nh_investment_api.py 실행
python services/nh_investment_api.py
```

**예상 결과:**
```
한화에어로스페이스: 185,000원 (+2.50%)
```

### 시나리오 2: 미국 주식 (Lockheed Martin)

```bash
# backend/services/us_stock_service.py 실행
python services/us_stock_service.py
```

**예상 결과:**
```
LMT: $445.50 (+1.20%)
```

### 시나리오 3: 방산 섹터 일괄 조회

```python
# 한국 방산
kr_defense = ['012450', '079550', '272210']
for ticker in kr_defense:
    data = kr_api.get_current_price(ticker)
    print(f"{data['name']}: {data['price']:,}원")

# 미국 방산
us_defense = ['LMT', 'RTX', 'BA', 'NOC', 'GD']
prices = us_service.get_multiple_prices(us_defense)
for ticker, data in prices.items():
    print(f"{ticker}: ${data['price']:.2f}")
```

---

## ⚠️ 중요: API 키 보안

### .env 파일 사용 (필수!)

```bash
# backend/.env
NH_APP_KEY=your_nh_app_key
NH_APP_SECRET=your_nh_app_secret
ALPHA_VANTAGE_KEY=your_alpha_vantage_key  # 선택사항
```

### .gitignore 추가

```bash
# backend/.gitignore에 추가
.env
*.env
__pycache__/
*.pyc
```

### ⚠️ 절대 하지 말 것
- ❌ API 키를 코드에 직접 입력
- ❌ .env 파일을 Git에 커밋
- ❌ API 키를 공개 저장소에 업로드

---

## 📊 데이터 수집 전략 (권장)

### 일상 운용 (Decision Stream 프로젝트)

```
1. 기본 데이터 (목업):
   - 개발/학습용으로 충분
   - 시뮬레이션 연습에 사용

2. 실시간 필요 시:
   - 한국: 한국투자증권 API (500회/일)
   - 미국: yfinance (무제한)

3. 월간 스크리너:
   - HTS CSV 다운로드 (수동, 월 1회)
   - 정확하고 안전함
```

---

## 🎓 학습 순서

### Week 1: yfinance로 시작
```bash
# 설치
pip install yfinance

# 테스트
python services/us_stock_service.py
```

### Week 2: 한국투자증권 API 신청
1. 회원가입
2. API 신청
3. 환경변수 설정
4. 테스트

### Week 3: Decision Stream 통합
1. FastAPI 엔드포인트 추가
2. 프론트엔드 연동
3. 실시간 가격 업데이트 기능

### Week 4: 월간 스크리너 + HTS CSV
1. HTS에서 CSV 다운로드
2. 변환 스크립트 실행
3. 스크리너 실행

---

## 📞 다음 단계

### 즉시 실행 가능
```bash
# 1. 패키지 설치
cd backend
pip install -r requirements.txt

# 2. 미국 주식 테스트 (API 키 불필요)
python services/us_stock_service.py

# 3. NH투자증권 API 신청
# https://securities.nhqv.com

# 4. 환경변수 설정
echo "NH_APP_KEY=발급받은_키" > .env
echo "NH_APP_SECRET=발급받은_시크릿" >> .env

# 5. 한국 주식 테스트
python services/nh_investment_api.py
```

---

## 📚 추가 학습 자료

- **상세 가이드**: STOCK_DATA_COLLECTION_GUIDE.md
- **NH투자증권 API 문서**: https://securities.nhqv.com
- **yfinance 문서**: https://github.com/ranaroussi/yfinance
- **Alpha Vantage 문서**: https://www.alphavantage.co/documentation/

---

**합법적이고 안전하게 주식 데이터를 수집하세요! 📊✅**

**무료로 시작할 수 있으며, Decision Stream에 즉시 통합 가능합니다!**
