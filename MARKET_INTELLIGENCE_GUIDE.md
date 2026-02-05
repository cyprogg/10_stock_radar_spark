# 📺 시장 해설 생성 (Market Intelligence) 사용 가이드

## 🎯 개요

**시장 해설 생성**은 Decision Stream의 `index.html` 대시보드에서 제공하는 기능으로, 현재 시장 상황을 종합적으로 분석하여 자동으로 해설을 생성합니다.

---

## 📍 위치

**파일**: `index.html` (Decision Stream 통합 대시보드)

**섹션**: "5) 📺 Market Intelligence"

---

## 🚀 사용 방법 (단계별)

### 준비 사항

1. **백엔드 서버 실행** (필수!)
   ```bash
   cd backend
   python server.py
   ```
   
2. **프론트엔드 서버 실행** (권장)
   ```bash
   # 프로젝트 루트 폴더에서
   python -m http.server 8000
   ```
   
3. 브라우저에서 `http://localhost:8000/index.html` 열기

---

### STEP 1: Regime 조회

1. 페이지 상단의 **"1) 🌡️ Market Regime"** 섹션 찾기
2. **"Regime 조회"** 버튼 클릭
3. 결과 확인:
   ```
   State: RISK_ON
   Risk Score: 72
   Playbook: 눌림 매수
   Drivers: 금리 안정, 외국인 순매수
   ```

---

### STEP 2: Sectors 조회

1. **"2) 🔥 Sector Heatmap"** 섹션으로 이동
2. **"Sectors 조회"** 버튼 클릭
3. SURGE 섹터 확인:
   ```
   방산: 97 (SURGE)
   헬스케어: 96 (SURGE)
   AI 반도체: 46 (NORMAL)
   ```

---

### STEP 3: 섹터 클릭

1. **SURGE 상태인 섹터 클릭** (예: **방산**)
2. 자동으로 Stock Funnel 데이터 로드됨:
   ```
   Leader: 없음
   Follower: LMT, 012450 (한화에어로스페이스)
   No-Go: 없음
   ```

---

### STEP 4: 시장 해설 생성

1. **"5) 📺 Market Intelligence"** 섹션으로 스크롤
2. **"▶ 시장 해설 생성"** 버튼 클릭
3. **자동으로 생성된 해설 확인**:

```
📊 Decision Stream 시장 해설

현재 시장은 RISK_ON이며 Risk Score는 72입니다.
이는 자금이 위험자산으로 이동 중인 전형적인 Risk-On 국면입니다.

자금 흐름
현재 기관 자금은 방산, 헬스케어 섹터로 집중되고 있습니다.

종목 구조
선도주: 없음
Follower: LMT, 012450

이는 섹터는 이미 움직였고, 종목들은 아직 본격적인 돌파 전인 
최적의 매집 구간을 의미합니다.

전략
방산 → 눌림 매수 대기

한 줄 요약
"공격 자금이 활발한 시장입니다."
```

---

## ⚠️ 주의사항

### 1. "먼저 섹터를 선택하세요" 오류

**원인**: Regime → Sectors → 섹터 클릭 순서를 지키지 않음

**해결**:
```
✅ 올바른 순서:
1. Regime 조회
2. Sectors 조회
3. SURGE 섹터 클릭 (예: 방산)
4. 시장 해설 생성
```

### 2. 백엔드 서버 미실행

**증상**: 
- "Regime 조회" 클릭 시 응답 없음
- 콘솔에 네트워크 에러

**해결**:
```bash
cd backend
python server.py

# 출력 확인:
# INFO:     Uvicorn running on http://127.0.0.1:8125
```

### 3. CORS 에러 (file:// 프로토콜)

**증상**: 콘솔에 "CORS policy" 에러

**해결**: 로컬 서버 사용
```bash
python -m http.server 8000
# 브라우저: http://localhost:8000/index.html
```

---

## 🎨 해설 내용 구성

시장 해설은 다음 요소들을 포함합니다:

### 1. Market Regime
- 현재 상태 (RISK_ON / RISK_OFF)
- Risk Score (0-100)
- 시장 국면 설명

### 2. 자금 흐름
- SURGE 상태 섹터 목록
- 기관 자금 이동 방향

### 3. 종목 구조
- Leader (선도주)
- Follower (추종주)
- 시장 단계 분석

### 4. 전략 제안
- 선택된 섹터의 매매 전략
- 진입 타이밍

### 5. 한 줄 요약
- 시장 성격을 한 문장으로 요약

---

## 🔄 실전 활용 플로우

```
1. index.html 열기
   ↓
2. Regime 조회 (시장 분위기 파악)
   ↓
3. Sectors 조회 (자금 흐름 파악)
   ↓
4. SURGE 섹터 클릭 (집중 분석)
   ↓
5. Stock Funnel 확인 (종목 분류)
   ↓
6. 시장 해설 생성 (종합 분석)
   ↓
7. Trade Plan으로 이동 (구체적 계획 수립)
```

---

## 🧪 테스트 시나리오

### 시나리오 1: Risk-On 장 (정상 케이스)

```
1. Regime 조회
   → State: RISK_ON, Risk Score: 72

2. Sectors 조회
   → 방산: 97 (SURGE)
   → 헬스케어: 96 (SURGE)

3. "방산" 클릭
   → Follower: LMT, 012450

4. 시장 해설 생성
   → "공격 자금이 활발한 시장입니다."
```

### 시나리오 2: Risk-Off 장

```
1. Regime 조회
   → State: RISK_OFF, Risk Score: 35

2. Sectors 조회
   → 대부분 NORMAL

3. 섹터 선택 어려움
   → 방어적 접근 필요

4. 시장 해설 생성
   → "방어적 관점이 필요한 시장입니다."
```

---

## 🐛 문제 해결

### Q1. "시장 해설 생성" 버튼이 안 보여요

**A**: 스크롤을 아래로 내리세요. "5) 📺 Market Intelligence" 섹션은 페이지 중간에 있습니다.

### Q2. 버튼을 눌러도 아무 반응이 없어요

**A**: 
1. F12 → Console 탭 확인
2. 에러 메시지 확인
3. 백엔드 서버 실행 여부 확인
4. Regime/Sectors/섹터 클릭 순서 확인

### Q3. "먼저 섹터를 선택하세요" 알림이 떠요

**A**: 
```javascript
// 필요한 데이터가 로드되지 않음
// 순서대로 다시 실행:
1. Regime 조회
2. Sectors 조회
3. SURGE 섹터 클릭
4. 시장 해설 생성
```

### Q4. 섹터를 클릭했는데 반응이 없어요

**A**: 
- Sectors 조회를 먼저 했는지 확인
- 콘솔에서 에러 확인
- 백엔드 서버 실행 확인

---

## 💡 팁

### 1. 빠른 분석
```
Regime → Sectors → SURGE 섹터 클릭 → 해설 생성
(약 10초 소요)
```

### 2. 여러 섹터 비교
```
1. 방산 클릭 → 해설 생성 → 내용 확인
2. 헬스케어 클릭 → 해설 생성 → 내용 확인
3. 두 섹터 비교하여 최적 선택
```

### 3. Trade Plan 연동
```
시장 해설 생성
   ↓
Follower 종목 확인 (예: 012450)
   ↓
"Trade Plan" 섹션으로 이동
   ↓
종목 입력 → 계획 생성
```

---

## 📸 스크린샷 가이드

### 위치 확인

```
index.html 구조:

[1) Market Regime]
[2) Sector Heatmap]
[3) Stock Funnel]
[4) Checklist]
[5) 📺 Market Intelligence]  ← 여기!
    "시장 해설을 생성하려면 버튼을 클릭하세요."
    [▶ 시장 해설 생성]
[6) Trade Plan]
```

---

## 🎓 학습 순서

### 초급 (처음 사용)
1. 백엔드 서버 실행 배우기
2. Regime → Sectors → 섹터 클릭 순서 익히기
3. 시장 해설 생성 연습

### 중급 (익숙해진 후)
1. 각 섹터별 해설 비교
2. Risk Score 변화에 따른 전략 차이 이해
3. Leader/Follower 구조 분석

### 고급 (숙련자)
1. 시장 해설 → Trade Plan 통합 워크플로우
2. 여러 시나리오 시뮬레이션
3. 실전 투자 의사결정에 활용

---

## 📚 관련 문서

- [README.md](README.md) - 프로젝트 전체 개요
- [MARKET_ANALYSIS_GUIDE.md](MARKET_ANALYSIS_GUIDE.md) - 시장 분석 해석 가이드
- [QUICKSTART.md](QUICKSTART.md) - 빠른 시작 가이드

---

## 🎯 요약

**시장 해설 생성 = 원클릭 시장 분석 리포트**

```
필수 조건:
✅ 백엔드 서버 실행 (python server.py)
✅ Regime 조회 완료
✅ Sectors 조회 완료
✅ 섹터 선택 완료

클릭 한 번:
"▶ 시장 해설 생성"

결과:
📊 현재 시장 상황 종합 분석 리포트
```

---

© 2026 Decision Stream - 중기 스윙 투자 프레임워크
