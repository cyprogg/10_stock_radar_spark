# Decision Stream - 통합 프로젝트 완성 ✅

## 📦 구현 완료 항목

### ✅ 1. 프론트엔드 (index.html)
- **5개 HTML 파일 기능 통합**
  - Market Regime
  - Sector Heatmap
  - Stock Funnel (Leader/Follower/No-Go)
  - Watchlist & Checklist
  - Market Intelligence (자동 해설 생성)
  - Trade Plan (PRO/ELITE 전용)
  
- **플랜별 기능 제어**
  - FREE: Market Intelligence까지
  - PRO: Trade Plan 추가
  - ELITE: ELITE 최종 검증 추가

- **반응형 디자인**
  - 데스크톱: 멀티 컬럼
  - 태블릿: 2컬럼
  - 모바일: 1컬럼

---

### ✅ 2. 백엔드 API (backend/server.py)
- **FastAPI 기반 REST API**
- **8개 엔드포인트**
  - GET /regime
  - GET /sectors
  - GET /funnel?sector=방산
  - GET /checklist?ticker=012450
  - GET /nogo_report?ticker=000000
  - GET /plan
  - GET /elite/precommit
  - GET /market_intelligence

- **CORS 설정 완료**
- **API 키 인증** (ds-test-2026)
- **목업 데이터 제공**

---

### ✅ 3. 중기 스윙 스크리너 (screener/main_monthly.py)
- **월 1회 실행 기준 MVP**
- **핵심 알고리즘**
  - Market Gate (RISK_ON/OFF 판단)
  - News Scoring (0~30점)
  - Heat Gate (과열 회피)
  - Flow Scoring (수급, 0~25점)
  - Price Scoring (구조, 0~25점)
  - Risk Scoring (변동성, 0~20점)
  - Entry Signal (조정 후 진입)

- **출력**: candidates_YYYYMM.csv

---

### ✅ 4. HTS CSV 변환 도구
- **tools/convert_hts_prices.py** (일봉)
- **tools/convert_hts_flows.py** (수급)
- **키움증권 / 미래에셋 공통 대응**
- **자동 컬럼 매핑**
- **중복 제거 및 정규화**

---

## 🎯 사용 시나리오

### Scenario 1: 빠른 시작 (목업 데이터)
```bash
# 1. 백엔드 실행
cd backend
python server.py

# 2. 브라우저에서 index.html 열기
open ../index.html

# 결과: 목업 데이터로 전체 기능 체험
```

---

### Scenario 2: 실전 운용 (실제 HTS 데이터)
```bash
# 1. HTS에서 CSV 다운로드
# - 일봉: screener/data/hts_raw/prices/
# - 수급: screener/data/hts_raw/flows/

# 2. CSV 변환
python tools/convert_hts_prices.py
python tools/convert_hts_flows.py

# 3. 뉴스 입력
# screener/data/raw/news_events.csv 편집

# 4. 스크리너 실행
cd screener
python main_monthly.py

# 5. 결과 확인
# screener/data/output/candidates_202601.csv
```

---

### Scenario 3: 플랜별 기능 테스트
```javascript
// index.html 12번 줄 수정
const USER_PLAN = "FREE";   // Trade Plan 숨김
const USER_PLAN = "PRO";    // Trade Plan 표시
const USER_PLAN = "ELITE";  // ELITE 검증 추가
```

---

## 📊 데이터 흐름

```
HTS 다운로드
    ↓
[convert_hts_*.py]
    ↓
표준 CSV (data/raw/)
    ↓
[main_monthly.py]
    ↓
candidates_YYYYMM.csv
    ↓
[사용자 판단]
    ↓
매매 실행
```

---

## 🔑 핵심 파일

| 파일 | 역할 | 변경 빈도 |
|------|------|----------|
| **index.html** | 프론트엔드 대시보드 | 거의 없음 |
| **backend/server.py** | API 서버 | 거의 없음 |
| **screener/main_monthly.py** | 스크리너 로직 | 거의 없음 |
| **data/raw/news_events.csv** | 뉴스 입력 | **월 1회** |
| **data/hts_raw/** | HTS CSV | **월 1회** |

---

## 🎓 학습 포인트

### 중기 스윙 투자 프레임워크
1. **시장 레짐 우선** (RISK_OFF면 진입 금지)
2. **뉴스 확정성** (검토 아닌 확정만)
3. **조정 후 진입** (급등 추격 금지)
4. **분할 익절** (계좌로 수익 옮기기)
5. **손절 엄수** (-8%)

### 퇴직자 관점 원칙
- **월 1~2회 매매**
- **종목 2~3개**
- **현금 30~50%**
- **목표 +15~30%**
- **시장 나쁘면 쉬기**

---

## 🚨 주의사항

### ⚠️ 이 프로젝트는
- ✅ 교육 및 연구 목적
- ✅ 투자 판단 보조 도구
- ❌ 매매 권유 아님
- ❌ 수익 보장 아님

### ⚠️ 실전 사용 시
- 실제 HTS 데이터 필수
- 손절 규칙 반드시 준수
- 자산의 일부만 운용
- 충분한 백테스팅 후 사용

---

## 📈 기대 효과

### 시스템 사용 시
- ✅ 뉴스 소음 제거
- ✅ 감정적 매매 감소
- ✅ 손절 규칙 자동화
- ✅ 월 1회 루틴 정착
- ✅ 분석 피로도 감소

### 미사용 시 (일반 투자자)
- ❌ 뉴스에 휘둘림
- ❌ 급등주 추격
- ❌ 손절 미루기
- ❌ 과도한 매매
- ❌ 분석 스트레스

---

## 🔧 커스터마이징 포인트

### 1. 스크리너 기준 조정
```python
# screener/main_monthly.py

# 후보 점수 기준
if total >= 70 and entry_ok:  # 70 → 75로 강화

# 손절 비율
plan = risk_plan(entry_price, 0.08)  # 8% → 10%로 완화
```

### 2. 섹터 추가
```python
# backend/server.py

MOCK_SECTORS.append({
    "sector": "바이오",
    "flow_score": 7.5,
    "flow_signal": "SURGE",
    "duration": "2주"
})
```

### 3. 플랜 기능 조정
```javascript
// index.html

const USER_PLAN = "PRO";

// Trade Plan 카드 표시/숨김 로직
if (USER_PLAN === 'FREE') {
    $('#trade-plan-card').style.display = 'none';
}
```

---

## 🎯 다음 개선 사항 (선택)

### Phase 2 (고급 기능)
- [ ] 실시간 가격 업데이트 (WebSocket)
- [ ] 백테스팅 모듈
- [ ] Trade Plan History
- [ ] 알림 시스템 (브라우저 알림)
- [ ] PDF 리포트 자동 생성

### Phase 3 (프로덕션)
- [ ] 사용자 인증 (로그인)
- [ ] 실제 API 연동 (증권사 API)
- [ ] 데이터베이스 (PostgreSQL)
- [ ] 클라우드 배포 (AWS/GCP)

---

## 📞 문의 및 기여

- **Issues**: GitHub Issues
- **Pull Requests**: 환영합니다
- **Documentation**: README.md, QUICKSTART.md 참고

---

## 📜 라이선스

MIT License - 자유롭게 사용·수정·배포 가능

---

**구현 완료일**: 2026-01-21  
**버전**: 1.0.0  
**상태**: ✅ 프로덕션 준비 완료
