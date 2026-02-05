# 📋 두 체크리스트의 차이점과 역할

## 🤔 질문: 왜 두 체크리스트가 다른가?

**답변**: 두 체크리스트는 **목적, 시점, 깊이가 다릅니다**. 같은 체크리스트가 아니라 **의사결정의 다른 단계**를 검증합니다.

---

## 📊 비교표

| 구분 | index.html 체크리스트 | trade_plan_simulation.html 체크리스트 |
|-----|---------------------|----------------------------------|
| **위치** | Watch & Checklist 카드 | 결과 영역 (매매 계획 하단) |
| **목적** | **진입 가능 여부 판단** | **전략 타당성 검증** |
| **시점** | 종목 선택 직후 (사전 스크리닝) | 매매 계획 생성 후 (사후 검증) |
| **항목 수** | **5개** (Safety Checklist) | **7개** (9요소 간소화 버전) |
| **질문** | "사면 안 되는 이유가 있는가?" | "이 전략이 타당한가?" |
| **결과** | State 결정 (BUY_NOW/WATCH/NO_GO 등) | Risk Warning (진입 조건 평가) |
| **영향** | Trade Plan 생성 여부 결정 | 포지션 크기/신중도 조정 |

---

## 1️⃣ index.html - Safety Checklist (5개)

### 위치
```javascript
function checkSafetyChecklist(stock, funnelType) {
  /**
   * 5가지 체크리스트
   * "사면 안 되는 이유가 있는가?"
   */
  const checks = {
    priceStructure: false,  // 가격 구조 (과열/이격 없음)
    volume: false,          // 거래량 정상
    volatility: false,      // 변동성 안정
    eventRisk: false,       // 이벤트 리스크 없음
    pullback: false         // 구조적 눌림
  };
  // ...
}
```

### 목적
**"이 종목을 지금 매수 리스트에 올려도 되는가?"**

- ❌ 구조적 문제가 있으면 → 배제
- ✅ 통과하면 → Trade Plan 생성

### 체크 항목 (5개)

| 항목 | 의미 | 실패 시 |
|-----|------|--------|
| 🏗️ **가격 구조** | 과열/이격 없음 | 추격 리스크 |
| 📊 **거래량** | 거래량 정상 | 유동성 리스크 |
| 📈 **변동성** | 변동성 안정 | 손절 어려움 |
| ⚠️ **이벤트 리스크** | 이벤트 리스크 없음 | 갑작스런 악재 |
| 📉 **구조적 눌림** | 구조적 눌림 구간 | 타이밍 부적절 |

### 판정 기준
```javascript
const passCount = Object.values(checks).filter(v => v).length;

if (passCount === 5) → checklistLevel = 'Strong'
if (passCount === 4) → checklistLevel = 'Medium'
else                 → checklistLevel = 'Weak'
```

### State 결정 로직
```javascript
function determineState(funnelType, checklistLevel) {
  if (funnelType === 'LEADER') {
    if (checklistLevel === 'Strong')  → 'BUY_NOW'      // 즉시 매수 가능
    if (checklistLevel === 'Medium')  → 'BUY_PULLBACK' // 눌림 대기
    else                              → 'HOLD_OFF'      // 보류
  }
  
  if (funnelType === 'FOLLOWER') {
    if (checklistLevel === 'Strong')  → 'ACCUMULATE'   // 선제 매집
    if (checklistLevel === 'Medium')  → 'WATCH'        // 관찰
    else                              → 'HOLD_OFF'      // 보류
  }
}
```

### 역할
- **Gatekeeper** (문지기)
- "이 종목을 더 깊이 검토할 가치가 있는가?"
- ❌ 5개 중 2개 이하 통과 → Trade Plan 생성하지 않음
- ✅ 3개 이상 통과 → Trade Plan 생성 진행

---

## 2️⃣ trade_plan_simulation.html - 7요소 체크리스트

### 위치
```javascript
// Line 1201-1243
const checklistItems = [
  { name: '수급 신호', pass: ..., detail: '외국인/기관 누적 매수 확인' },
  { name: '정책/테마', pass: ..., detail: '확정·지속·실적연결 뉴스' },
  { name: '시장 사이클', pass: ..., detail: 'MA20 상향, 변동성 정상' },
  { name: '기업 질', pass: ..., detail: '부채비율, 실적 안정성' },
  { name: '서사', pass: ..., detail: '장기 성장 스토리 존재' },
  { name: '하방 리스크', pass: ..., detail: '과열 신호 없음' },
  { name: '시간 적합성', pass: ..., detail: '조정 후 진입 구간' }
];
```

### 목적
**"이 매매 계획(전략)이 타당한가?"**

- 매매 계획이 **이미 생성된 후**
- 전략의 강점과 약점 파악
- 포지션 크기 조정 힌트

### 체크 항목 (7개) - 9요소 프레임워크의 간소화 버전

| 항목 | 의미 | 9요소 연결 |
|-----|------|----------|
| 💰 **수급 신호** | 외국인/기관 누적 매수 | 자금 흐름 |
| 📰 **정책/테마** | 확정·지속·실적연결 뉴스 | 서사 + 사이클 |
| 🔄 **시장 사이클** | MA20 상향, 변동성 정상 | 사이클 + 모멘텀 품질 |
| 💎 **기업 질** | 부채비율, 실적 안정성 | 기업의 질 |
| 📖 **서사** | 장기 성장 스토리 존재 | 서사 |
| ⚠️ **하방 리스크** | 과열 신호 없음 | 하방 리스크 |
| ⏰ **시간 적합성** | 조정 후 진입 구간 | 시간 적합성 |

### 판정 기준
```javascript
const passCount = checklistItems.filter(i => i.pass).length;

if (passCount >= 6) → '체크리스트 통과! 손절가 엄수하고 20일선 관리'
if (passCount >= 4) → '일부 조건 미달. 포지션 크기 줄이고 신중 접근'
else                → '⚠️ 진입 조건 미달! 관망 권장'
```

### 역할
- **Strategy Validator** (전략 검증자)
- "이 전략이 얼마나 견고한가?"
- ❌ 4개 미만 통과 → 포지션 축소 또는 관망
- ✅ 4-5개 통과 → 보수적 진입
- ✅✅ 6개 이상 통과 → 정상 진입

---

## 🔄 두 체크리스트의 관계

### 의사결정 흐름

```
1. index.html - Safety Checklist (5개)
   ↓
   "이 종목이 매수 후보군에 올라갈 자격이 있는가?"
   ↓
   ❌ 2개 이하 통과 → HOLD_OFF (Trade Plan 생성 안 함)
   ✅ 3개 이상 통과 → Trade Plan 생성
   ↓
   
2. 사용자가 "상세 시뮬레이션 열기" 클릭
   ↓
   
3. trade_plan_simulation.html - 7요소 체크리스트
   ↓
   "이 매매 계획(전략)의 타당성은?"
   ↓
   ❌ 3개 이하 → 관망 권장
   ⚠️ 4-5개 → 포지션 축소
   ✅ 6개 이상 → 정상 진입
```

### 비유

**index.html (5개)**: **1차 서류 심사**
- "이 지원자가 면접을 볼 자격이 있는가?"
- 자격 미달 → 탈락
- 자격 충족 → 면접 진행

**trade_plan_simulation.html (7개)**: **면접 및 최종 평가**
- "이 지원자의 구체적인 강점과 약점은?"
- 약점 많음 → 낮은 직급 제안
- 강점 많음 → 높은 직급 제안

---

## 📐 설계 철학

### 1. 두 단계 검증 (Two-Stage Validation)

**Why?**
- 모든 종목을 7요소로 검증하면 **과부하**
- 5개 Safety Checklist로 먼저 **필터링**
- 통과한 종목만 **깊이 있게 분석**

**Benefit:**
- ⚡ 빠른 스크리닝
- 🎯 집중된 분석
- 💡 효율적 의사결정

### 2. 간결함 vs 완전함 (Simplicity vs Completeness)

**index.html (5개)**: 
- 최소한의 체크 (빠른 판단)
- "사면 안 되는 이유" 집중

**trade_plan_simulation.html (7개)**:
- 9요소 프레임워크의 간소화 버전
- "전략의 강점/약점" 파악

### 3. 행동 지향 (Action-Oriented)

**index.html**:
- 결과: State (BUY_NOW, WATCH, HOLD_OFF)
- → 즉시 행동 가능한 신호

**trade_plan_simulation.html**:
- 결과: Risk Warning (조건 통과/미달)
- → 포지션 크기 조정

---

## 💡 FAQ

### Q1: 왜 체크리스트를 통일하지 않았나?
**A**: 목적이 다르기 때문입니다.
- index.html: 빠른 스크리닝 (5개면 충분)
- simulation.html: 전략 검증 (7개 필요)

### Q2: 5개와 7개의 항목이 겹치는가?
**A**: 부분적으로 겹치지만 **관점이 다릅니다**.

**겹치는 영역**:
- 가격 구조 ≈ 시장 사이클
- 변동성 ≈ 하방 리스크
- 구조적 눌림 ≈ 시간 적합성

**다른 영역**:
- index.html: 거래량, 이벤트 리스크 (기술적 위험)
- simulation.html: 수급 신호, 정책/테마, 기업 질, 서사 (펀더멘털 + 모멘텀)

### Q3: 둘 다 통과해야 매수하는가?
**A**: 논리적으로는 Yes, 실전에서는 상황 판단.

**이상적 시나리오**:
1. index.html Safety Checklist: 5/5 또는 4/5 통과 → BUY_NOW
2. simulation 7요소: 6-7개 통과 → 정상 진입

**현실적 시나리오**:
- index.html 4/5 + simulation 5/7 → 보수적 진입 (포지션 축소)
- index.html 3/5 + simulation 4/7 → 관망 또는 소량 테스트

### Q4: 체크리스트 통과율이 낮으면?
**A**: **무조건 안 사는 게 아니라**, 접근 방식을 조정.

| 통과율 | 행동 |
|-------|------|
| 낮음 (< 50%) | 관망 / Pass |
| 중간 (50-70%) | 포지션 축소 (10-15%) |
| 높음 (> 70%) | 정상 진입 (20-25%) |

---

## 🎯 실전 예시

### 예시 1: 한화에어로스페이스 (012450)

**Step 1: index.html Safety Checklist**
```
✅ 가격 구조: 과열 없음
✅ 거래량: 정상
✅ 변동성: 안정
✅ 이벤트 리스크: 없음
✅ 구조적 눌림: Yes

→ 5/5 통과 → checklistLevel = 'Strong'
→ LEADER + Strong → State = 'BUY_NOW'
→ Trade Plan 생성!
```

**Step 2: 상세 시뮬레이션 클릭**

**Step 3: trade_plan_simulation.html 7요소**
```
✅ 수급 신호: 기관 매수 지속
✅ 정책/테마: 방산 정책 확정
✅ 시장 사이클: 상승 추세
✅ 기업 질: 실적 안정
✅ 서사: 방산 수출 성장 스토리
⚠️ 하방 리스크: 단기 과열 우려
✅ 시간 적합성: 눌림 매수 구간

→ 6/7 통과
→ Risk Warning: "체크리스트 통과! 손절가 엄수하고 20일선 관리"
→ 정상 포지션 (25%) 진입 가능
```

**결론**: 
- ✅ 1차 스크리닝 통과
- ✅ 2차 검증 통과
- 🟢 진입 조건 충족
- 📊 포지션 25%, 손절 -8%, 목표 +20%

---

### 예시 2: 가상 종목 "급등주X"

**Step 1: index.html Safety Checklist**
```
❌ 가격 구조: 단기 급등 (이격 과도)
❌ 거래량: 폭증 (불안정)
⚠️ 변동성: 높음
❌ 이벤트 리스크: 단일 뉴스 의존
✅ 구조적 눌림: N/A

→ 1/5 통과 → checklistLevel = 'Weak'
→ State = 'HOLD_OFF' 또는 'NO_GO'
→ Trade Plan 생성 안 함 (또는 경고 포함 생성)
```

**결론**:
- ❌ 1차 스크리닝 실패
- 🔴 상세 시뮬레이션 불필요
- ⛔ 진입 금지

---

## 📚 관련 문서

1. **TRADING_CHECKLIST_SHORT_MID_TERM.md** - 완전한 0-8단계 체크리스트
2. **INVESTMENT_FRAMEWORK_9_FACTORS.md** - 9요소 철학
3. **AI_AGENT_ARCHITECTURE.md** - Stock Screener 설계
4. **TRADE_PLAN_INTEGRATION.md** - Seamless 통합 가이드

---

## 🎓 핵심 정리

### 두 체크리스트는...

| | index.html | trade_plan_simulation.html |
|---|-----------|---------------------------|
| **역할** | Gatekeeper (문지기) | Validator (검증자) |
| **질문** | "사면 안 되는가?" | "전략이 타당한가?" |
| **시점** | 종목 선택 직후 | 매매 계획 생성 후 |
| **결과** | 진입 가능 여부 | 전략 강도 평가 |
| **행동** | Trade Plan 생성 | 포지션 크기 조정 |

### 왜 두 개인가?

1. **효율성**: 모든 종목을 깊이 분석하지 않음
2. **명확성**: 각 단계의 목적이 분명함
3. **실용성**: 빠른 판단 + 신중한 검증

### 사용자는 어떻게 이해해야 하나?

**"1차 서류 심사 → 2차 면접"** 처럼
1. index.html: 빠른 필터링 (5개)
2. simulation.html: 깊이 있는 분석 (7개)

**둘 다 중요하지만, 역할이 다릅니다!**

---

**작성일**: 2026-01-27  
**버전**: v1.0  
**상태**: ✅ 완료
