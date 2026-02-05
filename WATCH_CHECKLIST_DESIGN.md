# Watch & Checklist 시스템 설계서

## 🎯 핵심 정의

> **Funnel은 "구조적 위치"를 말하고,**  
> **Checklist는 "지금 행동해도 되는가"를 검증한다.**
> 
> **둘 중 하나라도 불합격이면 매매 금지.**

---

## 📐 전체 의사결정 흐름

```
Market Regime (시장에 들어가도 되는가)
    ↓
Sector Heatmap (돈이 어디로 가는가)
    ↓
Stock Funnel (어떤 종목이 후보인가)
    ↓
Watch & Checklist (지금 행동해도 되는가)
    ↓
Action (Buy / Watch / Skip)
```

**Funnel = 후보를 나누는 장치**  
**Checklist = 행동을 허가하는 장치**

---

## 🎯 Decision State Engine

### **6단계 최종 상태**

| State Code | 의미 | 사용자 행동 | 색상 |
|------------|------|------------|------|
| **BUY_NOW** | 매수 허가 | 분할/즉시 진입 | 🔵 Blue |
| **BUY_PULLBACK** | 눌림 매수 대기 | 알림 설정 | 🟢 Green |
| **ACCUMULATE** | 선제 매집 | 소량 진입 | 🟡 Yellow |
| **WATCH** | 관찰 | 대기 | ⚪ Gray |
| **HOLD_OFF** | 보류 | 관망 | 🟠 Orange |
| **NO_GO** | 매수 금지 | 차단 | 🔴 Red |

---

## ✅ Checklist 5가지 항목

### **"사면 안 되는 이유"를 체크**

| 항목 | 질문 | 통과 기준 |
|------|------|----------|
| **1. 가격 구조** | 과열/이격 없는가? | RSI < 70, 고점 대비 5% 이내 |
| **2. 거래량** | 정상 범위인가? | 평균 대비 50~200% |
| **3. 변동성** | 안정적인가? | 5일 ATR < 평균 ATR × 1.5 |
| **4. 이벤트 리스크** | 악재 없는가? | 실적 발표/공시 D-7 이상 |
| **5. 구조적 눌림** | 매수 구간인가? | 20일선 지지 or 돌파 직전 |

### **Checklist 점수 기준**

- ✔ 5개: **Strong** (완벽)
- ✔ 4개: **Medium** (보통)
- ✔ 3개 이하: **Weak** (위험)

---

## 🔄 Funnel × Checklist 연동

### **1️⃣ Leader 연동**

| Funnel | Checklist | State | 행동 |
|--------|-----------|-------|------|
| Leader | Strong | **BUY_NOW** | 즉시/분할 매수 가능 |
| Leader | Medium | **BUY_PULLBACK** | 눌림 대기 |
| Leader | Weak | **HOLD_OFF** | 추격 금지 |

**핵심:**  
Leader는 **'무엇을 살지'**를 말하고,  
Checklist는 **'언제 살지'**를 말한다.

---

### **2️⃣ Follower 연동 (가장 중요)**

| Funnel | Checklist | State | 행동 |
|--------|-----------|-------|------|
| Follower | Strong | **ACCUMULATE** | 선제 매집 (미래 Leader 후보) |
| Follower | Medium | **WATCH** | 관찰 대기 |
| Follower | Weak | **HOLD_OFF** | 보류 |

**핵심:**  
Follower는 **Checklist를 통과했을 때만 알파가 된다.**

**시나리오:**
```
섹터는 이미 강함
종목은 아직 본격 돌파 전
기대수익률 최대 구간

→ Checklist Strong → 선제 매집 허가
→ Checklist Weak → 보류
```

---

### **3️⃣ No-Go 연동**

| Funnel | Checklist | State | 행동 |
|--------|-----------|-------|------|
| No-Go | ANY | **NO_GO** | 매수 금지 (절대) |

**핵심:**  
Checklist는 **설득 도구**입니다.  
"왜 사면 안 되는지"를 논리적으로 보여줌.

---

## 🎨 UI/UX 강제 설계

### **상태별 시각화**

```javascript
const STATE_CONFIG = {
    BUY_NOW: {
        color: '#4A90E2',
        icon: '🔵',
        label: '매수 가능',
        button: '매수 진입',
        enabled: true
    },
    BUY_PULLBACK: {
        color: '#52D27D',
        icon: '🟢',
        label: '눌림 대기',
        button: '알림 설정',
        enabled: true
    },
    ACCUMULATE: {
        color: '#FFB84D',
        icon: '🟡',
        label: '선제 매집',
        button: '소량 진입',
        enabled: true
    },
    WATCH: {
        color: '#AAB3D6',
        icon: '⚪',
        label: '관찰',
        button: '감시 추가',
        enabled: true
    },
    HOLD_OFF: {
        color: '#FF9A66',
        icon: '🟠',
        label: '보류',
        button: '비활성',
        enabled: false
    },
    NO_GO: {
        color: '#FF4D4D',
        icon: '🔴',
        label: '매수 금지',
        button: '이유 보기',
        enabled: false
    }
};
```

### **버튼 행동 규칙**

- **BUY_NOW** → 매수 페이지 이동
- **BUY_PULLBACK** → 알림 설정 모달
- **ACCUMULATE** → 소량 진입 가이드
- **WATCH** → 관찰 리스트 추가
- **HOLD_OFF** → 버튼 비활성화
- **NO_GO** → No-Go 리포트 표시

---

## 🎙️ 자동 멘트 생성

### **Leader 멘트**

```
[BUY_NOW]
"이 종목은 Leader이고 Checklist도 완벽합니다.
즉시 또는 분할 매수 가능 구간입니다."

[BUY_PULLBACK]
"이 종목은 Leader지만 Checklist가 완벽하지 않아
지금은 추격이 아니라 눌림을 기다립니다."

[HOLD_OFF]
"Leader이지만 과열 또는 리스크 요인이 있어
매수를 보류합니다."
```

### **Follower 멘트**

```
[ACCUMULATE]
"섹터는 이미 강합니다.
이 종목은 Follower이고 Checklist가 좋아
미래 Leader 후보로 선제 매집 구간입니다."

[WATCH]
"Follower 위치이지만 Checklist가 중간 수준입니다.
관찰하며 타이밍을 기다립니다."

[HOLD_OFF]
"Follower이지만 리스크가 명확합니다.
보류 또는 Pass를 권장합니다."
```

### **No-Go 멘트**

```
[NO_GO]
"이 종목은 구조적으로 No-Go입니다.
Checklist를 보면 왜 지금 사면 안 되는지 명확합니다."
```

---

## 📊 결정 테이블 (전체)

| Funnel | Checklist | State | 색상 | 멘트 요약 |
|--------|-----------|-------|------|----------|
| Leader | Strong (5개) | BUY_NOW | 🔵 | 즉시 매수 가능 |
| Leader | Medium (4개) | BUY_PULLBACK | 🟢 | 눌림 대기 |
| Leader | Weak (≤3개) | HOLD_OFF | 🟠 | 추격 금지 |
| Follower | Strong (5개) | ACCUMULATE | 🟡 | 선제 매집 |
| Follower | Medium (4개) | WATCH | ⚪ | 관찰 대기 |
| Follower | Weak (≤3개) | HOLD_OFF | 🟠 | 보류 |
| No-Go | ANY | NO_GO | 🔴 | 매수 금지 |

---

## 🔧 구현 체크리스트

- [ ] Checklist 5가지 항목 계산 로직
- [ ] Funnel × Checklist → State 매핑 엔진
- [ ] 6가지 State별 UI 컴포넌트
- [ ] 상태별 색상/아이콘 자동 적용
- [ ] 버튼 행동 규칙 (enabled/disabled)
- [ ] 자동 멘트 생성 로직
- [ ] No-Go 리포트 모달
- [ ] 알림 설정 기능
- [ ] 관찰 리스트 저장

---

## 🎯 핵심 원칙 (반드시 지킬 것)

1. **Funnel만으로는 매수 허가하지 않는다**
2. **Checklist Weak면 무조건 HOLD_OFF 이상**
3. **No-Go는 Checklist와 무관하게 절대 금지**
4. **색상만 봐도 행동이 결정되어야 함**
5. **UI는 행동을 강제한다 (추천이 아님)**

---

이 설계서대로 구현하면 Decision Stream은  
**"추천 시스템"이 아니라 "행동 통제 시스템"**이 됩니다.
