# Follower → Leader 승격 알고리즘

## 🎯 핵심 정의

> **Follower → Leader 전환은**  
> **"섹터 확신(SURGE) + 종목 구조 + 자금 행동"이**  
> **동시에 충족될 때만 발생한다.**
>
> **단일 신호 ❌ / 복수 조건 AND 구조 ⭕**

---

## 📐 승격 판정 로직

### **전제조건: Sector Gate (필수)**

```python
def check_sector_gate(sector_data):
    """
    섹터 조건 확인
    Leader는 섹터 합의의 산물
    """
    # 조건 1: SURGE 신호
    is_surge = sector_data['flow_signal'] == 'SURGE'
    
    # 조건 2: SURGE 연속일
    surge_streak = sector_data.get('surge_streak_days', 0)
    
    # 조건 3: SCL (Sector Confidence Level) ≥ 2
    scl = sector_data.get('scl', 0)
    
    # 하나라도 충족하면 Gate 통과
    sector_gate = is_surge or (surge_streak >= 2) or (scl >= 2)
    
    return sector_gate, scl
```

---

### **조건 1: Structure Score (구조 조건)**

**다음 중 2개 이상 충족**

```python
def calculate_structure_score(stock_data, sector_index):
    """
    구조 조건 (2개 이상 필요)
    """
    score = 0
    
    # 1) 중기 고점 돌파 or 갱신
    if stock_data['close'] >= stock_data['high_60d'] * 0.98:
        score += 1
    
    # 2) Higher Low 유지
    if stock_data['low_20d'] > stock_data['low_60d']:
        score += 1
    
    # 3) 장기 이동평균 상방 유지
    if (stock_data['close'] > stock_data['ma60'] and 
        stock_data['close'] > stock_data['ma120']):
        score += 1
    
    # 4) 섹터 대비 상대강도 상위 30%
    rs = calculate_relative_strength(stock_data, sector_index, period=20)
    if rs > 110:  # 섹터 대비 10% 이상 초과 수익
        score += 1
    
    return score  # 2 이상 필요
```

---

### **조건 2: Flow Score (자금 조건)**

**다음 중 1개 이상 충족**

```python
def calculate_flow_score(stock_data):
    """
    자금 조건 (1개 이상 필요)
    """
    score = 0
    
    # 1) 거래량 평균 대비 ≥ 1.5배
    volume_ratio = stock_data['volume'] / stock_data['avg_volume_20d']
    if volume_ratio >= 1.5:
        score += 1
    
    # 2) 기관/외국인 순매수 신호
    if (stock_data.get('institution_net_buy_5d', 0) > 0 or 
        stock_data.get('foreign_net_buy_5d', 0) > 0):
        score += 1
    
    # 3) 변동성 축소 후 확장 (Squeeze → Expansion)
    atr_current = stock_data['atr_5d']
    atr_avg = stock_data['atr_20d']
    if atr_current > atr_avg * 1.2:  # 변동성 확장
        score += 1
    
    return score  # 1 이상 필요
```

---

### **조건 3: Checklist (리스크 필터)**

**동적 기준 적용**

```python
def check_checklist_condition(stock_data, scl):
    """
    Checklist 조건 (동적 기준)
    """
    checklist = {
        'price_structure': check_price_structure(stock_data),
        'volume': check_volume(stock_data),
        'volatility': check_volatility(stock_data),
        'event_risk': check_event_risk(stock_data),
        'pullback': check_pullback(stock_data),
        'trend': check_trend(stock_data)  # 추가 항목
    }
    
    pass_count = sum(checklist.values())
    
    # 동적 기준
    if scl >= 3:
        required = 4  # 확신 구간 → 완화
    elif scl >= 2:
        required = 5
    else:
        required = 6  # 기본값
    
    checklist_ok = pass_count >= required
    
    return checklist_ok, pass_count, required
```

---

### **조건 4: Confirm Rule (False Break 방지)**

**2회 연속 관측 필요**

```python
def check_promotion_confirmation(stock_ticker, history_db):
    """
    시간 조건: 2회 연속 관측
    단발성 뉴스/위꼬리 제거
    """
    # 최근 3일 승격 후보 기록 확인
    recent_signals = history_db.get(stock_ticker, [])
    
    # 연속 2회 이상 승격 조건 충족
    confirm_count = sum(1 for signal in recent_signals[-3:] 
                       if signal['promotion_candidate'] == True)
    
    return confirm_count >= 2
```

---

## 🎯 최종 승격 판정

```python
def evaluate_promotion(stock_data, sector_data, sector_index, history_db):
    """
    Follower → Leader 승격 판정
    
    모든 조건을 AND로 결합
    """
    # 현재 Funnel 위치 확인
    if stock_data['funnel_type'] != 'FOLLOWER':
        return False, "Not a Follower"
    
    # Gate 1: 섹터 조건
    sector_gate, scl = check_sector_gate(sector_data)
    if not sector_gate:
        return False, "Sector Gate Failed"
    
    # 조건 1: Structure Score
    structure_score = calculate_structure_score(stock_data, sector_index)
    if structure_score < 2:
        return False, f"Structure Score: {structure_score}/4 (need ≥2)"
    
    # 조건 2: Flow Score
    flow_score = calculate_flow_score(stock_data)
    if flow_score < 1:
        return False, f"Flow Score: {flow_score}/3 (need ≥1)"
    
    # 조건 3: Checklist
    checklist_ok, pass_count, required = check_checklist_condition(stock_data, scl)
    if not checklist_ok:
        return False, f"Checklist: {pass_count}/{required}"
    
    # 조건 4: Confirmation
    confirm = check_promotion_confirmation(stock_data['ticker'], history_db)
    if not confirm:
        return False, "Confirmation Needed (1 more observation)"
    
    # 모든 조건 충족 → 승격!
    return True, {
        'sector_gate': sector_gate,
        'scl': scl,
        'structure_score': structure_score,
        'flow_score': flow_score,
        'checklist': f"{pass_count}/{required}",
        'confirm_count': 2
    }
```

---

## 🔄 승격 이후 시스템 동작

### **1️⃣ 즉시 반영**

```python
def execute_promotion(stock_data, promotion_reason):
    """
    승격 실행
    """
    # Funnel 이동
    stock_data['funnel_type'] = 'LEADER'
    stock_data['promoted_at'] = datetime.now()
    stock_data['promotion_reason'] = promotion_reason
    
    # 로그 기록
    log_promotion_event({
        'ticker': stock_data['ticker'],
        'name': stock_data['name'],
        'sector': stock_data['sector'],
        'from': 'FOLLOWER',
        'to': 'LEADER',
        'reason': promotion_reason,
        'timestamp': datetime.now()
    })
    
    # SCL Jump 검사 트리거
    check_scl_jump(stock_data['sector'])
    
    return stock_data
```

### **2️⃣ 행동 규칙 자동 변경**

```python
def update_action_rules(stock_data):
    """
    Leader 승격 후 규칙 변경
    """
    rules = {
        'checklist_level': 'STRICT',  # 눌림 기준 강화
        'entry_strategy': 'PULLBACK',  # Breakout 금지
        'stop_loss_tighter': True,     # 손절 타이트
        'position_size': 'REDUCED',    # 포지션 축소
        'alert_priority': 'HIGH'       # 알림 우선순위 상승
    }
    
    return rules
```

### **3️⃣ 콘텐츠 자동 생성**

```python
def generate_promotion_message(stock_data, promotion_reason):
    """
    승격 감지 자동 멘트
    """
    message = f"""
🚀 승격 감지!

{stock_data['name']} ({stock_data['ticker']})
Follower → Leader 전환

승격 근거:
• 섹터 확신: SCL {promotion_reason['scl']}
• 구조 점수: {promotion_reason['structure_score']}/4
• 자금 유입: {promotion_reason['flow_score']}/3
• Checklist: {promotion_reason['checklist']}

⚠️ 행동 규칙:
• 추격 매수 금지
• 눌림 매수 전략 전환
• 알림 설정 권장

💡 "시장이 이 종목에 대해 합의했다"는 신호입니다.
"""
    
    return message
```

---

## ❌ 절대 금지 규칙

```python
# ❌ 하루 상승률 기준 승격
if decision_based_on == 'daily_return_only':
    raise ValueError("Single day return cannot trigger promotion")

# ❌ 거래량 하나로 승격
if decision_based_on == 'volume_only':
    raise ValueError("Volume alone cannot trigger promotion")

# ❌ 뉴스 이벤트 단독 승격
if decision_based_on == 'news_event_only':
    raise ValueError("News alone cannot trigger promotion")

# ❌ 수동 Leader 지정
if triggered_by == 'manual_user_action':
    raise ValueError("Leader can only be created by system")
```

---

## 📊 승격 판정 흐름도

```
[Follower 종목]
    ↓
[Sector Gate Check]
    ↓ PASS
[Structure Score ≥ 2?]
    ↓ YES
[Flow Score ≥ 1?]
    ↓ YES
[Checklist ≥ Required?]
    ↓ YES
[Confirm Count ≥ 2?]
    ↓ YES
[🚀 PROMOTION TO LEADER]
    ↓
[1. Funnel 이동]
[2. 규칙 변경]
[3. 알림 발송]
[4. 콘텐츠 생성]
```

---

## 🎯 기획자 최종 문장

> **"Follower → Leader 전환은**  
> **'이 종목이 좋아 보인다'가 아니라**  
> **'시장이 이 종목에 대해 합의했다'는 선언이다."**

---

## 📝 구현 체크리스트

- [ ] Sector Gate 로직 구현
- [ ] Structure Score 계산 (4가지 조건)
- [ ] Flow Score 계산 (3가지 조건)
- [ ] Checklist 동적 기준 (SCL 기반)
- [ ] Confirmation Rule (2회 연속)
- [ ] 승격 실행 함수
- [ ] 행동 규칙 자동 변경
- [ ] 승격 멘트 자동 생성
- [ ] 로그 및 히스토리 관리
- [ ] 금지 규칙 Validation

---

이 알고리즘으로 **Leader는 시스템만 만들 수 있습니다.**
