# 🚀 Vercel + Railway 배포 체크리스트

## ✅ 배포 전 준비

### 1. GitHub Repository 생성
```bash
# 터미널에서 실행
cd /path/to/your/project

# Git 초기화 (아직 안했다면)
git init

# .gitignore 확인
cat .gitignore  # .env가 포함되어 있는지 확인

# 첫 커밋
git add .
git commit -m "Initial commit: Decision Stream MVP"

# GitHub에서 새 저장소 생성 후
git remote add origin https://github.com/YOUR_USERNAME/decision-stream.git
git branch -M main
git push -u origin main
```

**확인:**
- [ ] GitHub 저장소 생성 완료
- [ ] 로컬 코드 푸시 완료
- [ ] .env 파일이 Git에 포함되지 않았는지 확인

---

## 🚂 Railway 배포 (백엔드)

### Step 1: 계정 생성 및 로그인
1. https://railway.app 접속
2. **Login with GitHub** 클릭
3. GitHub 계정 연동 허용

**확인:**
- [ ] Railway 계정 생성 완료

---

### Step 2: 프로젝트 생성
1. **New Project** 클릭
2. **Deploy from GitHub repo** 선택
3. 저장소 `decision-stream` 선택
4. **Deploy Now** 클릭

**확인:**
- [ ] 프로젝트 생성 완료
- [ ] 첫 배포 시작됨

---

### Step 3: 백엔드 설정
1. 배포된 프로젝트 클릭
2. **Settings** 탭 클릭
3. **Root Directory** 입력: `backend`
4. **Start Command** 입력: `uvicorn server:app --host 0.0.0.0 --port $PORT`
5. **Save** 클릭

**확인:**
- [ ] Root Directory 설정 완료
- [ ] Start Command 설정 완료

---

### Step 4: 환경 변수 설정
1. **Variables** 탭 클릭
2. **New Variable** 클릭
3. 다음 변수 추가:

```
KRX_API_KEY=your_actual_key_here
NH_API_KEY=your_actual_key_here
KIS_APP_KEY=your_actual_key_here
KIS_APP_SECRET=your_actual_secret_here
KIS_USE_MOCK=true
ALPHA_VANTAGE_KEY=demo
```

4. **Add** 클릭

**확인:**
- [ ] 모든 환경 변수 추가 완료
- [ ] 변수 저장 완료

---

### Step 5: 도메인 확인
1. **Settings** → **Networking** 탭
2. **Public Domain** 복사 (예: `decision-stream-backend-production.up.railway.app`)

**도메인 기록:**
```
Railway Backend URL: ___________________________________
```

**확인:**
- [ ] Railway 도메인 복사 완료

---

### Step 6: 백엔드 테스트
브라우저에서 접속:

```
https://YOUR-RAILWAY-DOMAIN.railway.app/
https://YOUR-RAILWAY-DOMAIN.railway.app/regime?key=ds-test-2026
```

**확인:**
- [ ] 루트 URL 응답 확인
- [ ] /regime 엔드포인트 정상 작동

---

## 🌐 Vercel 배포 (프론트엔드)

### Step 1: 계정 생성 및 로그인
1. https://vercel.com 접속
2. **Sign Up with GitHub** 클릭
3. GitHub 계정 연동 허용

**확인:**
- [ ] Vercel 계정 생성 완료

---

### Step 2: API URL 업데이트
**로컬에서 수정:**

`index.html` 파일 열기, 394번 줄 수정:

```javascript
const API = isDevelopment 
  ? "http://127.0.0.1:8125" 
  : "https://YOUR-RAILWAY-DOMAIN.railway.app"; // ⬅️ 여기에 Railway 도메인 입력
```

**저장 후 커밋:**
```bash
git add index.html
git commit -m "Update API URL for production"
git push
```

**확인:**
- [ ] API URL 업데이트 완료
- [ ] Git 푸시 완료

---

### Step 3: 프로젝트 배포
1. Vercel 대시보드에서 **Add New** → **Project** 클릭
2. GitHub 저장소 `decision-stream` 선택
3. **Import** 클릭
4. 설정 확인:
   - Framework Preset: **Other**
   - Root Directory: `.` (루트)
   - Build Command: (비워두기)
   - Output Directory: `.` (루트)
5. **Deploy** 클릭

**확인:**
- [ ] 프로젝트 Import 완료
- [ ] 배포 시작됨

---

### Step 4: 배포 완료 확인
1. 배포 완료 대기 (1-2분)
2. **Visit** 버튼 클릭
3. 도메인 확인 (예: `decision-stream.vercel.app`)

**도메인 기록:**
```
Vercel Frontend URL: ___________________________________
```

**확인:**
- [ ] 배포 성공 (✅ Ready)
- [ ] 도메인 접속 가능

---

## 🧪 전체 테스트

### Test 1: 시장 분석 로딩
1. Vercel 도메인 접속
2. **Market Regime** 확인:
   - "RISK_ON" 표시되는지
   - Risk Score 표시되는지
3. **Sector Heatmap** 확인:
   - 섹터 목록 로딩되는지

**확인:**
- [ ] Market Regime 정상 로딩
- [ ] Sector Heatmap 정상 로딩

---

### Test 2: 섹터 클릭
1. **방산** 섹터 클릭 (SURGE)
2. Stock Funnel 확인:
   - Follower에 "Lockheed Martin" 표시
   - Follower에 "한화에어로스페이스" 표시

**확인:**
- [ ] 섹터 클릭 정상 작동
- [ ] Stock Funnel 정상 표시

---

### Test 3: 종목 클릭 → 시뮬레이션 이동
1. **Lockheed Martin** 클릭
2. `trade_plan_simulation.html`로 이동 확인
3. 종목 정보 자동 입력 확인:
   - 시장: US
   - 종목: LMT
   - 현재가: $445.50

**확인:**
- [ ] 종목 클릭 시 페이지 이동
- [ ] 종목 정보 자동 입력

---

### Test 4: 시장 해설 생성
1. index.html로 돌아가기
2. **▶ 시장 해설 생성** 버튼 클릭
3. 시장 해설 표시 확인

**확인:**
- [ ] 시장 해설 버튼 작동
- [ ] 시장 해설 정상 표시

---

### Test 5: 모바일 테스트
1. 스마트폰에서 Vercel 도메인 접속
2. 레이아웃 확인
3. 모든 기능 테스트

**확인:**
- [ ] 모바일 반응형 정상
- [ ] 모든 기능 작동

---

## 🐛 문제 해결

### 문제 1: Railway 빌드 실패
**증상:**
```
ERROR: Could not find a version that satisfies the requirement ...
```

**해결:**
```bash
cd backend
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update requirements"
git push
```

→ Railway가 자동으로 재배포

---

### 문제 2: CORS 에러
**증상:**
```
Access to fetch at '...' has been blocked by CORS policy
```

**해결:**
`backend/server.py` 수정:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://decision-stream.vercel.app",
        "https://*.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**커밋 후 푸시:**
```bash
git add backend/server.py
git commit -m "Fix CORS for Vercel"
git push
```

---

### 문제 3: API 응답 없음
**증상:**
- index.html에서 "로딩중" 상태 유지
- 콘솔에 에러 표시

**해결:**
1. **F12** → **Console** 탭 확인
2. Railway 로그 확인:
   - Railway 대시보드
   - 프로젝트 클릭
   - **Deployments** → **View Logs**

---

## 📊 모니터링

### Railway 로그 확인
```
Railway 대시보드 → 프로젝트 → Deployments → View Logs
```

### Vercel 로그 확인
```
Vercel 대시보드 → 프로젝트 → Deployments → 배포 항목 클릭 → Logs
```

---

## ✅ 최종 확인

- [ ] Railway 백엔드 정상 작동
- [ ] Vercel 프론트엔드 정상 작동
- [ ] API 연결 정상
- [ ] 모든 기능 테스트 완료
- [ ] 모바일 테스트 완료
- [ ] 도메인 기록 완료

---

## 🎉 배포 완료!

**프로덕션 URL:**
```
Frontend: https://decision-stream.vercel.app
Backend:  https://YOUR-RAILWAY-DOMAIN.railway.app
```

**다음 단계:**
1. 커스텀 도메인 연결 (선택)
2. Google Analytics 추가 (선택)
3. 사용자 피드백 수집

---

**문제가 발생하면 [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)를 참조하세요!**