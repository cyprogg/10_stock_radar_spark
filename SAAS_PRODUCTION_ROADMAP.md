# 🚀 SaaS 상용화 로드맵

## 현재 상태 (MVP)
- ✅ AI Agent 시스템 (5개 Agent)
- ✅ Yahoo Finance 실시간 데이터
- ✅ 한국/미국 주식 지원
- ✅ 기본 대시보드 UI
- ⚠️ 단일 API Key (ds-test-2026)
- ⚠️ 무료 무제한 사용
- ⚠️ 사용자 구분 없음

---

## 📋 Phase 1: 사용자 관리 (2-3주)

### 1.1 인증 시스템
**목표**: 회원가입, 로그인, 세션 관리

**구현 옵션**:
- **Option A (권장)**: Supabase Auth (무료 50,000 MAU)
  - 이메일/비밀번호, 소셜 로그인 (Google, GitHub)
  - 자동 이메일 인증
  - JWT 토큰 기반
  
- **Option B**: Firebase Auth
- **Option C**: Auth0 (월 $25 부터)

**작업**:
```javascript
// 1. Supabase 프로젝트 생성
// 2. backend/auth.py 생성
from supabase import create_client

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.post("/api/auth/signup")
def signup(email: str, password: str):
    result = supabase.auth.sign_up({
        "email": email,
        "password": password
    })
    return result

@app.post("/api/auth/login")
def login(email: str, password: str):
    result = supabase.auth.sign_in_with_password({
        "email": email,
        "password": password
    })
    return result
```

**체크리스트**:
- [ ] 회원가입 페이지 (signup.html)
- [ ] 로그인 페이지 (login.html)
- [ ] JWT 미들웨어 구현
- [ ] 비밀번호 재설정 기능
- [ ] 이메일 인증 기능

---

### 1.2 사용자 프로필 DB
**목표**: 사용자별 설정, 구독 상태, 사용량 추적

**DB 스키마** (PostgreSQL):
```sql
-- users 테이블 (Supabase Auth 자동 생성)
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email VARCHAR(255) UNIQUE NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  last_login TIMESTAMP
);

-- user_profiles 테이블
CREATE TABLE user_profiles (
  id UUID PRIMARY KEY REFERENCES users(id),
  full_name VARCHAR(255),
  company VARCHAR(255),
  subscription_tier VARCHAR(50) DEFAULT 'free',  -- free, basic, pro
  api_key VARCHAR(255) UNIQUE NOT NULL,
  api_calls_today INTEGER DEFAULT 0,
  api_calls_month INTEGER DEFAULT 0,
  credits_remaining INTEGER DEFAULT 100,  -- 무료 크레딧
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- usage_logs 테이블
CREATE TABLE usage_logs (
  id SERIAL PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  endpoint VARCHAR(255),
  request_time TIMESTAMP DEFAULT NOW(),
  response_time_ms INTEGER,
  status_code INTEGER
);
```

**체크리스트**:
- [ ] PostgreSQL DB 생성 (Railway or Supabase)
- [ ] 테이블 생성 스크립트
- [ ] API Key 자동 생성 로직
- [ ] 사용량 추적 미들웨어

---

## 📋 Phase 2: 구독 & 결제 (2-3주)

### 2.1 가격 정책 설계
**권장 티어**:

| Tier | 가격 | API 호출 | 기능 |
|------|------|----------|------|
| **Free** | ₩0 | 100/월 | 기본 Market Regime, 1개 섹터 |
| **Basic** | ₩29,000/월 | 1,000/월 | 모든 API, 5개 섹터, 이메일 지원, **알림 10개** |
| **Pro** | ₩99,000/월 | 10,000/월 | 무제한 섹터, **무제한 알림**, Slack/Webhook, 우선 지원 |
| **Enterprise** | 협의 | 무제한 | 전용 서버, SLA 99.9%, 커스텀 알림 |

**참고**: 경쟁사 가격
- TradingView Pro: $14.95/월 (~₩20,000)
- Investing.com Premium: $29.99/월 (~₩40,000)

---

### 2.2 결제 시스템 통합
**Option A: Stripe (권장)**
```bash
pip install stripe
```

```python
# backend/payments.py
import stripe

stripe.api_key = STRIPE_SECRET_KEY

@app.post("/api/subscribe")
async def create_subscription(user_id: str, tier: str):
    # Stripe Checkout Session 생성
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': PRICE_IDS[tier],  # Stripe Dashboard에서 생성
            'quantity': 1,
        }],
        mode='subscription',
        success_url='https://your-domain.com/success',
        cancel_url='https://your-domain.com/cancel',
        client_reference_id=user_id
    )
    return {"checkout_url": session.url}

@app.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    # Stripe Webhook 처리 (구독 성공/취소)
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    
    event = stripe.Webhook.construct_event(
        payload, sig_header, STRIPE_WEBHOOK_SECRET
    )
    
    if event['type'] == 'checkout.session.completed':
        # 구독 활성화
        session = event['data']['object']
        user_id = session['client_reference_id']
        # DB 업데이트: subscription_tier = 'pro'
    
    return {"status": "ok"}
```

**Option B: Toss Payments (한국 전용)**
- 한국 사용자만 대상이면 고려
- 카카오페이, 네이버페이, 토스 등 지원

**체크리스트**:
- [ ] Stripe 계정 생성
- [ ] 가격 상품 생성 (Dashboard)
- [ ] Checkout 페이지 구현
- [ ] Webhook 처리 구현
- [ ] 구독 관리 페이지 (결제 내역, 취소)

---

## 📋 Phase 3: API Rate Limiting & 보안 (1주)

### 3.1 Rate Limiting 구현
**목표**: 무료 사용자는 API 호출 제한

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.get("/api/agent/market-regime")
@limiter.limit("10/minute")  # 분당 10회
async def market_regime(request: Request):
    # 사용자 구독 정보 확인
    user = get_current_user(request)
    
    if user.subscription_tier == 'free':
        if user.api_calls_month >= 100:
            return JSONResponse(
                status_code=429,
                content={"error": "Monthly limit exceeded. Upgrade to continue."}
            )
    
    # API 로직
    user.api_calls_month += 1
    save_user(user)
    
    return {"state": "RISK_ON", ...}
```

**티어별 제한**:
```python
RATE_LIMITS = {
    "free": "10/minute",      # 시간당 600회
    "basic": "100/minute",    # 시간당 6,000회
    "pro": "1000/minute",     # 사실상 무제한
    "enterprise": None        # 제한 없음
}
```

**체크리스트**:
- [ ] slowapi 또는 redis 기반 Rate Limiter 구현
- [ ] 사용자별 월간 호출 횟수 추적
- [ ] 429 에러 응답 (UI에서 업그레이드 유도)
- [ ] 관리자 대시보드 (사용량 모니터링)

---

### 3.2 보안 강화
**현재 문제점**:
- ❌ 단일 API Key (`ds-test-2026`) - 누구나 사용 가능
- ❌ CORS 무제한 (`allow_origins=["*"]`)
- ❌ HTTPS 미적용 (로컬)

**해결책**:
```python
# 1. 사용자별 API Key (UUID)
import uuid

def generate_api_key():
    return f"ds_{uuid.uuid4().hex}"

# 2. API Key 검증 미들웨어
@app.middleware("http")
async def verify_api_key(request: Request, call_next):
    api_key = request.headers.get("X-API-Key")
    
    user = get_user_by_api_key(api_key)
    if not user:
        return JSONResponse(status_code=401, content={"error": "Invalid API key"})
    
    request.state.user = user
    return await call_next(request)

# 3. CORS 화이트리스트
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-domain.com",
        "https://www.your-domain.com"
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["X-API-Key"]
)
```

**HTTPS 적용**:
- Railway/Vercel 자동 제공 (Let's Encrypt)
- 커스텀 도메인 추가: `api.your-domain.com`

**체크리스트**:
- [ ] 사용자별 API Key 생성
- [ ] API Key 검증 미들웨어
- [ ] CORS 화이트리스트
- [ ] HTTPS 강제 (HTTP → HTTPS 리다이렉트)
- [ ] 민감 정보 환경 변수 이동 (.env)

---

## 📋 Phase 4: 모니터링 & 로깅 (1주)

### 4.1 에러 추적
**Sentry 통합** (권장):
```bash
pip install sentry-sdk[fastapi]
```

```python
import sentry_sdk

sentry_sdk.init(
    dsn="https://your-sentry-dsn@sentry.io/project-id",
    traces_sample_rate=1.0,
    environment="production"
)

# 자동으로 에러 캡처 & 알림
```

**대안**:
- **Rollbar**
- **Bugsnag**
- 직접 구현 (Slack Webhook)

**체크리스트**:
- [ ] Sentry 프로젝트 생성
- [ ] FastAPI 통합
- [ ] 에러 알림 설정 (Slack/Email)

---

### 4.2 성능 모니터링
**Grafana + Prometheus**:
```bash
pip install prometheus-fastapi-instrumentator
```

```python
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)

# /metrics 엔드포인트 생성 (Prometheus가 수집)
```

**체크리스트**:
- [ ] Prometheus 설치 (Railway Add-on)
- [ ] Grafana 대시보드 생성
- [ ] 알림 규칙 설정 (응답 시간 > 2초, 에러율 > 5%)

---

### 4.3 사용자 행동 추적
**Mixpanel or PostHog** (권장):
```javascript
// 프론트엔드에서 이벤트 추적
mixpanel.track('Market Regime Viewed', {
  user_id: user.id,
  tier: user.subscription_tier,
  regime_state: 'RISK_ON'
});

mixpanel.track('Stock Clicked', {
  ticker: 'AAPL',
  sector: '반도체'
});
```

**추적할 이벤트**:
- 페이지 뷰
- API 호출 (성공/실패)
- 기능 사용 (섹터 클릭, 종목 선택)
- 결제 전환율 (Free → Basic → Pro)

**체크리스트**:
- [ ] Mixpanel/PostHog 프로젝트 생성
- [ ] 주요 이벤트 정의
- [ ] 프론트엔드 통합
- [ ] Funnel 분석 (회원가입 → 결제)

---

## 📋 Phase 5: 인프라 최적화 (2주)

### 5.1 데이터베이스 최적화
**현재**: Yahoo Finance API를 매번 호출 (느림, 비용)

**개선안**: 캐싱 + DB 저장
```python
# Redis 캐싱 (1분)
import redis

redis_client = redis.Redis(host='localhost', port=6379)

@app.get("/api/chart/{ticker}")
def get_chart(ticker: str):
    # 1. Redis 캐시 확인
    cache_key = f"chart:{ticker}"
    cached = redis_client.get(cache_key)
    
    if cached:
        return json.loads(cached)
    
    # 2. Yahoo Finance 호출
    data = fetch_from_yahoo(ticker)
    
    # 3. Redis에 저장 (60초 TTL)
    redis_client.setex(cache_key, 60, json.dumps(data))
    
    return data
```

**일일 주가 데이터 저장**:
```sql
CREATE TABLE daily_prices (
  ticker VARCHAR(20),
  date DATE,
  open NUMERIC,
  high NUMERIC,
  low NUMERIC,
  close NUMERIC,
  volume BIGINT,
  PRIMARY KEY (ticker, date)
);

-- 매일 오전 9시 크론잡으로 업데이트
```

**체크리스트**:
- [ ] Redis 서버 추가 (Railway Add-on, 무료 25MB)
- [ ] 캐싱 레이어 구현
- [ ] 일일 주가 배치 작업
- [ ] DB 인덱스 최적화

---

### 5.2 CDN & 정적 파일
**현재**: Vercel이 자동 CDN 제공 ✅

**추가 최적화**:
- 이미지 압축 (WebP)
- JavaScript 번들 최소화
- Lazy Loading

---

### 5.3 사용자 알림 시스템 ⭐
**목표**: 조건 충족 시 자동 알림 (가격 도달, Leader 등장, 섹터 Surge)

**알림 유형**:

| 알림 종류 | 트리거 조건 | 티어 제한 |
|----------|------------|---------|
| **가격 알림** | 목표가 도달, 손절가 터치 | Basic: 10개, Pro: 무제한 |
| **종목 알림** | Follower → Leader 전환 | Basic: 5개, Pro: 무제한 |
| **섹터 알림** | SURGE 섹터 등장 (flow_score > 75) | Pro만 |
| **Market Regime 알림** | RISK_ON ↔ RISK_OFF 전환 | 모든 티어 |

**알림 채널**:
```python
# 1. 이메일 (기본)
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_email_alert(user_email, alert_type, message):
    message = Mail(
        from_email='alerts@decision-stream.com',
        to_emails=user_email,
        subject=f'[Decision Stream] {alert_type}',
        html_content=f'<strong>{message}</strong>'
    )
    sg = SendGridAPIClient(SENDGRID_API_KEY)
    sg.send(message)

# 2. Slack Webhook (Pro 티어)
import requests

def send_slack_alert(webhook_url, message):
    payload = {
        "text": message,
        "username": "Decision Stream Bot",
        "icon_emoji": ":chart_with_upwards_trend:"
    }
    requests.post(webhook_url, json=payload)

# 3. Custom Webhook (Pro 티어)
def send_webhook_alert(webhook_url, alert_data):
    requests.post(webhook_url, json=alert_data)
```

**DB 스키마**:
```sql
-- 알림 설정 테이블
CREATE TABLE user_alerts (
  id SERIAL PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  alert_type VARCHAR(50),  -- price, stock, sector, regime
  ticker VARCHAR(20),       -- 종목 코드 (종목 알림의 경우)
  condition VARCHAR(255),   -- JSON: {"type": "price_above", "value": 150000}
  channels VARCHAR[],       -- ['email', 'slack', 'webhook']
  webhook_url VARCHAR(500), -- Slack/Custom Webhook URL
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT NOW()
);

-- 알림 발송 로그
CREATE TABLE alert_logs (
  id SERIAL PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  alert_id INTEGER REFERENCES user_alerts(id),
  sent_at TIMESTAMP DEFAULT NOW(),
  channel VARCHAR(50),
  status VARCHAR(50)  -- sent, failed, rate_limited
);
```

**백엔드 API**:
```python
# 알림 생성
@app.post("/api/alerts")
def create_alert(
    user_id: str, 
    alert_type: str,
    ticker: Optional[str],
    condition: dict,
    channels: list[str]
):
    # 티어별 제한 확인
    user = get_user_profile(user_id)
    
    if user.subscription_tier == 'free':
        raise HTTPException(400, "알림 기능은 Basic 이상 필요")
    
    if user.subscription_tier == 'basic':
        alert_count = count_user_alerts(user_id)
        if alert_type == 'price' and alert_count >= 10:
            raise HTTPException(400, "Basic 티어는 최대 10개 가격 알림")
        if alert_type == 'sector':
            raise HTTPException(400, "섹터 알림은 Pro 티어 전용")
    
    # DB에 저장
    alert_id = db.insert_alert(user_id, alert_type, ticker, condition, channels)
    return {"alert_id": alert_id}

# 알림 체크 (크론잡, 1분마다)
@app.post("/internal/check-alerts")
def check_alerts():
    active_alerts = db.get_active_alerts()
    
    for alert in active_alerts:
        if should_trigger(alert):
            send_notification(alert)
            
            # 발송 로그 저장
            db.insert_alert_log(alert.user_id, alert.id, 'email', 'sent')

def should_trigger(alert):
    if alert.alert_type == 'price':
        current_price = get_current_price(alert.ticker)
        condition = json.loads(alert.condition)
        
        if condition['type'] == 'price_above':
            return current_price >= condition['value']
        elif condition['type'] == 'price_below':
            return current_price <= condition['value']
    
    elif alert.alert_type == 'stock':
        # Follower → Leader 전환 체크
        classification = classify_stock(alert.ticker)
        return classification == 'LEADER'
    
    elif alert.alert_type == 'sector':
        sector_data = get_sector_data()
        for sector in sector_data:
            if sector['flow_score'] > 75:
                return True
    
    return False
```

**프론트엔드 UI**:
```html
<!-- 알림 설정 모달 -->
<div class="alert-modal">
  <h3>📢 알림 설정</h3>
  
  <select id="alert-type">
    <option value="price">가격 알림</option>
    <option value="stock">종목 알림 (Leader 전환)</option>
    <option value="sector">섹터 알림 (SURGE)</option>
  </select>
  
  <input type="text" id="ticker" placeholder="종목 코드 (예: 012450)">
  
  <input type="number" id="target-price" placeholder="목표가 (예: 150000)">
  
  <label>
    <input type="checkbox" checked> 이메일
  </label>
  <label>
    <input type="checkbox"> Slack (Pro)
  </label>
  
  <button onclick="createAlert()">알림 생성</button>
</div>
```

**이메일 서비스 옵션**:

| 서비스 | 무료 한도 | 월 비용 |
|--------|---------|--------|
| **SendGrid** | 100/일 (3,000/월) | $19.95 (50K/월) |
| **Mailgun** | 5,000/월 | $35 (50K/월) |
| **Amazon SES** | 62,000/월 (EC2 내) | $0.10 / 1,000건 |
| **Resend** | 3,000/월 | $20 (50K/월) |

**권장**: SendGrid (3,000/월 무료, 충분함)

**Slack 알림 예시**:
```
🚀 [Decision Stream 알림]

종목: 한화에어로스페이스 (012450)
이벤트: Follower → Leader 전환
현재가: ₩1,149,000 (+3.2%)

9요소 점수:
- 자금 흐름: 85/100
- 가격 구조: 78/100
- 서사: 92/100

👉 상세 보기: https://decision-stream.com/stock/012450
```

**체크리스트**:
- [ ] 알림 DB 테이블 생성
- [ ] 알림 생성 API (/api/alerts)
- [ ] 알림 체크 크론잡 (Railway Cron)
- [ ] SendGrid 계정 생성 및 통합
- [ ] 이메일 템플릿 디자인
- [ ] Slack Webhook 통합 (Pro 티어)
- [ ] 프론트엔드 알림 설정 UI
- [ ] 티어별 알림 제한 구현
- [ ] 알림 히스토리 페이지

**예상 비용**:
- SendGrid: $0 (3,000/월 무료)
- Railway Cron: $0 (포함)
- **총: $0**

---

### 5.4 백엔드 확장성
**현재**: Railway 단일 인스턴스 (최대 8GB RAM)

**확장 옵션**:
- **Horizontal Scaling**: Railway Team Plan ($20/월) - 로드 밸런서
- **Serverless**: 백엔드를 AWS Lambda로 이전 (Pay-per-request)

**예상 비용** (월 1만 사용자 기준):
- Railway Hobby: $5 (500시간)
- Railway Team: $20 (무제한)
- AWS Lambda: ~$10 (100만 요청)

---

## 📋 Phase 6: 법적 준비 (1주)

### 6.1 필수 문서
**서비스 약관** (Terms of Service):
- 사용 제한 사항
- 데이터 정확성 면책
- 구독 취소 정책
- 환불 정책

**개인정보 처리방침** (Privacy Policy):
- 수집하는 정보 (이메일, 결제 정보)
- 정보 사용 목적
- 제3자 제공 (Stripe, Supabase)
- GDPR/CCPA 준수

**템플릿**:
- https://www.termsfeed.com/terms-service-generator/
- https://www.privacypolicies.com/privacy-policy-generator/

**체크리스트**:
- [ ] 서비스 약관 작성 (/terms.html)
- [ ] 개인정보 처리방침 작성 (/privacy.html)
- [ ] 회원가입 시 동의 체크박스
- [ ] 쿠키 동의 배너 (GDPR)

---

### 6.2 금융 투자 면책
**⚠️ 중요**: 주식 투자 추천은 법적 리스크가 있습니다.

**명시 사항**:
> "본 서비스는 투자 조언이 아닌 정보 제공 목적입니다. 투자 결정은 본인의 책임이며, 손실에 대해 회사는 책임지지 않습니다."

**추가**:
- Trading Plan은 "참고용"임을 강조
- AI Agent 결과는 "예측"이 아닌 "분석"

---

## 📋 Phase 7: 마케팅 & 런칭 (2-3주)

### 7.1 랜딩 페이지
**목표**: Free → Basic 전환율 10% 이상

**구성 요소**:
1. **Hero Section**: "AI가 분석하는 스윙 트레이딩 시스템"
2. **기능 소개**: 3가지 핵심 기능 (Market Regime, Sector Heatmap, Stock Funnel)
3. **가격표**: Free vs Basic vs Pro 비교
4. **CTA**: "무료로 시작하기" (회원가입)
5. **Social Proof**: 사용자 후기 (런칭 후 수집)

**도구**:
- Figma (디자인)
- Tailwind CSS (구현)
- Vercel (배포)

---

### 7.2 SEO 최적화
```html
<!-- index.html -->
<title>Decision Stream - AI 주식 분석 시스템</title>
<meta name="description" content="AI Agent가 실시간으로 분석하는 중기 스윙 투자 시스템. 시장 상태, 섹터 순위, 종목 추천을 자동화하세요.">
<meta name="keywords" content="주식 분석, AI 투자, 스윙 트레이딩, 시장 분석, 섹터 로테이션">
<link rel="canonical" href="https://decisionstream.io">
```

**Google Search Console**:
- 사이트맵 제출
- robots.txt 설정

---

### 7.3 초기 사용자 확보
**채널**:
1. **Reddit**: r/StockMarket, r/swingtrading
2. **Twitter/X**: 주식 투자 커뮤니티
3. **네이버 카페**: "주식초보모임", "단타의 신"
4. **Product Hunt**: 런칭 (최소 100 upvotes 목표)
5. **YouTube**: 사용법 튜토리얼 (한국어/영어)

**프리미엄 전략**:
- Beta 사용자 50명 모집 (무료 Pro 1개월)
- 피드백 수집 → 개선 → 정식 런칭

---

## 💰 예상 비용 (월)

| 항목 | 서비스 | 비용 |
|------|--------|------|
| **호스팅** | Railway (백엔드) | $5~20 |
| | Vercel (프론트) | $0 (무료) |
| **DB** | Supabase PostgreSQL | $0 (무료 500MB) |
| **캐시** | Railway Redis | $0 (무료 25MB) |
| **인증** | Supabase Auth | $0 (무료) |
| **결제** | Stripe | 3.6% + ₩250/건 |
| **모니터링** | Sentry | $0 (무료 5K 이벤트) |
| **도메인** | domain.com | $1~2/월 |
| **총계** | | **~$10~30/월** |

**수익 시뮬레이션**:
- Free 사용자: 1,000명 → ₩0
- Basic 사용자: 50명 × ₩29,000 = **₩1,450,000/월**
- Pro 사용자: 10명 × ₩99,000 = **₩990,000/월**
- **총 수익**: **₩2,440,000/월 (~$1,850)**
- **순이익**: **₩2,400,000/월** (비용 제외)

---

## 📊 타임라인

| 주차 | 작업 | 산출물 |
|------|------|--------|
| **1-2주** | 인증 & DB 구축 | 회원가입/로그인 기능 |
| **3-4주** | 결제 연동 | Stripe 구독 시스템 |
| **5주** | Rate Limiting & 보안 | API Key 발급, HTTPS |
| **6주** | 모니터링 설정 | Sentry, Grafana |
| **7-8주** | 인프라 최적화 | Redis 캐싱, DB 배치 |
| **9주** | 법적 문서 작성 | 약관, 개인정보 처리방침 |
| **10-12주** | 마케팅 & 런칭 | 랜딩 페이지, Beta 테스트 |

**총 기간**: **약 3개월**

---

## 🎯 즉시 시작할 수 있는 작업 (Quick Wins)

### 1. 도메인 구매 (30분)
- **Namecheap** or **GoDaddy**
- 추천 도메인: `decisionstream.io`, `aitrading.pro`
- 비용: ~$10/년

### 2. Railway 배포 (1시간)
- DEPLOYMENT_CHECKLIST.md 참고
- 백엔드 배포 완료

### 3. Vercel 배포 (30분)
- GitHub 연동
- 프론트엔드 배포 완료

### 4. Supabase 계정 생성 (30분)
- https://supabase.com
- 새 프로젝트 생성
- PostgreSQL DB 자동 생성

### 5. Stripe 계정 생성 (1시간)
- https://stripe.com
- 가격 상품 3개 생성 (Free, Basic, Pro)
- Webhook 설정

---

## 🚨 런칭 전 필수 체크리스트

- [ ] HTTPS 적용 (커스텀 도메인)
- [ ] 환경 변수 모두 설정 (API Keys 숨김)
- [ ] Rate Limiting 동작 확인
- [ ] 결제 테스트 (Test Mode)
- [ ] 에러 추적 동작 확인 (Sentry)
- [ ] 서비스 약관, 개인정보 처리방침 게시
- [ ] Beta 테스트 (최소 10명)
- [ ] 백업 시스템 (DB 자동 백업)
- [ ] 고객 지원 채널 (이메일 or 채팅)

---

## 📚 참고 자료

### 유사 SaaS 분석
- **TradingView**: 차트 + 소셜 네트워크
- **Finviz**: 주식 스크리너 (무료 + Premium $39.50/월)
- **Koyfin**: 금융 데이터 플랫폼 (무료 + Pro $39/월)

### 기술 스택 문서
- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [Supabase 가이드](https://supabase.com/docs)
- [Stripe API 문서](https://stripe.com/docs/api)
- [Vercel 배포 가이드](https://vercel.com/docs)

### SaaS 운영 가이드
- [SaaS Metrics](https://a16z.com/2015/08/21/16-metrics/) (a16z)
- [Pricing Strategy](https://www.priceintelligently.com/blog)
- [Customer Retention](https://www.profitwell.com/retention)

---

## 🎉 마무리

**이 로드맵을 따르면**:
- ✅ 3개월 안에 상용 SaaS 런칭 가능
- ✅ 초기 비용 $10~30/월 (매우 저렴)
- ✅ 확장 가능한 아키텍처
- ✅ 법적 리스크 최소화

**다음 단계**:
1. 이 문서를 팀원과 공유
2. Phase 1부터 순차적으로 진행
3. 주간 진행 상황 체크

**질문/피드백**:
- Issues 탭에서 토론
- 혹은 이메일로 연락

---

**Good luck! 🚀**
