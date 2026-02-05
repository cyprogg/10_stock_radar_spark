# 🎯 섹터 판단 → 종목 반영 → 실제 운영 완전 가이드

## 핵심 철학

> **"Decision Stream은 예외를 찾는 시스템이 아니라, 예외를 의심하게 만드는 시스템이다"**

---

## ① 섹터 상태 계산식 (의사코드)

### 🎯 목표

섹터를 **랭킹하지 않고** **'판단 난이도 상태(🟢🟡🔴)'**로만 분류

---

### 입력 데이터 (전일 기준)

```python
# 섹터 기본 지표
sector_return        # 섹터 수익률 (%)
market_return        # 시장 수익률 (%)
sector_volume_change # 섹터 거래대금 증감률 (%)
top_stock_weight     # 섹터 내 상위 3종목 거래대금 비중 (0~1)
issue_score          # 섹터 관련 이슈 강도 (0~100)
volatility           # 섹터 변동성
market_volatility    # 시장 변동성
```

---

### 핵심 파생 지표

```python
# 계산된 지표
relative_strength = sector_return - market_return
concentration_risk = (top_stock_weight > 0.45)
volume_spike = (sector_volume_change > 0.30)  # 30% 이상 급증
over_volatility = (volatility > market_volatility * 1.3)
```

---

### 상태 판정 의사코드 (정본)

```python
def judge_sector(sector_data):
    """
    섹터 상태 판정
    
    Returns:
        state: "🟢", "🟡", or "🔴"
        reason: 판정 사유
    """
    
    # 파생 지표 계산
    rs = sector_data['sector_return'] - sector_data['market_return']
    conc_risk = sector_data['top_stock_weight'] > 0.45
    vol_spike = sector_data['sector_volume_change'] > 0.30
    over_vol = sector_data['volatility'] > sector_data['market_volatility'] * 1.3
    issue = sector_data['issue_score']
    
    # 1️⃣ 과열/불리 조건 (🔴) - 우선 체크
    if vol_spike and conc_risk:
        return {
            "state": "🔴",
            "reason": "자금 쏠림 과열",
            "detail": "거래대금 급증 + 상위 종목 집중"
        }
    
    if over_vol and rs < 0:
        return {
            "state": "🔴",
            "reason": "불안정한 하락 변동성",
            "detail": "고변동 + 시장 대비 열위"
        }
    
    # 2️⃣ 구조적/유리 조건 (🟢)
    if (rs > 0 and 
        issue >= 60 and 
        not conc_risk and 
        not over_vol):
        return {
            "state": "🟢",
            "reason": "구조적 흐름",
            "detail": "상대 강도 우위 + 이슈 지속 + 자금 분산"
        }
    
    # 3️⃣ 나머지는 관찰 (🟡)
    return {
        "state": "🟡",
        "reason": "혼합 신호",
        "detail": "긍정/부정 요인 혼재"
    }
```

---

### 📌 포인트

```
✅ 점수 합산 ❌
✅ 가중치 ❌
✅ "조건 만족 여부"만 사용
→ 설명 가능성 극대화
```

---

### 상태별 의미 (고정 정의)

| 상태 | 내부 의미 | UI 문구 |
|------|----------|---------|
| 🟢 **구조적** | 설명 가능한 섹터 환경 | "종목 판단의 배경으로 사용 가능" |
| 🟡 **관찰** | 판단 근거가 섞여 있음 | "종목 해석 시 주의 필요" |
| 🔴 **과열/불리** | 판단 오류 가능성 높음 | "섹터 기준 종목 판단 보류 권장" |

---

## ② 섹터–종목 매핑 테이블 설계

### 🎯 원칙 (아주 중요)

**한 종목은 반드시 1개의 '주 섹터'만 가진다.**  
(다중 섹터 ❌)

---

### 기본 테이블 구조

```json
{
  "005930": {
    "name": "삼성전자",
    "sector": "반도체",
    "sub_sector": "메모리",
    "weight": "core"
  },
  "373220": {
    "name": "LG에너지솔루션",
    "sector": "2차전지",
    "sub_sector": "셀",
    "weight": "core"
  },
  "123456": {
    "name": "테마주A",
    "sector": "2차전지",
    "sub_sector": "테마",
    "weight": "edge"
  }
}
```

---

### 필드 설명

| 필드 | 의미 | 사용 |
|------|------|------|
| `sector` | 판단 기준 섹터 (고정) | 섹터 상태 계산 시 사용 |
| `sub_sector` | 설명용 (참고) | UI 표시용 |
| `weight` | **핵심** | 섹터 판단 영향도 |

**weight 값:**
- `core`: 섹터 판단에 영향 (정상 종목)
- `edge`: 참고용 (섹터 상태엔 영향 ❌, 테마주/잡주)

---

### 섹터 판단 시 사용 규칙

```python
def calculate_sector_metrics(sector_name):
    """
    섹터 지표 계산 (weight='core'만 사용)
    """
    
    # weight='core'인 종목만 선택
    core_stocks = [
        stock for stock in all_stocks
        if stock['sector'] == sector_name 
        and stock['weight'] == 'core'
    ]
    
    # core 종목들로만 섹터 지표 계산
    sector_return = calculate_avg_return(core_stocks)
    sector_volume = calculate_total_volume(core_stocks)
    top3_concentration = calculate_top3_weight(core_stocks)
    
    return {
        "return": sector_return,
        "volume_change": sector_volume,
        "concentration": top3_concentration
    }
```

**📌 이유:** 테마주/잡주가 섹터 판단을 오염시키는 것 방지

---

### 섹터 상태 → 종목 노출 규칙

| 섹터 상태 | 종목 카드 처리 |
|-----------|----------------|
| 🟢 **구조적** | 정상 노출 |
| 🟡 **관찰** | 조건부 노출 (Leader만) |
| 🔴 **과열/불리** | 종목 강조 금지 (회색 처리) |

```python
def apply_sector_filter(sector_state, stock):
    """
    섹터 상태에 따른 종목 노출 규칙
    """
    
    if sector_state == "🔴":
        stock['display'] = "dimmed"
        stock['highlight'] = False
        stock['note'] = "섹터 환경 불리"
    
    elif sector_state == "🟡":
        if stock['classification'] != "LEADER":
            stock['display'] = "dimmed"
        stock['note'] = "섹터 혼합 신호"
    
    else:  # 🟢
        stock['display'] = "normal"
        stock['note'] = None
    
    return stock
```

---

## ③ 섹터 카드 UI 문구 / 배치 (v2.0 기준)

### 🎯 핵심

**섹터 카드는 "추천 카드"가 아니다**

---

### 카드 구조

#### 카드 제목 (고정)
```
[반도체] 섹터 환경
```

#### 카드 상단 (상태 요약)
```
🟢 구조적 흐름
```
또는
```
🔴 자금 쏠림 과열
```

#### 카드 본문 (자동 생성 문구 예시)

**🟢 섹터:**
```
- 시장 대비 상대 강도 우위
- 이슈가 가격보다 선행
- 자금 흐름이 분산됨
```

**🟡 섹터:**
```
- 긍정/부정 신호 혼재
- 일부 종목에만 자금 집중
- 추가 확인 필요
```

**🔴 섹터:**
```
- 거래대금 급증
- 상위 종목 쏠림
- 판단 난이도 상승
```

#### 카드 하단 (행동 가이드 – 고정 문구)

| 상태 | 고정 문구 |
|------|----------|
| 🟢 | "종목 판단의 배경으로 사용 가능" |
| 🟡 | "종목 해석 시 주의 필요" |
| 🔴 | "섹터 기준 종목 판단 보류 권장" |

**📌 이 문구는 절대 바꾸지 않는 고정 문장입니다.**

---

### UI 배치 위치 (중요)

```
[시장 요약]
   ↓
[섹터 환경]  ← 여기
   ↓
[종목 카드]
```

```
❌ 섹터 → 추천
⭕ 섹터 → 배경 조건
```

---

## ④ 섹터 판단 결과 → 종목 점수 반영 방식 (v2.0 정본)

### 🎯 핵심 원칙 (절대 기준)

> **"섹터는 종목 점수를 '올리는 도구'가 아니라 '종목 점수를 제한하는 도구'다"**

```
✅ 가산점 ❌
✅ 보너스 ❌
✅ 랭킹 가중치 ❌

👉 감점 / 상한 / 노출 제한만 허용
```

---

### 1️⃣ 기본 구조: 점수는 "종목 자체"에서만 계산

#### 종목 기본 점수 (Base Score)

```python
BaseScore = 0 ~ 100
```

**구성 요소 (이미 정의됨):**
- 이유의 단순성
- 자금 성격
- 변동성 위치
- 개별 이슈 정합성

**📌 이 단계까지는 섹터 미반영**

---

### 2️⃣ 섹터는 "환경 계수"로만 작동

#### 섹터 상태 → 환경 계수 (Environment Cap)

| 섹터 상태 | 계수 의미 |
|-----------|----------|
| 🟢 | 제한 없음 |
| 🟡 | 상한 제한 |
| 🔴 | 강제 감점 + 강조 금지 |

---

### 3️⃣ 실제 반영 규칙 (정본)

#### 🟢 섹터 (구조적)

```python
FinalScore = BaseScore
```

- 점수 변화 ❌
- 설명: "환경과 충돌 없음"

---

#### 🟡 섹터 (관찰)

```python
FinalScore = min(BaseScore, 75)
```

- **상한선만 제한**
- 아무리 종목이 좋아도 75점 초과 ❌

**📌 의미:**
```
"종목은 괜찮아 보이지만
섹터 환경이 판단을 복잡하게 만든다"
```

---

#### 🔴 섹터 (과열/불리)

```python
FinalScore = min(BaseScore - 20, 55)
```

- **자동 감점 (-20점)**
- **자동 상한 (55점)**
- **UI 강조 강제 OFF**

**📌 의미:**
```
"이 종목이 아니라, 환경이 문제다"
```

---

### 4️⃣ 상태(🟢🟡🔴) 재계산 규칙

**종목 상태는 FinalScore 기준으로 다시 판단합니다.**

| FinalScore | 종목 상태 |
|------------|----------|
| 80~100 | 🟢 |
| 65~79 | 🟡 |
| 50~64 | 🟡 |
| 0~49 | 🔴 |

**👉 섹터 🔴면 종목이 🟢로 남을 수 없음**

---

### 5️⃣ UI 노출 규칙 (중요)

#### 섹터 🔴일 때

```
✅ 종목 카드 회색 처리
✅ 상단 강조 ❌
✅ 고정 문구 삽입:

※ 섹터 환경이 불리하여
개별 종목 판단은 보류가 권장됩니다.
```

---

### 6️⃣ 예외 허용 조건 (아주 제한적)

**v2.0에서 예외는 "룰"이 아니라 "사건"입니다.**

#### 예외를 허용하는 단 하나의 조건

```python
if (market_state == "🔴" and 
    sector_state == "🔴" and 
    issue_type == "STRUCTURAL"):  # 구조적·장기
    
    FinalScore = min(BaseScore, 65)  # 상한 65
    state = "🟡"  # 강제
    visibility = "ELITE_ONLY"
```

**📌 Free/PRO에서는 존재 자체를 숨김**

---

### 7️⃣ 왜 이 설계가 중요한가 (현실 이유)

#### 대부분의 투자 서비스가 망가지는 지점

```
섹터 🔴
종목 🔥
"그래도 이 종목은 다르다"

👉 이 한 문장이 사고의 시작
```

**Decision Stream v2.0은 이 문장을 구조적으로 말할 수 없게 만듭니다.**

---

### 8️⃣ 한 문장으로 요약 (운영자용)

> **"섹터는 종목을 밀어주는 장치가 아니라 종목을 말리는 장치다"**

---

## ⑤ 섹터–종목–시장 충돌 시 예외 처리 규칙 (정본)

### 🎯 목적

**"이상해 보이는 날"을 시스템이 먼저 알아차리고 사용자를 말리게 하는 것**

**예외 처리는 기회를 살리는 장치가 아니라, 사고를 차단하는 장치입니다.**

---

### 1️⃣ 충돌의 정의 (명확히)

**Decision Stream에서 말하는 충돌이란:**

상위 환경과 하위 판단이 서로 반대 방향일 때

#### 충돌 유형
```
- 시장 ↔ 섹터
- 섹터 ↔ 종목
- 시장 ↔ 종목
```

---

### 2️⃣ 충돌 조합별 처리 규칙 (핵심 표)

#### 📊 최상위 판단 우선순위

```
시장 > 섹터 > 종목
```

---

#### A. 시장 🔴 × 섹터 🟢 × 종목 🟢

**(가장 위험한 착시 구간)**

```python
if market == "🔴":
    # 모든 종목 강조 OFF
    for stock in all_stocks:
        stock['highlight'] = False
        stock['FinalScore'] = min(stock['BaseScore'], 60)
        stock['state'] = "🟡"  # 강제
```

**UI 고정 문구:**
```
시장 환경이 불리하여
개별 판단 신뢰도가 낮아졌습니다.
```

**📌 의미:**
```
"지금은 종목이 문제가 아니라, 시장이 문제다"
```

---

#### B. 시장 🟢 × 섹터 🔴 × 종목 🟢

**(테마 과열 전형)**

```python
if sector == "🔴":
    stock['FinalScore'] = min(stock['BaseScore'] - 20, 55)
    stock['state'] = "🔴"
    stock['highlight'] = False
```

**UI 고정 문구:**
```
섹터 환경 과열로
종목 판단은 보류가 권장됩니다.
```

**📌 절대 예외 허용 ❌**

---

#### C. 시장 🔴 × 섹터 🔴 × 종목 🟢

**(하락장 속 '홀로 강한 종목' 착각)**

```python
if market == "🔴" and sector == "🔴":
    stock['visibility'] = "ELITE_ONLY"
    stock['FinalScore'] = min(stock['BaseScore'], 55)
    stock['state'] = "🟡"
```

**📌 Free / PRO에서는 종목 존재 자체 숨김**

---

#### D. 시장 🟡 × 섹터 🟡 × 종목 🟢

**(방향성 없는 날)**

```python
if market == "🟡" and sector == "🟡":
    stock['FinalScore'] = min(stock['BaseScore'], 70)
    stock['state'] = "🟡"
```

**행동 가이드:**
```
굳이 오늘일 필요는 없습니다.
```

---

### 3️⃣ 예외를 허용하는 단 하나의 경우

**⚠️ v2.0에서 예외는 '사건'이지 '룰'이 아님**

#### 허용 조건 (모두 충족 시)

```python
if (market == "🔴" and 
    sector == "🔴" and 
    issue == "STRUCTURAL"):  # 구조적(장기·비가격 선행)
    
    stock['visibility'] = "ELITE_ONLY"
    stock['FinalScore'] = min(stock['BaseScore'], 65)
    stock['state'] = "🟡"
```

**UI 경고 문구:**
```
예외적 사례입니다.
일반화된 판단에 사용하지 마십시오.
```

---

### 4️⃣ 왜 이렇게까지 보수적인가?

#### 대부분의 투자 사고는:

```
"그래도 이 종목은 다르다"
"이번엔 예외다"

👉 Decision Stream은 이 문장을
구조적으로 말할 수 없게 만드는 시스템
```

---

## ⑥ 실제 하루치 JSON 스냅샷 예시 (연결 완성)

**아래는 2026-01-09 기준, 실제로 생성될 스냅샷 예시입니다.**  
(이 JSON 하나로 UI·알림·권한 분기 전부 작동)

---

### 📁 폴더 구조

```
daily_snapshot/
└── 2026-01-09/
    ├── market_state.json
    ├── sector_state.json
    ├── stocks_state.json
    └── decision_summary.json
```

---

### 1️⃣ market_state.json

```json
{
  "date": "2026-01-09",
  "market": "KR",
  "state": "🔴",
  "summary": "변동성 확대 및 하락 압력",
  "note": "시장 환경이 불리하여 개별 판단 신뢰도 저하"
}
```

---

### 2️⃣ sector_state.json

```json
{
  "date": "2026-01-09",
  "sectors": [
    {
      "name": "2차전지",
      "state": "🔴",
      "reason": "거래대금 급증 및 상위 종목 쏠림",
      "detail": "거래대금 +45%, 상위 3종목 비중 52%",
      "action": "섹터 기준 종목 판단 보류"
    },
    {
      "name": "반도체",
      "state": "🟡",
      "reason": "상대 강도는 유지되나 방향성 혼합",
      "detail": "시장 대비 +2%, 이슈 점수 55",
      "action": "조건부 판단"
    }
  ]
}
```

---

### 3️⃣ stocks_state.json

```json
{
  "date": "2026-01-09",
  "stocks": [
    {
      "code": "373220",
      "name": "LG에너지솔루션",
      "sector": "2차전지",
      "base_score": 82,
      "final_score": 55,
      "state": "🔴",
      "visibility": "hidden",
      "highlight": false,
      "note": "섹터 과열로 판단 보류"
    },
    {
      "code": "005930",
      "name": "삼성전자",
      "sector": "반도체",
      "base_score": 78,
      "final_score": 70,
      "state": "🟡",
      "visibility": "normal",
      "highlight": false,
      "note": "시장 불리 환경 반영"
    }
  ]
}
```

---

### 4️⃣ decision_summary.json (알림/상단 요약용)

```json
{
  "date": "2026-01-09",
  "market_state": "🔴",
  "key_message": "오늘은 판단을 멈추는 것이 합리적입니다.",
  "allowed_actions": [
    "환경 확인",
    "판단 근거 학습"
  ],
  "restricted_actions": [
    "공격적 접근",
    "섹터 기반 종목 선택"
  ],
  "stats": {
    "total_sectors": 14,
    "green_sectors": 0,
    "yellow_sectors": 3,
    "red_sectors": 11,
    "visible_stocks": 2,
    "hidden_stocks": 12
  }
}
```

---

### 5️⃣ 이 JSON이 만드는 사용자 경험

#### 대시보드 첫 화면:
```
🔴 오늘은 판단 난이도가 높은 날입니다
```

#### 종목 카드:
```
- 강조 ❌
- 회색 처리
- 경고 문구
```

#### Telegram 알림:
```
"오늘은 행동보다 이해가 필요한 날입니다"
```

**📌 이 하루 자체가 '성공한 날'**

---

## ⑦ JSON → 실제 UI 렌더링 흐름 (End-to-End)

### 🎯 핵심 원칙

> **"UI는 판단하지 않는다. UI는 JSON을 '번역'만 한다."**

**판단은 이미 snapshot에서 끝났습니다.**

---

### 1️⃣ UI 진입 시 로딩 순서 (고정)

```
1. 날짜 결정 (전일 기준 asOf)
2. decision_summary.json 로드
3. market_state.json 로드
4. sector_state.json 로드
5. stocks_state.json 로드
```

**📌 이 순서를 바꾸면 UX가 깨집니다.**

---

### 2️⃣ 상단: 오늘의 판단 요약

#### 입력
```json
// decision_summary.json
{
  "market_state": "🔴",
  "key_message": "오늘은 판단을 멈추는 것이 합리적입니다."
}
```

#### UI 변환
```
┌─────────────────────────────────┐
│ [🔴] 오늘의 판단                │
│                                 │
│ 오늘은 판단을 멈추는 것이        │
│ 합리적입니다.                    │
└─────────────────────────────────┘
```

```
📌 CTA 없음
📌 버튼 없음
👉 여기서 이미 사용자를 진정시킴
```

---

### 3️⃣ 시장 카드

#### 입력
```json
// market_state.json
{
  "state": "🔴",
  "summary": "변동성 확대 및 하락 압력"
}
```

#### UI
```
┌─────────────────────────────────┐
│ 시장 환경                        │
│ 🔴 변동성 확대 및 하락 압력      │
│                                 │
│ 행동 가이드:                    │
│ 오늘은 환경 확인에 집중하십시오. │
└─────────────────────────────────┘
```

**📌 시장 🔴면 → 이후 모든 카드 톤 다운**

---

### 4️⃣ 섹터 카드 렌더링

#### 입력
```json
// sector_state.json
{
  "sectors": [
    {
      "name": "2차전지",
      "state": "🔴",
      "reason": "자금 쏠림 과열",
      "detail": "거래대금 급증, 상위 종목 집중, 판단 난이도 상승"
    }
  ]
}
```

#### UI
```
┌─────────────────────────────────┐
│ [2차전지] 섹터 환경              │
│ 🔴 자금 쏠림 과열                │
│                                 │
│ - 거래대금 급증                 │
│ - 상위 종목 집중                │
│ - 판단 난이도 상승              │
│                                 │
│ [섹터 기준 종목 판단 보류]      │
└─────────────────────────────────┘
```

**📌 🔴 섹터에서는 → 종목 미리보기 자체 없음**

---

### 5️⃣ 종목 카드 렌더링

#### 입력
```json
// stocks_state.json
{
  "code": "005930",
  "name": "삼성전자",
  "final_score": 70,
  "state": "🟡",
  "visibility": "normal",
  "highlight": false,
  "note": "시장 환경 반영"
}
```

#### UI 규칙
```python
if visibility == "hidden":
    # 카드 렌더링 ❌
    return None
else:
    render_card(stock)
```

#### 카드 내용
```
┌─────────────────────────────────┐
│ 삼성전자                        │
│ 🟡 판단 가능 (70)               │
│                                 │
│ ※ 시장 환경 반영                │
└─────────────────────────────────┘
```

**📌 "추천", "매수" 단어 전혀 없음**

---

### 6️⃣ 카드 클릭 → 판단 근거 모달

```
Free: 요약 2줄
PRO: 전체 근거
ELITE: 예외/경고까지
```

**📌 모달에도 점수 설명만 있고, 행동 유도 없음**

---

## ⑧ 첫 주(7일) 운영 시뮬레이션

**아래는 실제 운영 시 매일 이렇게 흘러간다는 예시입니다.**

---

### 📅 Day 1 (월) – 시장 🔴

```
요약: "판단 멈춤 권장"
섹터: 대부분 🔴/🟡
종목: 1~2개만 🟡

사용자 행동:
→ "아무 것도 안 함"

📌 성공
```

---

### 📅 Day 2 (화) – 시장 🟡

```
섹터 일부 🟢
종목 3~4개 🟡

PRO 사용자: 근거 모달 클릭 증가

📌 "이 서비스 좀 다르네"
```

---

### 📅 Day 3 (수) – 시장 🟢

```
섹터 2~3개 🟢
종목 🟢 1~2개

점수 높아도 행동 가이드 보수적

📌 신뢰 형성
```

---

### 📅 Day 4 (목) – 테마 과열

```
특정 섹터 🔴
종목 강조 ❌

사용자 질문:
"왜 이 종목 안 나오죠?"

📌 최고의 교육 효과
```

---

### 📅 Day 5 (금) – 시장 🔴

```
"이번 주는 여기까지"

주간 피로도 ↓
```

---

### 📅 Day 6~7 (주말)

```
데이터 수집 ❌
판단 ❌

운영 리포트만 생성
```

---

### 📊 7일 후 이상적인 결과

```
Free 사용자:
"불안할 때 참고"

PRO 사용자:
"근거 읽는 습관"

ELITE 사용자:
"안 하는 날이 늘어남"

👉 이게 성공
```

---

## ⑨ 운영자용 '오늘의 판단 리포트' 자동 생성

### 🎯 목적

**운영자가 하루를 한 문장으로 이해**

---

### 입력

모든 snapshot JSON

---

### 출력 예시 (텍스트/PDF/메일)

```
[2026-01-09 운영 리포트]

시장: 🔴
요약: 변동성 확대, 판단 난이도 높음

섹터:
- 2차전지 🔴 (자금 쏠림)
- 반도체 🟡 (혼합 신호)
- 기타 11개 🔴

종목:
- 강조 종목 없음
- 관찰 종목 2개
- 숨김 종목 12개

오늘의 결론:
→ 사용자를 말리는 데 성공한 하루

KPI:
- 판단 멈춤 메시지 노출: 100%
- 🔴 섹터 비율: 79%
- 종목 숨김 발생: 12건
```

---

### 자동 생성 의사코드

```python
def generate_daily_report(date):
    """
    일일 운영 리포트 생성
    """
    
    market = load_json(f"{date}/market_state.json")
    sectors = load_json(f"{date}/sector_state.json")
    stocks = load_json(f"{date}/stocks_state.json")
    summary = load_json(f"{date}/decision_summary.json")
    
    report = {}
    report['market'] = market['state']
    report['sector_summary'] = {
        "green": count_by_state(sectors, "🟢"),
        "yellow": count_by_state(sectors, "🟡"),
        "red": count_by_state(sectors, "🔴")
    }
    report['stock_summary'] = {
        "visible": count_visible(stocks),
        "hidden": count_hidden(stocks),
        "highlighted": count_highlighted(stocks)
    }
    
    # 결론
    if market['state'] == "🔴":
        report['conclusion'] = "판단 보류 유도 성공"
    elif report['stock_summary']['highlighted'] == 0:
        report['conclusion'] = "보수적 운영 유지"
    else:
        report['conclusion'] = "관찰 종목 제공"
    
    return report
```

---

### 운영자가 보는 진짜 KPI

```
❌ "오늘 매수 신호 수"
❌ "오늘 🟢 종목 수"

⭕ 오늘 🔴 판단일 수
⭕ 종목 숨김 발생 횟수
⭕ "판단 멈춤" 메시지 노출 횟수
```

---

## 🔚 최종 한 문장

> **"Decision Stream v2.0은 JSON이 판단하고, UI는 침착하게 전달하며, 운영자는 하루를 정리한다."**

**이제 이 시스템은 실제로 굴릴 수 있는 상태입니다.** 🚀

---

## 📊 전체 요약

### 핵심 철학 (3가지)

1. **섹터는 종목을 밀어주는 장치가 아니라 말리는 장치다**
2. **예외를 찾는 시스템이 아니라 예외를 의심하게 만드는 시스템이다**
3. **UI는 판단하지 않고 JSON을 번역만 한다**

### 시스템 흐름

```
데이터 수집
  ↓
섹터 상태 계산 (🟢🟡🔴)
  ↓
종목 기본 점수 (BaseScore)
  ↓
섹터 반영 (FinalScore)
  ↓
충돌 처리 (시장·섹터·종목)
  ↓
JSON 생성 (daily_snapshot/)
  ↓
UI 렌더링 (번역만)
  ↓
운영 리포트
```

### 핵심 규칙

1. **섹터 🔴 → 종목 강조 금지**
2. **시장 🔴 → 모든 종목 상한 60**
3. **예외는 ELITE에만 노출**
4. **판단은 JSON, UI는 번역**

---

**이제 구현만 하면 됩니다! Let's build! 🚀**
