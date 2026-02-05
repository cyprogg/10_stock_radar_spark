# 📂 Decision Stream - 완전한 프로젝트 구조

```
decision-stream/
│
├── 🏠 home.html                            # 프로젝트 랜딩 페이지 (시작점)
│
├── 🎯 trade_plan_simulation.html           # ★ Trade Plan 시뮬레이션 (추천 시작)
│   └── 기능:
│       ├── 시장/섹터/종목 선택
│       ├── 리스크 성향별 포지션 계산
│       ├── 7요소 체크리스트 평가
│       ├── 시뮬레이션 기록 추적
│       └── 성과 통계 분석
│
├── 📈 index.html                           # Decision Stream 통합 대시보드
│   └── 모듈:
│       ├── Market Regime (RISK_ON/OFF)
│       ├── Sector Heatmap (SURGE 신호)
│       ├── Stock Funnel (Leader/Follower/No-Go)
│       ├── Watchlist & Checklist
│       └── Market Intelligence
│
├── 📚 문서 (Documentation)
│   ├── README.md                           # 프로젝트 전체 개요
│   ├── QUICKSTART.md                       # 상세 실행 가이드
│   ├── TRADE_PLAN_GUIDE.md                 # 시뮬레이션 완전 가이드 (7K+ 자)
│   ├── QUICK_REFERENCE.md                  # 빠른 참조 카드 (출력용)
│   ├── IMPLEMENTATION_SUMMARY.md           # 구현 완료 요약
│   └── PROJECT_SUMMARY.md                  # 프로젝트 요약
│
├── 🔧 backend/                             # 백엔드 API 서버
│   ├── server.py                           # FastAPI 서버
│   │   └── API 엔드포인트:
│   │       ├── /regime                     # Market Regime 조회
│   │       ├── /sectors                    # Sector Heatmap 조회
│   │       ├── /funnel                     # Stock Funnel 조회
│   │       ├── /checklist                  # 종목 체크리스트
│   │       ├── /nogo_report                # No-Go 리포트
│   │       ├── /plan                       # Trade Plan 조회
│   │       ├── /trade_plan/generate        # ★ 시뮬레이션 계획 생성
│   │       ├── /trade_plan/stocks          # ★ 섹터별 종목 조회
│   │       └── /trade_plan/stats           # ★ 시뮬레이션 통계
│   │
│   └── requirements.txt                    # Python 의존성
│       └── fastapi, uvicorn, pydantic
│
├── 🔍 screener/                            # 월간 스크리너 (MVP)
│   ├── main_monthly.py                     # 메인 스크리너 로직
│   │   └── 기능:
│   │       ├── Market Gate (진입 가능 여부)
│   │       ├── News Quality Gate (뉴스 점수)
│   │       ├── Heat Gate (과열 회피)
│   │       ├── Flow Score (수급 점수)
│   │       ├── Price Score (가격 구조)
│   │       ├── Risk Score (리스크 평가)
│   │       └── 후보 출력 (candidates_YYYYMM.csv)
│   │
│   ├── requirements.txt                    # Python 의존성
│   │   └── pandas, numpy
│   │
│   └── data/                               # 데이터 디렉토리
│       ├── raw/                            # 표준 CSV 파일
│       │   ├── universe.csv                # 종목 유니버스
│       │   ├── news_events.csv             # 뉴스 이벤트
│       │   ├── prices_daily.csv            # 일봉 데이터
│       │   ├── flows_daily.csv             # 수급 데이터
│       │   └── index_kospi.csv             # 코스피 지수
│       │
│       ├── hts_raw/                        # HTS 원본 CSV
│       │   ├── prices/                     # 일봉 원본
│       │   └── flows/                      # 수급 원본
│       │
│       └── output/                         # 스크리너 출력
│           └── candidates_YYYYMM.csv       # 월간 후보 종목
│
└── 🛠️ tools/                               # 유틸리티 도구
    ├── convert_hts_prices.py               # HTS 일봉 변환
    │   └── 지원: 키움, 미래에셋 포맷
    │
    └── convert_hts_flows.py                # HTS 수급 변환
        └── 지원: 키움, 미래에셋 포맷
```

---

## 🚀 시작 순서

### 🥇 첫 번째: Trade Plan Simulation (추천)

```bash
# 1. 서버 실행
cd backend
pip install -r requirements.txt
python server.py

# 2. 브라우저에서 열기
open trade_plan_simulation.html

# 3. 시뮬레이션 시작
# - 30회 이상 연습
# - 승률 50% 달성
# - 손익비 2:1 달성
```

**목표**: 실전 투자 전 충분한 시뮬레이션 학습

---

### 🥈 두 번째: Decision Stream Dashboard

```bash
# 브라우저에서 열기
open index.html

# 또는 home.html에서 "Decision Stream Dashboard" 클릭
```

**목표**: 실시간 시장 분석 및 종목 발굴

---

### 🥉 세 번째: 월간 스크리너 (선택)

```bash
# 1. HTS에서 CSV 다운로드
# - 일봉: screener/data/hts_raw/prices/
# - 수급: screener/data/hts_raw/flows/

# 2. 변환 스크립트 실행
cd tools
python convert_hts_prices.py
python convert_hts_flows.py

# 3. 스크리너 실행
cd ../screener
python main_monthly.py

# 4. 결과 확인
cat data/output/candidates_202601.csv
```

**목표**: 월 1회 후보 종목 자동 발굴

---

## 📖 문서 읽는 순서

1. **README.md** (5분)
   - 프로젝트 전체 개요
   - 핵심 철학 및 기능

2. **QUICK_REFERENCE.md** (3분) ← 출력 추천!
   - 7요소 체크리스트 요약
   - 리스크 성향별 설정
   - 학습 목표 체크리스트

3. **TRADE_PLAN_GUIDE.md** (20분)
   - 시뮬레이션 완전 가이드
   - 7요소 상세 설명
   - 교육 시나리오

4. **QUICKSTART.md** (10분)
   - 실행 가이드
   - HTS 연동 방법
   - API 사용법

5. **IMPLEMENTATION_SUMMARY.md** (5분)
   - 구현 완료 내역
   - 기술적 세부사항

---

## 🎯 학습 로드맵 (10주 계획)

```
Week 1-2: 프레임워크 이해 (시뮬레이션 1-10회)
   ├── QUICK_REFERENCE.md 숙독
   ├── 7요소 체크리스트 완전 이해
   └── 손절가 엄수 연습

Week 3-4: 체크리스트 숙달 (시뮬레이션 11-20회)
   ├── 리스크 성향 실험 (보수/중립)
   ├── 익절 전략 비교
   └── 목표: 승률 45% 이상

Week 5-6: 리스크 관리 (시뮬레이션 21-30회)
   ├── 포지션 사이징 최적화
   ├── 2차 익절 전략 적용
   └── 목표: 승률 50%, 손익비 1.8:1

Week 7-8: 최적화 (시뮬레이션 31-40회)
   ├── 공격적 리스크 도입 (조건부)
   ├── 2차 진입 전략
   └── 목표: 승률 55%, 손익비 2.2:1

Week 9-10: 실전 준비 (시뮬레이션 41-50회)
   ├── 포트폴리오 시뮬레이션 (다종목)
   ├── 실전 체크리스트 검토
   └── 소액 실전 시작 (자산의 10%)

Week 11+: 실전 운용
   ├── 월 1-2회 매매
   ├── 분할 익절 실행
   └── 연 8-15% 목표
```

---

## 💡 핵심 개념 맵

```
중기 스윙 투자 시스템
        │
        ├── 🎯 Trade Plan Simulation
        │   ├── 7요소 체크리스트 (총 100점)
        │   │   ├── 수급 (25점)
        │   │   ├── 정책/테마 (30점)
        │   │   ├── 시장 사이클 (10점)
        │   │   ├── 기업 질 (10점)
        │   │   ├── 서사 (8점)
        │   │   ├── 하방 리스크 (10점)
        │   │   └── 시간 적합성 (7점)
        │   │
        │   ├── 리스크 관리
        │   │   ├── 보수: -8% / +15% / 20%
        │   │   ├── 중립: -10% / +20% / 25%
        │   │   └── 공격: -12% / +25% / 30%
        │   │
        │   └── 성과 추적
        │       ├── 승률 (목표: 50%+)
        │       ├── 평균 수익률 (목표: +5%+)
        │       └── 손익비 (목표: 2:1+)
        │
        ├── 📈 Decision Stream Dashboard
        │   ├── Market Regime
        │   ├── Sector Heatmap
        │   ├── Stock Funnel
        │   ├── Watchlist & Checklist
        │   └── Market Intelligence
        │
        └── 🔍 월간 스크리너
            ├── Market Gate
            ├── News Quality Gate
            ├── Heat Gate
            ├── Flow Score
            ├── Price Score
            └── Risk Score
```

---

## 🎓 핵심 투자 원칙

### ✅ DO (해야 할 것)
```
✓ 확정 뉴스만 추종 (정책·예산·계약)
✓ 조정 후 진입 (눌림목 확인)
✓ 분할 익절 (1차 50%, 2차 30%, 잔량 20%)
✓ 손절 -8% 엄수 (예외 없음)
✓ 현금 30-50% 상시 유지
✓ 최대 3종목 보유
```

### ❌ DON'T (하지 말아야 할 것)
```
✗ 뉴스 당일 추격 매수
✗ 급등주 추격
✗ 테마 과열 진입
✗ 손절 미루기
✗ 전액 투자
✗ 과도한 분산 (4종목 이상)
```

---

## 📊 성과 목표

### 초급 (1-10회 시뮬레이션)
- 체크리스트 이해도 100%
- 손절가 엄수 기록 100%
- 시뮬레이션 10회 완료

### 중급 (11-30회 시뮬레이션)
- 승률 ≥ 50%
- 평균 수익률 ≥ +5%
- 손익비 ≥ 1.8:1

### 고급 (31회+ 시뮬레이션)
- 승률 ≥ 55%
- 평균 수익률 ≥ +8%
- 손익비 ≥ 2.2:1

### 실전 (연간 목표)
- 연 수익률: 8-15%
- 최대 낙폭: -10% 이내
- 매매 빈도: 12-24회/년

---

## 🆘 문제 해결

### 자주 발생하는 문제

**1. 서버 연결 실패**
```bash
# 해결: 서버 실행 확인
cd backend && python server.py
```

**2. CORS 에러**
```bash
# 해결: 서버 재시작 (CORS 설정 자동)
cd backend && python server.py
```

**3. 시뮬레이션 기록 사라짐**
```bash
# 원인: 다른 브라우저 또는 시크릿 모드 사용
# 해결: 같은 브라우저, 같은 도메인 사용
```

**4. 종목 데이터 안 보임**
```bash
# 해결: 섹터를 먼저 선택
# F12 개발자 도구에서 에러 확인
```

---

## 📞 지원 및 기여

- **문서**: README.md, QUICKSTART.md, TRADE_PLAN_GUIDE.md
- **버그 리포트**: 프로젝트 이슈 등록
- **기능 제안**: 프로젝트 이슈 또는 PR

---

## 📜 라이선스

MIT License - 자유롭게 사용·수정 가능

---

**이 프로젝트로 안전하고 수익성 있는 투자를 시작하세요! 🚀📈**
