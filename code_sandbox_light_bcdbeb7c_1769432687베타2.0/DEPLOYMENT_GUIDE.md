# Deployment Guide: Vercel + Railway

## 🚀 배포 순서

### 1. GitHub Repository 생성

```bash
# Git 초기화 (아직 안했다면)
git init
git add .
git commit -m "Initial commit"

# GitHub에 새 저장소 생성 후
git remote add origin https://github.com/YOUR_USERNAME/decision-stream.git
git branch -M main
git push -u origin main
```

---

## 📦 Step 1: 백엔드 배포 (Railway)

### 1-1. Railway 가입
- https://railway.app 접속
- **Login with GitHub** 클릭
- GitHub 계정 연동

### 1-2. 새 프로젝트 생성
1. **New Project** 클릭
2. **Deploy from GitHub repo** 선택
3. 저장소 선택: `decision-stream`
4. **Deploy Now** 클릭

### 1-3. 백엔드 설정
1. 프로젝트 클릭 → **Settings** 탭
2. **Root Directory** 설정: `backend`
3. **Start Command** 설정: `uvicorn server:app --host 0.0.0.0 --port $PORT`

### 1-4. 환경 변수 설정
**Variables** 탭에서 추가:

```
KRX_API_KEY=your_krx_api_key_here
NH_API_KEY=your_nh_api_key_here
KIS_APP_KEY=your_kis_app_key_here
KIS_APP_SECRET=your_kis_app_secret_here
KIS_USE_MOCK=true
ALPHA_VANTAGE_KEY=your_alpha_vantage_key_here
```

### 1-5. 도메인 확인
- **Settings** → **Networking**
- **Public Domain** 복사 (예: `https://decision-stream-backend.railway.app`)

---

## 🌐 Step 2: 프론트엔드 배포 (Vercel)

### 2-1. Vercel 가입
- https://vercel.com 접속
- **Sign Up with GitHub** 클릭
- GitHub 계정 연동

### 2-2. 새 프로젝트 생성
1. **Add New** → **Project** 클릭
2. GitHub 저장소 선택: `decision-stream`
3. **Import** 클릭

### 2-3. 프로젝트 설정
- **Framework Preset**: Other
- **Root Directory**: `.` (루트)
- **Build Command**: (비워두기)
- **Output Directory**: `.` (루트)

### 2-4. 환경 변수 설정
**Environment Variables** 섹션에 추가:

```
NEXT_PUBLIC_API_URL=https://decision-stream-backend.railway.app
```

### 2-5. 배포
- **Deploy** 클릭
- 배포 완료 후 도메인 확인 (예: `https://decision-stream.vercel.app`)

---

## 🔧 Step 3: API URL 연결

### 3-1. vercel.json 수정

`vercel.json` 파일을 열어 Railway 도메인으로 변경:

```json
{
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://YOUR-RAILWAY-DOMAIN.railway.app/:path*"
    }
  ]
}
```

### 3-2. index.html API URL 변경

```javascript
// 개발 환경
const API = "http://127.0.0.1:8125";
const USE_MOCK_DATA = true;

// 프로덕션 환경 (배포 후)
const API = "https://YOUR-RAILWAY-DOMAIN.railway.app";
const USE_MOCK_DATA = false;
```

**또는 자동 감지:**

```javascript
const isDevelopment = window.location.hostname === 'localhost';
const API = isDevelopment 
  ? "http://127.0.0.1:8125" 
  : "https://YOUR-RAILWAY-DOMAIN.railway.app";
const USE_MOCK_DATA = isDevelopment;
```

### 3-3. 변경사항 배포

```bash
git add .
git commit -m "Update API URL for production"
git push
```

→ Vercel이 자동으로 재배포합니다!

---

## ✅ Step 4: 배포 확인

### 4-1. 백엔드 테스트

```bash
# 브라우저에서 접속
https://YOUR-RAILWAY-DOMAIN.railway.app/

# API 테스트
https://YOUR-RAILWAY-DOMAIN.railway.app/regime?key=ds-test-2026
```

### 4-2. 프론트엔드 테스트

```bash
# Vercel 도메인 접속
https://decision-stream.vercel.app/

# 기능 확인
1. Market Regime 로딩 확인
2. Sector Heatmap 로딩 확인
3. 종목 클릭 → 시뮬레이션 이동 확인
```

---

## 🐛 문제 해결

### 문제 1: CORS 에러

**증상:**
```
Access to fetch at 'https://...' has been blocked by CORS policy
```

**해결:**
`backend/server.py` 수정:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "https://decision-stream.vercel.app",
        "https://*.vercel.app"  # Vercel preview 도메인
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 문제 2: Railway 빌드 실패

**증상:**
```
ERROR: Could not find a version that satisfies the requirement ...
```

**해결:**
`backend/requirements.txt` 확인:

```bash
cd backend
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update requirements"
git push
```

### 문제 3: API 키 없음

**증상:**
```
KeyError: 'KRX_API_KEY'
```

**해결:**
- Railway 대시보드 → Variables 탭
- 모든 환경 변수 재확인
- 저장 후 **Restart** 클릭

---

## 📊 모니터링

### Railway 로그 확인
1. Railway 대시보드
2. 프로젝트 클릭
3. **Deployments** 탭
4. **View Logs** 클릭

### Vercel 로그 확인
1. Vercel 대시보드
2. 프로젝트 클릭
3. **Deployments** 탭
4. 배포 항목 클릭 → **Logs** 탭

---

## 💰 비용

### Railway
- **무료**: 500시간/월 ($5 크레딧)
- **Pro**: $20/월 (무제한)

### Vercel
- **Hobby**: 무료 (개인 프로젝트)
- **Pro**: $20/월 (상업 프로젝트)

**총 무료 사용 가능: 500시간/월**
- 하루 16시간 이상 운영 가능
- 24시간 운영: ~20일 무료

---

## 🎯 다음 단계

1. ✅ **Redis 캐싱 추가** (API 호출 최소화)
2. ✅ **사용자 인증** (로그인 시스템)
3. ✅ **커스텀 도메인** (your-domain.com)
4. ✅ **분석 도구** (Google Analytics)
5. ✅ **에러 트래킹** (Sentry)

---

## 📝 체크리스트

배포 전:
- [ ] GitHub 저장소 생성
- [ ] .gitignore에 .env 추가
- [ ] requirements.txt 최신화
- [ ] API 키 준비

배포 후:
- [ ] Railway 환경 변수 설정
- [ ] Vercel 도메인 확인
- [ ] CORS 설정 확인
- [ ] API 테스트 완료
- [ ] 프론트엔드 테스트 완료

---

**배포 완료 후 도메인을 알려주세요!** 🎉