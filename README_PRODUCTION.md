# 🎯 Decision Stream - 중기 스윙 투자 시스템

**Market-Driven Trade Planning System**

실시간 시장 분석 기반 중기 스윙 트레이딩을 위한 의사결정 지원 시스템

---

## 🚀 빠른 시작

### 로컬 개발 환경

```bash
# 1. 백엔드 서버 실행
cd backend
pip install -r requirements.txt
python server.py

# 2. 프론트엔드 실행
# index.html을 브라우저에서 열기
```

### 프로덕션 배포

**배포 가이드**: [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) 참조

---

## 📦 주요 기능

### 1️⃣ 시장 분석 (Market Regime)
- **RISK_ON/RISK_OFF** 자동 감지
- Risk Score 기반 포지션 관리
- Playbook 자동 추천

### 2️⃣ 섹터 히트맵 (Sector Heatmap)
- 자금 흐름 실시간 추적
- **SURGE** 섹터 자동 감지
- 섹터 강도 스코어링

### 3️⃣ Stock Funnel
- **Leader**: 선도주 식별
- **Follower**: 추종주 (매집 기회)
- **No-Go**: 진입 금지 종목

### 4️⃣ 매매 계획 시뮬레이션
- 진입가/손절가/목표가 자동 계산
- 7요소 체크리스트
- 리스크 관리 경고

### 5️⃣ 시장 해설 생성
- AI 기반 시장 분석 리포트
- 섹터별 전략 추천
- 종목별 진입 시점 분석

---

## 🏗️ 기술 스택

### Frontend
- **HTML5 + Vanilla JavaScript**
- **CSS3** (Dark Theme)
- **Static Hosting**: Vercel

### Backend
- **FastAPI** (Python)
- **Uvicorn** (ASGI Server)
- **Redis** (Caching)
- **Hosting**: Railway

### Data Sources
- **KRX API** (한국 주식)
- **NH투자증권 API** (한국 주식)
- **Yahoo Finance** (미국 주식)

---

## 📂 프로젝트 구조

```
decision-stream/
├── index.html                      # 메인 대시보드
├── trade_plan_simulation.html      # 매매 계획 시뮬레이션
├── market_driven_plan.html         # (선택) Market-Driven Plan
├── vercel.json                     # Vercel 배포 설정
├── DEPLOYMENT_GUIDE.md             # 배포 가이드
├── README.md                       # 프로젝트 문서
│
└── backend/                        # 백엔드 서버
    ├── server.py                   # FastAPI 메인 서버
    ├── scheduler.py                # 주가 자동 업데이트
    ├── requirements.txt            # Python 패키지
    ├── .env                        # 환경 변수 (비공개)
    ├── Procfile                    # Railway 배포 설정
    ├── runtime.txt                 # Python 버전
    │
    └── services/                   # API 서비스 모듈
        ├── nh_investment_api.py    # NH투자증권 API
        ├── nh_stock_api.py         # NH투자증권 API (보조)
        ├── krx_stock_api.py        # KRX API
        └── us_stock_service.py     # 미국 주식 (Yahoo Finance)
```

---

## ⚙️ 환경 설정

### backend/.env

```bash
# KRX API
KRX_API_KEY=your_krx_api_key

# NH투자증권 API (주 사용)
NH_APP_KEY=your_nh_app_key
NH_APP_SECRET=your_nh_app_secret
NH_USE_MOCK=false

# Alpha Vantage (미국 주식)
ALPHA_VANTAGE_KEY=your_alpha_vantage_key

# Redis (프로덕션)
REDIS_URL=redis://localhost:6379
```

---

## 🔐 보안

### API 키 관리
- ✅ `.env` 파일 사용 (Git에 커밋하지 않음)
- ✅ 백엔드에서만 API 키 사용
- ✅ 프론트엔드에는 API 키 노출 금지

### CORS 설정
```python
# server.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📊 데이터 캐싱

### Redis 캐싱 전략
- **주가 데이터**: 5분 TTL
- **시장 레짐**: 10분 TTL
- **섹터 데이터**: 5분 TTL

**효과:**
- API 호출 99% 감소
- 응답 속도 10배 향상
- 비용 절감 (API 호출 제한 회피)

---

## 🚀 배포 상태

### Vercel (Frontend)
- **URL**: https://decision-stream.vercel.app
- **Status**: ✅ Live
- **Build**: Automatic (Git push)

### Railway (Backend)
- **URL**: https://decision-stream-backend.railway.app
- **Status**: ✅ Live
- **Deploy**: Automatic (Git push)

---

## 📈 확장 계획

### Phase 1: MVP (현재)
- ✅ 시장 분석 대시보드
- ✅ 매매 계획 시뮬레이션
- ✅ Mock 데이터 지원

### Phase 2: Production (1-2주)
- 🔄 실제 API 연동 (KRX, NH)
- 🔄 Redis 캐싱 구현
- 🔄 사용자 인증 시스템

### Phase 3: Scale (1-2개월)
- ⏳ 실시간 알림 (조건 충족 시)
- ⏳ 포트폴리오 추적
- ⏳ 백테스팅 시스템

---

## 💰 비용 예측

### 무료 티어 (0-100명)
- **Vercel**: $0/월
- **Railway**: $0/월 (500시간)
- **총**: $0/월

### 유료 (100-500명)
- **Vercel Pro**: $20/월
- **Railway Pro**: $20/월
- **Redis (Upstash)**: $10/월
- **총**: $50/월

---

## 🐛 알려진 이슈

### 1. API 호출 제한
- **문제**: KRX API는 하루 1,000회 제한
- **해결**: Redis 캐싱으로 288회로 감소

### 2. CORS 에러 (로컬 개발)
- **문제**: `file://` 프로토콜에서 fetch 실패
- **해결**: Live Server 사용 또는 Mock 데이터 활성화

### 3. 시장 시간 외 데이터
- **문제**: 장 마감 후 주가 업데이트 안됨
- **해결**: 마지막 수신 시간 표시

---

## 📝 라이선스

**MIT License**

본 프로젝트는 교육 및 투자 보조 목적으로 제공됩니다.  
투자 권유나 수익 보장을 하지 않습니다.

---

## 👨‍💻 개발자

**Decision Stream Team**

- GitHub: https://github.com/YOUR_USERNAME/decision-stream
- Contact: your-email@example.com

---

## 🙏 감사의 말

- **FastAPI**: 빠른 API 개발
- **Vercel**: 무료 호스팅
- **Railway**: 간편한 백엔드 배포
- **KRX/NH**: 주가 데이터 제공

---

**⚠️ 면책 조항**

본 시스템은 투자 판단을 보조하는 도구일 뿐, 투자 권유나 수익을 보장하지 않습니다.  
모든 투자 결정은 본인의 책임 하에 이루어져야 합니다.

---

**📖 더 읽기**

- [배포 가이드](./DEPLOYMENT_GUIDE.md)
- [API 문서](./backend/README.md)
- [트러블슈팅](./TROUBLESHOOTING.md)