# Risk_ON 판정 알고리즘 (중기 스윙 전용)

## 📐 핵심 철학

> **Risk_ON이란?**  
> "시장이 수익을 추구해도 되는 상태"가 아니라,  
> **"리스크를 확장해도 시장이 즉시 응징하지 않는 상태"**

---

## 🎯 3대 원칙

### 원칙 ① 단일 지표 금지 ❌
- 코스피만 상승 ❌
- 지수 신고가 ❌
- 반드시 **복합 판정**

### 원칙 ② 방향보다 확산(Breadth) 중시
- 오르는 종목 수
- 테마의 지속성
- **소수 대형주 착시 제거**

### 원칙 ③ "깨질 때 빠르게 OFF"
- Risk_ON은 **허용 상태**
- 기본값은 **Risk_OFF**
- 의심스러우면 OFF

---

## 🔹 Risk_ON 최소 기준 세트

**아래 3개 중 2개 이상 충족 시 Risk_ON**

---

### 기준 1. 시장 Breadth (가장 중요) ⭐⭐⭐

**정의:**  
상승 종목 수가 하락 종목 수를 이기는 상태

**실전 기준:**
```
상승 종목 수 : 하락 종목 수 ≥ 1.2 : 1
```

**계산 방법:**
```python
def check_breadth(market_data):
    """
    시장 Breadth 확인
    """
    advancing = market_data['advancing_stocks']  # 상승 종목 수
    declining = market_data['declining_stocks']  # 하락 종목 수
    
    if declining == 0:
        return True  # 전체 상승
    
    ratio = advancing / declining
    
    return ratio >= 1.2

# 예시
# 상승 600개, 하락 400개 → 1.5 : 1 ✅ OK
# 상승 500개, 하락 500개 → 1.0 : 1 ❌ NG
```

**왜 중요한가:**
- 일부 대형주 착시 제거
- 중소형/섹터 확산 확인
- **👉 이게 없으면 Risk_ON 아님**

---

### 기준 2. 변동성 억제 (리스크 허용성) ⭐⭐

**정의:**  
시장이 충격을 "흡수"하고 있는가

**실전 기준:**
```
VKOSPI ≤ 20  또는
최근 5일 하락 추세
```

**계산 방법:**
```python
def check_volatility(vix_data):
    """
    변동성 억제 확인
    """
    current_vix = vix_data['current']
    vix_5d_ago = vix_data['5d_ago']
    
    # 조건 1: VIX 20 이하
    if current_vix <= 20:
        return True
    
    # 조건 2: 5일 전보다 하락
    if current_vix < vix_5d_ago:
        return True
    
    return False

# 예시
# VKOSPI 18 ✅ OK
# VKOSPI 25 → 22 (하락 중) ✅ OK
# VKOSPI 30 (급등) ❌ NG
```

**왜 중요한가:**
- 변동성 급등 구간에서 중기 스윙은 통계적으로 불리
- VIX 30 이상 = 공포 국면 = 즉시 OFF

---

### 기준 3. 테마 지속성 (핵심 보조) ⭐

**정의:**  
같은 섹터/테마가 3일 이상 살아 있는가

**실전 기준:**
```
동일 테마
상승 종목 ≥ 2개
3거래일 연속
```

**계산 방법:**
```python
def check_theme_persistence(theme_data):
    """
    테마 지속성 확인
    """
    themes_lasting_3days = []
    
    for theme in theme_data:
        # 3일 연속 상승 종목 2개 이상
        if (theme['consecutive_days'] >= 3 and 
            theme['advancing_stocks'] >= 2):
            themes_lasting_3days.append(theme['name'])
    
    # 지속 테마가 1개 이상 있으면 OK
    return len(themes_lasting_3days) > 0

# 예시
# 방산 테마: 3일 연속, 상승 종목 5개 ✅ OK
# AI 테마: 1일, 상승 종목 10개 ❌ NG (단타 테마)
```

**왜 중요한가:**
- 하루짜리 테마는 Risk_ON 아님
- **중기 스윙은 지속성 게임**
- 1일 급등 = 분배 신호

---

## 🧮 Risk_ON 판정 공식

```python
def determine_risk_regime(market_data, vix_data, theme_data):
    """
    Risk_ON / Risk_OFF 판정
    
    3개 기준 중 2개 이상 충족 → Risk_ON
    그 외 → Risk_OFF
    """
    breadth_ok = check_breadth(market_data)
    volatility_ok = check_volatility(vix_data)
    theme_ok = check_theme_persistence(theme_data)
    
    # 점수 계산 (1 or 0)
    score = (
        (1 if breadth_ok else 0) +
        (1 if volatility_ok else 0) +
        (1 if theme_ok else 0)
    )
    
    # 2개 이상 충족 시 Risk_ON
    if score >= 2:
        state = "RISK_ON"
    else:
        state = "RISK_OFF"
    
    return {
        "state": state,
        "score": score,
        "factors": {
            "breadth": breadth_ok,
            "volatility": volatility_ok,
            "theme": theme_ok
        }
    }
```

---

## 📊 엑셀 판정식 (보수형)

### CONTROL 시트

| 항목 | 기준 | 결과 |
|------|------|------|
| Breadth_OK | 상승:하락 ≥ 1.2:1 | 1 or 0 |
| Volatility_OK | VKOSPI ≤ 20 또는 하락 중 | 1 or 0 |
| Theme_OK | 3일 연속 테마 ≥ 1개 | 1 or 0 |

```excel
=IF(
    (Breadth_OK + Volatility_OK + Theme_OK) >= 2,
    "Risk_ON",
    "Risk_OFF"
)
```

---

## ✅ Risk_ON 올바른 사용법

### ❌ 잘못된 사용
```
Risk_ON = 매수
Risk_ON = 적극 진입
Risk_ON = 무조건 수익
```

### ✅ 올바른 사용
```
Risk_ON = 진입 가능성 검토 허가
Risk_OFF = Action Guide 봉쇄
```

**즉,**

> Risk_ON은  
> **"사도 된다"가 아니라**  
> **"사도 죽지 않을 확률이 높다"**

---

## 🚨 Risk_OFF 즉시 전환 조건

다음 중 **1개라도 발생 시 즉시 OFF**:

1. **Breadth 붕괴**
   - 상승:하락 < 1:1 (하락 우세)

2. **변동성 폭발**
   - VKOSPI > 30

3. **테마 동시 소멸**
   - 3일 이상 지속 테마 0개

4. **급락 신호**
   - 지수 -2% 이상 하락

---

## 📈 실전 예시

### Case 1: Risk_ON ✅
```
Breadth: 상승 650, 하락 450 → 1.44:1 ✅
Volatility: VKOSPI 18 ✅
Theme: 방산 3일 연속, 헬스케어 4일 연속 ✅

→ 3개 모두 충족 → Risk_ON
→ 진입 가능성 검토 허가
```

### Case 2: Risk_OFF ❌
```
Breadth: 상승 550, 하락 550 → 1:1 ❌
Volatility: VKOSPI 16 ✅
Theme: 방산 3일 연속 ✅

→ 2개 충족 (Breadth 실패)
→ Risk_OFF
→ 관망 / 현금 대기
```

### Case 3: Risk_OFF (변동성 급등) ❌
```
Breadth: 상승 700, 하락 400 → 1.75:1 ✅
Volatility: VKOSPI 35 (급등) ❌
Theme: 모든 테마 1일 단타 ❌

→ 1개만 충족
→ Risk_OFF
→ 즉시 철수 / 신규 진입 금지
```

---

## 🎯 중기 스윙 투자자를 위한 결론

1. **Risk_ON ≠ 매수 신호**
   - Risk_ON = 시장이 리스크를 허용하는 상태
   - 추가 종목 분석 필요 (Sector, Stock Funnel)

2. **Risk_OFF = 무조건 관망**
   - 아무리 좋은 종목이라도 진입 금지
   - 기존 포지션 손절 검토

3. **기본값은 OFF**
   - 의심스러우면 OFF
   - 보수적 판정이 장기 생존률 높임

4. **Breadth가 가장 중요**
   - Breadth 없으면 절대 Risk_ON 아님
   - 대형주 착시 조심

---

## 🛠️ 구현 체크리스트

- [ ] 상승/하락 종목 수 데이터 수집
- [ ] VKOSPI (또는 VIX) 데이터 연동
- [ ] 테마별 지속성 트래킹 (3일 이상)
- [ ] Risk_ON/OFF 판정 엔진 구현
- [ ] UI에서 3가지 기준 시각화
- [ ] 즉시 OFF 전환 알림 시스템

---

이 설계서를 기반으로 백엔드 구현을 시작하시겠습니까?
