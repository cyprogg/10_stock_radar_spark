# 🚀 Stock Radar Spark - AI 주식 분석 플랫폼

**AI 기반 주식 종목 분석 및 투자 의사결정 지원 시스템**

---

## 📊 소개

Stock Radar Spark는 **5개의 AI Agent**를 활용하여 주식을 종합적으로 분석하고 투자 전략을 자동으로 생성합니다.

### 핵심 가치
- **설명 가능한 AI**: 모든 추천에는 논리적 근거가 있습니다
- **자동화된 분석**: 5개 Algorithm이 협력하여 신뢰도 높은 결과 제공
- **실시간 데이터**: Yahoo Finance + OpenDART 공시정보 활용
- **사용자 맞춤**: 투자 성향(보수/중립/공격)에 따른 설정

---

## ✨ 주요 기능

### 1. 시장 상태 분석
현재 시장이 **공격적 매수 시기(RISK_ON)** 또는 **방어 모드(RISK_OFF)**인지 판단합니다.

**결과:**
```
상태: RISK_ON
신뢰도: 85%
추천: 공격적 매수 가능
```

### 2. 섹터 강도 분석
현재 자금이 집중되고 있는 **최강 섹터**를 랭킹합니다.

**결과:**
```
1. 반도체 - 강한 상승 (95점)
2. 방위산업 - 중등도 상승 (88점)
3. 에너지 - 중립 (65점)
```

### 3. 종목 분류
개별 종목을 **LEADER / FOLLOWER / NO_GO**로 자동 분류합니다.

**결과:**
```
분류: LEADER
신뢰도: 92%
추천: 매수
우선도: 높음
```

### 4. 매매 계획
분류된 종목에 대해 **진입가, 손절선, 목표가**를 자동으로 제시합니다.

**결과:**
```
진입가: 71,400원
손절가: 67,000원
목표가: 75,000원
위험/수익 비율: 1:2.0
```

### 5. 투자 위험 평가
**우려사항**과 **대응방안**을 자동으로 제시합니다.

**결과:**
```
위험도: MEDIUM
우려사항:
  - 대형 기관 물량 증가
  - 기술적 저항선 근처

대응방안:
  - 분할 진입 권장
  - 손절선 엄격히 준수
```

---

## 🔧 기술 스택

| 계층 | 기술 |
|---|---|
| **Backend** | FastAPI (Python) |
| **Database** | SQLite (dev) / PostgreSQL (prod) |
| **Authentication** | JWT + bcrypt |
| **Data Source** | Yahoo Finance, OpenDART API |
| **AI Engine** | 5-Agent Orchestrator |

---

## 🎯 사용 시나리오

### 아침 시장 점검
```
1. /api/analysis/market-regime
   → 오늘 장의 성격 파악

2. /api/analysis/sectors
   → 주력 섹터 확인

3. 애플리케이션 대시보드
   → 종목별 분석 결과 조회
```

### 투자 기회 발굴
```
1. 관심 종목 선택

2. /api/analysis/classify
   → LEADER/FOLLOWER 확인

3. LEADER라면:
   - /api/analysis/trade-plan
     → 구체적 매매 계획 수립
   
   - /api/analysis/risk-assessment
     → 위험도 평가
```

---

## 📈 베타 기간 계획

| 기간 | 목표 | 사용자 |
|---|---|---|
| **2026.2.21~3.7** | 기능 검증 | 5명 |
| **2026.3.8~3.31** | 개선 & 최적화 | 50명 |
| **2026.4+** | 상용 출시 | 무제한 |

---

## 🚀 빠른 시작

### 1. 설치
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
```

### 2. 서버 시작
```bash
# Windows
start_backend.bat

# Mac/Linux
python -m uvicorn server_v2:app --reload --host 0.0.0.0 --port 8000
```

### 3. 접속
```
http://localhost:8000
```

---

## 📖 문서

### 사용자 문서
- **[PUBLIC_API_GUIDE.md](PUBLIC_API_GUIDE.md)** - API 사용 설명서
- **[BETA_TESTER_GUIDE.md](BETA_TESTER_GUIDE.md)** - 베타테스터 가이드

### 개발 문서
- **[BETA_DEPLOYMENT_CHECKLIST.md](BETA_DEPLOYMENT_CHECKLIST.md)** - 배포 계획
- **[SCALABILITY_ANALYSIS.md](SCALABILITY_ANALYSIS.md)** - 확장 계획

---

## 🔐 데이터 보안

- **사용자 데이터**: SQLAlchemy ORM으로 안전하게 관리
- **비밀번호**: bcrypt로 해싱 (복호화 불가)
- **API 통신**: JWT 토큰 (24시간 유효)
- **API 키**: 환경변수에 저장 (.env)

---

## 💡 핵심 특징

### ✅ 설명 가능한 AI
```
"왜 LEADER인가?"
→ 신뢰도 92%의 근거 기반 판단
→ 자동 생성된 매매 계획
→ 자동 생성된 반대 의견
```

### ✅ 실시간 데이터
```
Yahoo Finance: 실시간 시세
OpenDART: 최신 공시정보
Market Breadth: 시장 전체 상황
```

### ✅ 사용자 맞춤화
```
투자 성향: 보수/중립/공격
투자 기간: 단기/중기/장기
계좌 규모: 자동 포지션 계산
```

---

## 📊 성능

| 항목 | 목표 |
|---|---|
| **API 응답** | < 5초 |
| **동시 사용자** | 5-10명 (베타) |
| **메모리 사용** | < 300MB |
| **가용성** | 99% |

---

## 🔄 피드백

베타 기간 중 문제 발생 시:

1. **버그**: GitHub Issues 또는 이메일
2. **기능 요청**: Discord/Slack 채널
3. **긴급 문제**: 직접 연락처

---

## 📞 연락처

- **문제 보고**: support@stockradar.ai
- **피드백**: feedback@stockradar.ai
- **긴급**: crisis@stockradar.ai

---

## 📄 라이선스

**Proprietary Beta** - 베타테스터만 사용 권한

---

## 🙏 감사말

이 프로젝트는 **신뢰도 높은 투자 의사결정**을 위해 만들어졌습니다.

모든 추천은 참고만 하시고, **최종 투자 결정은 본인의 판단**으로 하시기 바랍니다.

**행운을 빕니다! 📈**

---

**Version**: 1.0.0-beta  
**Last Updated**: 2026년 2월 21일
