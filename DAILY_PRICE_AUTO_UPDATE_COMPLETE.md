# ✅ 매일 오후 6시 주가 자동 업데이트 시스템 - 구현 완료!

## 🎉 완료 요약

**매일 오후 6시 (18:00) 자동으로 모든 종목의 종가를 업데이트하는 시스템이 완성되었습니다!**

---

## 📋 구현 내역

### 1. 백엔드 스케줄러 (`backend/scheduler.py`)
- ✅ APScheduler를 사용한 자동화
- ✅ 매일 오후 6시 실행
- ✅ 한국투자증권 API 연동 (한국 주식 19개)
- ✅ Yahoo Finance API 연동 (미국 주식 2개)
- ✅ `stock_prices.json` 파일 자동 생성

### 2. 서버 통합 (`backend/server.py`)
- ✅ 서버 시작 시 스케줄러 자동 시작
- ✅ 수동 업데이트 API 추가: `POST /api/prices/refresh`

### 3. 프론트엔드 (`trade_plan_simulation.html`)
- ✅ `stock_prices.json` 자동 로드
- ✅ STOCK_DATABASE 자동 업데이트
- ✅ 헤더에 업데이트 시간 표시

### 4. 의존성 (`backend/requirements.txt`)
- ✅ apscheduler==3.10.4 추가

---

## 🚀 사용 방법

### Step 1: 패키지 설치
```bash
cd backend
pip install -r requirements.txt
```

**설치되는 패키지:**
- `apscheduler==3.10.4` (스케줄러)
- `yfinance==0.2.35` (미국 주식)
- `python-dotenv==1.0.0` (환경변수)
- `requests==2.31.0` (한국투자증권 API)

---

### Step 2: 환경변수 설정 (.env 파일)

```bash
# backend/.env

# 한국투자증권 API (필수)
KIS_APP_KEY=your_kis_app_key_here
KIS_APP_SECRET=your_kis_app_secret_here

# Alpha Vantage (선택, 실시간 미국 주식)
ALPHA_VANTAGE_KEY=your_alpha_vantage_key_here
```

**한국투자증권 API 발급:**
1. https://apiportal.koreainvestment.com/ 회원가입
2. API 신청 → 앱 키 발급
3. `.env` 파일에 추가

---

### Step 3: 서버 실행

```bash
cd backend
python server.py
```

**출력 예시:**
```
🚀 서버 시작 중...
✅ 한국투자증권 API 초기화 완료
✅ 미국 주식 서비스 초기화 완료

============================================================
🕐 스케줄러 시작됨
⏰ 실행 시간: 매일 오후 6시 (18:00)
📊 대상 종목:
   - 미국 주식: 2개
   - 한국 주식: 19개
   - 총 21개 종목
============================================================

✅ 스케줄러 초기화 완료

INFO:     Uvicorn running on http://127.0.0.1:8125
INFO:     Application startup complete.
```

---

### Step 4: 수동 업데이트 (선택, 테스트용)

#### 방법 1: Python 스크립트
```bash
cd backend
python -c "from scheduler import manual_update; manual_update()"
```

#### 방법 2: API 호출
```bash
curl -X POST "http://127.0.0.1:8125/api/prices/refresh?key=ds-test-2026"
```

**출력 예시:**
```
============================================================
[2026-01-21 18:00:00] 주가 업데이트 시작
============================================================

📊 미국 주식 조회 중...
  ✅ Lockheed Martin                  (LMT   ):    $581.25
  ✅ Johnson & Johnson                (JNJ   ):    $215.50

📊 한국 주식 조회 중...
  ✅ 한화에어로스페이스              (012450):    ₩185,300
  ✅ LIG넥스원                       (079550):    ₩544,500
  ✅ 삼성전자                        (005930):     ₩75,200
  ✅ SK하이닉스                      (000660):    ₩142,500
  ... (총 19개)

============================================================
📁 저장 위치: /path/to/stock_prices.json
✅ 성공: 21개
[2026-01-21 18:00:15] 주가 업데이트 완료!
============================================================
```

---

## 📊 stock_prices.json 예시

```json
{
  "lastUpdate": "2026-01-21T18:00:00.123456",
  "updateTime": "2026-01-21 18:00:00",
  "totalStocks": 21,
  "successCount": 21,
  "failCount": 0,
  "prices": {
    "LMT": 581.25,
    "JNJ": 215.5,
    "012450": 185300,
    "079550": 544500,
    "005930": 75200,
    "000660": 142500,
    "207940": 851000,
    "068270": 175800,
    "373220": 451000,
    "096770": 145500,
    "051910": 380500,
    "326030": 92200,
    "005380": 235500,
    "000270": 98200,
    "012330": 265500,
    "009830": 42100,
    "011170": 145200,
    "009540": 145300,
    "010140": 9850,
    "042660": 31100,
    "042700": 85200
  }
}
```

---

## 🎨 프론트엔드 동작

### 1. 페이지 로드 시
```javascript
// 1. stock_prices.json 파일 자동 로드
const prices = await loadStockPrices();

// 2. STOCK_DATABASE 업데이트
STOCK_DATABASE['방산'][0].price = prices['LMT'];  // $581.25

// 3. 헤더에 업데이트 시간 표시
"📊 주가: 2026-01-21 18:00:00"
```

### 2. 종목 선택 시
```javascript
// 업데이트된 최신 주가가 자동으로 입력됨
LMT 선택 → 현재 주가: 581.25
```

---

## 📁 파일 구조

```
decision-stream/
├── backend/
│   ├── server.py              ✅ 스케줄러 통합
│   ├── scheduler.py           ✅ 새로 생성
│   ├── requirements.txt       ✅ apscheduler 추가
│   ├── .env                   ⚠️  API 키 설정 필요
│   └── services/
│       ├── korea_investment_api.py  ✅ 이미 존재
│       └── us_stock_service.py      ✅ 이미 존재
├── stock_prices.json          ✅ 자동 생성 (매일 6시)
├── trade_plan_simulation.html ✅ JSON 로더 추가
└── DAILY_PRICE_AUTO_UPDATE_COMPLETE.md  ✅ 이 파일
```

---

## ⚙️ 설정 커스터마이징

### 업데이트 시간 변경
```python
# backend/scheduler.py

# 매일 오후 7시로 변경
scheduler.add_job(
    update_stock_prices,
    'cron',
    hour=19,  # 변경
    minute=0,
    id='daily_price_update'
)

# 매일 오전 9시와 오후 6시 (하루 2회)
scheduler.add_job(update_stock_prices, 'cron', hour=9, minute=0)
scheduler.add_job(update_stock_prices, 'cron', hour=18, minute=0)
```

### 종목 추가/제거
```python
# backend/scheduler.py

STOCK_LIST = {
    "US": [
        {"ticker": "LMT", "name": "Lockheed Martin"},
        {"ticker": "JNJ", "name": "Johnson & Johnson"},
        {"ticker": "AAPL", "name": "Apple"},  # 새로 추가
    ],
    "KR": [
        # ... 기존 종목
        {"ticker": "035720", "name": "카카오"},  # 새로 추가
    ]
}
```

---

## 🔍 테스트 방법

### Test 1: 스케줄러 즉시 실행
```bash
cd backend
python scheduler.py
```

**예상 결과:**
- 모든 종목 주가 조회
- `stock_prices.json` 파일 생성
- 성공/실패 개수 출력

### Test 2: 프론트엔드 확인
1. `backend/server.py` 실행
2. `trade_plan_simulation.html` 열기
3. 헤더 우측 확인: "📊 주가: 2026-01-21 18:00:00"
4. F12 콘솔 확인:
   ```
   ✅ 주가 데이터 로드 완료 (업데이트: 2026-01-21 18:00:00)
      - 성공: 21개, 실패: 0개
   📈 Lockheed Martin (LMT): 497 → 581.25
   📈 LIG넥스원 (079550): 95000 → 544500
   ✅ 21개 종목 주가 업데이트 완료
   ```

### Test 3: API 수동 호출
```bash
# Postman 또는 curl로 테스트
curl -X POST "http://127.0.0.1:8125/api/prices/refresh?key=ds-test-2026"
```

---

## ⚠️ 주의사항

### 1. API 키 필수
- `.env` 파일에 `KIS_APP_KEY`, `KIS_APP_SECRET` 설정 필요
- 없으면 한국 주식 조회 실패

### 2. 장 마감 시간
- 한국 주식: 15:30 마감 → 오후 6시면 당일 종가
- 미국 주식: 06:00 마감 (한국 시간) → 전일 종가

### 3. API 호출 제한
- 한국투자증권: 분당 20회 제한
- Yahoo Finance: 무제한 (무료)
- Alpha Vantage: 25회/일 (무료 플랜)

### 4. 에러 처리
- API 호출 실패 시에도 서버는 계속 실행
- 실패한 종목은 로그에 표시
- JSON 파일에는 성공한 종목만 저장

---

## 📊 주가 데이터 흐름

```
매일 18:00
    ↓
[스케줄러 실행]
    ↓
┌─────────────────┐    ┌──────────────────┐
│한국투자증권 API  │    │Yahoo Finance API │
│(한국 주식 19개)  │    │(미국 주식 2개)    │
└────────┬────────┘    └────────┬─────────┘
         │                       │
         └───────────┬───────────┘
                     ↓
         ┌─────────────────────┐
         │ stock_prices.json   │
         │ (프로젝트 루트)      │
         └──────────┬──────────┘
                    │
                    ↓
         ┌─────────────────────┐
         │ 프론트엔드 로드       │
         │ (페이지 열릴 때)     │
         └──────────┬──────────┘
                    │
                    ↓
         ┌─────────────────────┐
         │ STOCK_DATABASE      │
         │ 자동 업데이트        │
         └─────────────────────┘
```

---

## 🎉 완료된 기능

✅ **매일 오후 6시 자동 실행**  
✅ **한국투자증권 API 연동** (한국 주식 19개)  
✅ **Yahoo Finance API 연동** (미국 주식 2개)  
✅ **JSON 파일 자동 생성**  
✅ **프론트엔드 자동 로드**  
✅ **헤더에 업데이트 시간 표시**  
✅ **수동 업데이트 API** (`/api/prices/refresh`)  
✅ **에러 처리 및 로깅**  

---

## 💡 추가 개선 아이디어 (선택)

### 1. 업데이트 히스토리
```json
{
  "history": [
    {"date": "2026-01-21", "success": 21, "failed": 0},
    {"date": "2026-01-20", "success": 21, "failed": 0}
  ]
}
```

### 2. 프론트엔드 새로고침 버튼
```html
<button onclick="refreshPrices()">🔄 주가 새로고침</button>
```

### 3. 웹소켓 실시간 푸시
- 주가 업데이트 시 브라우저에 자동 반영
- 페이지 새로고침 불필요

### 4. 가격 변동 알림
- 특정 종목 가격이 목표가 도달 시 알림
- 이메일 또는 텔레그램 연동

---

## 🚀 다음 단계

1. **서버 실행:**
   ```bash
   cd backend
   python server.py
   ```

2. **프론트엔드 테스트:**
   - `trade_plan_simulation.html` 열기
   - 헤더에 "📊 주가: 2026-01-21 18:00:00" 확인
   - 종목 선택 시 최신 주가 자동 입력 확인

3. **운영:**
   - 서버를 계속 실행 상태로 유지
   - 매일 오후 6시에 자동으로 주가 업데이트
   - 필요 시 수동 업데이트 API 호출

---

## 📞 문제 해결

### Q: stock_prices.json 파일이 생성되지 않아요
**A:** 
1. 서버가 실행 중인지 확인
2. `.env` 파일에 API 키가 설정되었는지 확인
3. 수동 업데이트 실행: `python -c "from scheduler import manual_update; manual_update()"`

### Q: 한국 주식만 조회되고 미국 주식이 안 돼요
**A:**
- Yahoo Finance API는 인터넷 연결 필요
- 방화벽 확인
- yfinance 패키지 재설치: `pip install --upgrade yfinance`

### Q: 스케줄러가 6시에 실행되지 않아요
**A:**
1. 서버가 계속 실행 중인지 확인 (종료하면 스케줄러도 멈춤)
2. 시스템 시간 확인
3. 로그 확인: 스케줄러 시작 메시지가 출력되었는지

---

## 🎊 결론

**매일 오후 6시 자동 주가 업데이트 시스템이 완성되었습니다!**

- ✅ 한국투자증권 + Yahoo Finance API
- ✅ 완전 자동화 (매일 18:00)
- ✅ 중기 스윙 투자에 최적화
- ✅ 서버 부하 최소화
- ✅ 사용자 경험 향상

---

> **최종 업데이트:** 2026-01-21  
> **작성자:** Decision Stream Development Team  
> **상태:** ✅ 구현 완료 / 테스트 대기
