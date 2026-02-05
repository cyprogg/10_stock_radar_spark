# 🎯 단기·중기 매매용 실전 체크리스트

## 철학

**"단기·중기 매매의 목적은 많이 맞히는 것이 아니라 계좌를 지키며 반복하는 것"**

Decision Stream은 불필요한 매매의 70%를 자동으로 걸러내는 실전 체크리스트를 제공합니다.

---

## 0️⃣ 전제 확인 (이게 안 되면 매매 금지)

### 3가지 필수 질문

```
1. 이 종목은 투자가 아니라 트레이딩 대상인가?
2. 손절 기준을 사전에 숫자로 정했는가?
3. 이벤트 종료 시 미련 없이 나올 수 있는가?
```

👉 **하나라도 "아니오"면 진입 금지**

### Decision Stream 구현

```python
def check_prerequisite(trade):
    """
    전제 확인 (0단계)
    
    Returns:
        pass: True/False
        reason: 탈락 사유
    """
    
    # 1. 트레이딩 대상 확인
    is_trading = check_trading_eligible(trade)
    # - 변동성 충분
    # - 유동성 확보
    # - 이벤트 종료 시점 명확
    
    # 2. 손절 기준 설정
    has_stop_loss = (trade.get('stop_loss') is not None)
    
    # 3. 출구 전략 존재
    has_exit_plan = (trade.get('exit_plan') is not None)
    
    # 판정
    if not is_trading:
        return {"pass": False, "reason": "트레이딩 대상 아님"}
    if not has_stop_loss:
        return {"pass": False, "reason": "손절 기준 미설정"}
    if not has_exit_plan:
        return {"pass": False, "reason": "출구 전략 없음"}
    
    return {"pass": True}
```

---

## 1️⃣ 자금 유입 확인 (최우선)

### 체크 항목

```
☑ 최근 5~20거래일 거래대금 증가
☑ 기관/외국인 순매수 전환 또는 가속
☑ 테마 ETF, 섹터 ETF 동반 강세
```

### 📌 핵심 질문

**이 종목을 사는 '나 말고 다른 큰 손'이 있는가?**

❌ 개인만 몰리면 단기 급등 후 급락 확률 높음

### Decision Stream 구현

```python
def check_capital_inflow(stock):
    """
    자금 유입 확인 (1단계)
    
    Returns:
        score: 0~100
        signal: "STRONG", "MODERATE", or "WEAK"
    """
    
    # 1. 거래대금 증가
    volume_increase = calculate_volume_trend(stock, days=[5, 10, 20])
    # - 5일 평균 vs 20일 평균
    # - 지속적 증가 = 강한 신호
    
    # 2. 기관/외국인 순매수
    institution_net = get_institution_net_buy(stock, days=5)
    foreign_net = get_foreign_net_buy(stock, days=5)
    
    # - 둘 다 순매수: +40점
    # - 하나만: +20점
    # - 개인만 순매수: -20점 (경고)
    
    # 3. ETF 동반 강세
    etf_inflow = check_sector_etf_flow(stock.sector)
    # - 섹터 ETF 자금 유입: +20점
    
    total_score = (
        volume_increase * 40 +
        (institution_net + foreign_net) * 40 +
        etf_inflow * 20
    )
    
    # 판정
    if total_score >= 70:
        signal = "STRONG"  # 큰 손이 사고 있음
    elif total_score >= 40:
        signal = "MODERATE"  # 지켜볼 만함
    else:
        signal = "WEAK"  # 개인만 몰리는 중
    
    return {
        "score": total_score,
        "signal": signal,
        "message": "나 말고 다른 큰 손이 있는가?" if signal == "STRONG" else "개인만 몰리는 중"
    }
```

---

## 2️⃣ 모멘텀의 성격 분석 (진짜 vs 가짜)

### 진짜 모멘텀
```
✅ 정책, 제도, 수주, 실적 가이던스
✅ 산업 단위의 연쇄 상승
✅ 여러 종목이 동시에 움직임
```

### 가짜 모멘텀
```
❌ 단일 기사
❌ 루머성 재료
❌ 특정 유튜버·커뮤니티 확산
```

### 📌 강한 의견

**혼자 오르는 종목은 위험, 같이 오르는 종목은 돈 냄새**

### Decision Stream 구현

👉 **상세 구현**: [MOMENTUM_QUALITY_FRAMEWORK.md](MOMENTUM_QUALITY_FRAMEWORK.md)

---

## 3️⃣ 가격 구조 (차트는 "예측"이 아니라 "판단 도구")

### 체크 항목

```
☑ 고점·저점이 높아지는 구조
☑ 조정 시 거래량 감소
☑ 이동평균선(20·60일) 위 유지
```

### 📌 단기 기준

```
급등 직후 횡보 → 매집 가능성
급등 후 장대 음봉 → 분배 가능성
```

❌ **바닥 추측 매수 금지**

### Decision Stream 구현

```python
def check_price_structure(stock):
    """
    가격 구조 확인 (3단계)
    
    Returns:
        structure: "HEALTHY", "NEUTRAL", or "BROKEN"
        pattern: 매집/분배 패턴
    """
    
    # 1. Higher High, Higher Low
    hh_hl = check_higher_high_low(stock, days=60)
    
    # 2. 조정 시 거래량 감소
    correction_volume = check_correction_volume(stock)
    # - 하락 시 거래량 감소 = 건강
    # - 하락 시 거래량 증가 = 분배
    
    # 3. 이동평균선 위치
    ma_position = check_ma_position(stock, [20, 60])
    
    # 4. 급등 후 패턴 분석
    post_surge_pattern = analyze_post_surge(stock)
    # - 횡보 + 거래량 유지 = 매집
    # - 장대 음봉 + 거래량 증가 = 분배
    
    # 판정
    if hh_hl and correction_volume == "HEALTHY" and ma_position == "ABOVE":
        structure = "HEALTHY"
        message = "✅ 건강한 구조"
    elif post_surge_pattern == "DISTRIBUTION":
        structure = "BROKEN"
        message = "❌ 분배 패턴 (위험)"
    else:
        structure = "NEUTRAL"
        message = "⚠️ 관찰 필요"
    
    return {
        "structure": structure,
        "pattern": post_surge_pattern,
        "message": message
    }
```

---

## 4️⃣ 시간 프레임 정합성

### 시간 구분

**단기 (수일~2주)**
```
→ 뉴스·수급·변동성 중심
```

**중기 (1~3개월)**
```
→ 실적 가시성 + 산업 흐름
```

### 📌 질문

**이 재료는 며칠짜리인가, 몇 달짜리인가?**

시간을 잘못 잡으면 옳은 판단도 손실로 끝납니다.

### Decision Stream 구현

```python
def check_time_frame_fit(stock, catalyst):
    """
    시간 프레임 정합성 (4단계)
    
    Returns:
        timeframe: "SHORT", "MID", or "LONG"
        fit: True/False
        expected_duration: 예상 지속 기간
    """
    
    # 재료 분석
    catalyst_type = analyze_catalyst_type(catalyst)
    
    # 단기 재료
    if catalyst_type in ["뉴스", "수급 급변", "변동성 확대"]:
        timeframe = "SHORT"
        expected_duration = "수일~2주"
    
    # 중기 재료
    elif catalyst_type in ["실적 가이던스", "수주", "산업 흐름"]:
        timeframe = "MID"
        expected_duration = "1~3개월"
    
    # 장기 재료
    elif catalyst_type in ["정책 확정", "구조적 변화"]:
        timeframe = "LONG"
        expected_duration = "6개월~1년"
    
    # 사용자 보유 기간과 비교
    user_timeframe = get_user_preference("timeframe")
    fit = (timeframe == user_timeframe)
    
    return {
        "timeframe": timeframe,
        "fit": fit,
        "expected_duration": expected_duration,
        "message": f"이 재료는 {expected_duration}짜리입니다"
    }
```

---

## 5️⃣ 기대수익 vs 손실비 (Risk/Reward)

### 체크 항목

```
☑ 기대수익 ≥ 손실의 2배 이상
☑ 손절 라인이 명확한 가격대에 있는가?
☑ 변동성 대비 포지션 크기 적절한가?
```

### 📌 실전 공식

**10번 중 4번만 맞아도 계좌가 느는 구조인지 확인**

### Decision Stream 구현

```python
def check_risk_reward(trade):
    """
    Risk/Reward 확인 (5단계)
    
    Returns:
        ratio: 수익/손실 비율
        acceptable: True/False
    """
    
    entry_price = trade['entry_price']
    stop_loss = trade['stop_loss']
    target = trade['target']
    
    # 손실 크기
    max_loss = abs(entry_price - stop_loss)
    
    # 기대 수익
    expected_profit = abs(target - entry_price)
    
    # 비율 계산
    ratio = expected_profit / max_loss if max_loss > 0 else 0
    
    # 판정
    if ratio >= 2.0:
        acceptable = True
        message = f"✅ 수익/손실 비율 {ratio:.1f}:1 (우수)"
    elif ratio >= 1.5:
        acceptable = True
        message = f"⚠️ 수익/손실 비율 {ratio:.1f}:1 (최소 기준)"
    else:
        acceptable = False
        message = f"❌ 수익/손실 비율 {ratio:.1f}:1 (불충분)"
    
    # 포지션 크기 체크
    volatility = get_volatility(trade['stock'])
    position_size = calculate_safe_position(trade, volatility)
    
    return {
        "ratio": ratio,
        "acceptable": acceptable,
        "message": message,
        "recommended_position": position_size,
        "win_rate_needed": f"{100 / (1 + ratio):.0f}%"  # 손익분기 승률
    }
```

---

## 6️⃣ 시장 환경 필터 (개별주보다 우선)

### 체크 항목

```
☑ 코스피/코스닥 지수 방향
☑ 금리·환율 급변 여부
☑ 글로벌 증시 동조성
```

### 📌 강한 의견

**시장이 위험회피면, 개별주는 아무리 좋아도 제한적 상승**

### Decision Stream 구현

```python
def check_market_environment():
    """
    시장 환경 필터 (6단계)
    
    Returns:
        regime: "RISK_ON", "RISK_OFF"
        impact: 개별주 영향도
    """
    
    # 1. 지수 방향
    index_trend = check_index_trend(["KOSPI", "KOSDAQ", "S&P500"])
    
    # 2. 금리·환율 급변
    rate_change = check_rate_volatility()
    fx_change = check_fx_volatility()
    
    # 3. 글로벌 동조성
    global_sync = check_global_sync()
    
    # 판정
    if index_trend == "DOWN" and (rate_change or fx_change):
        regime = "RISK_OFF"
        impact = "HIGH"  # 개별주 영향 크다
        message = "❌ 시장 위험회피: 매매 자제 권장"
    elif global_sync == "NEGATIVE":
        regime = "RISK_OFF"
        impact = "MODERATE"
        message = "⚠️ 글로벌 조정: 신중 필요"
    else:
        regime = "RISK_ON"
        impact = "LOW"
        message = "✅ 시장 우호적: 개별주 매매 가능"
    
    return {
        "regime": regime,
        "impact": impact,
        "message": message
    }
```

---

## 7️⃣ 테마 피로도 체크

### 경고 신호

```
❌ 같은 테마 3~5번째 급등주인가?
❌ 뉴스 헤드라인에 "연일 급등"이 붙었는가?
❌ 초보 투자자 질문이 급증했는가?
```

### 📌 냉정한 기준

**사람들이 다 아는 테마는 이미 늦었을 가능성이 높다**

### Decision Stream 구현

```python
def check_theme_fatigue(stock, theme):
    """
    테마 피로도 체크 (7단계)
    
    Returns:
        stage: "EARLY", "MID", or "LATE"
        action: "BUY", "WATCH", or "AVOID"
    """
    
    # 1. 테마 내 급등주 순서
    surge_order = get_surge_order_in_theme(stock, theme)
    
    # 2. 뉴스 헤드라인 분석
    news_heat = analyze_news_headlines(theme)
    # - "연일", "급등", "주목" 키워드 빈도
    
    # 3. 커뮤니티 질문 빈도
    community_questions = get_community_heat(theme)
    # - 초보 질문 급증 = 말기 신호
    
    # 4. 테마 지속 기간
    theme_duration = get_theme_duration(theme)
    
    # 판정
    if surge_order <= 2 and theme_duration <= 5:
        stage = "EARLY"
        action = "BUY"
        message = "✅ 테마 초기 (진입 가능)"
    elif surge_order <= 4 and theme_duration <= 10:
        stage = "MID"
        action = "WATCH"
        message = "⚠️ 테마 중반 (신중 진입)"
    else:
        stage = "LATE"
        action = "AVOID"
        message = "❌ 테마 말기 (회피)"
    
    return {
        "stage": stage,
        "action": action,
        "surge_order": surge_order,
        "duration": f"{theme_duration}일",
        "message": message
    }
```

---

## 8️⃣ 출구 전략 (진입보다 중요)

### 체크 항목

```
☑ 목표가 분할 매도 계획
☑ 이벤트 종료 시 즉시 정리
☑ 추세 이탈 시 자동 손절
```

### 📌 실패하는 투자자의 공통점

**들어갈 때는 계획, 나올 때는 감정**

### Decision Stream 구현

```python
def check_exit_strategy(trade):
    """
    출구 전략 확인 (8단계)
    
    Returns:
        has_plan: True/False
        plan: 출구 전략 상세
    """
    
    # 1. 분할 매도 계획
    has_split_exit = (
        trade.get('target_1') is not None and
        trade.get('target_2') is not None
    )
    
    # 2. 이벤트 종료 시점
    has_event_exit = (trade.get('event_end_date') is not None)
    
    # 3. 손절 라인
    has_stop_loss = (trade.get('stop_loss') is not None)
    
    # 판정
    if has_split_exit and has_event_exit and has_stop_loss:
        has_plan = True
        message = "✅ 완벽한 출구 전략"
    elif has_stop_loss:
        has_plan = True
        message = "⚠️ 최소 손절 라인 존재"
    else:
        has_plan = False
        message = "❌ 출구 전략 없음 (위험)"
    
    return {
        "has_plan": has_plan,
        "message": message,
        "plan": {
            "target_1": trade.get('target_1'),
            "target_2": trade.get('target_2'),
            "stop_loss": trade.get('stop_loss'),
            "event_end": trade.get('event_end_date')
        }
    }
```

---

## 🧠 단기·중기 매매 최종 10문장 점검

### 자동 체크리스트

```python
def final_checklist(stock, trade):
    """
    최종 10문장 점검
    
    Returns:
        pass_count: 통과 항목 수
        result: "GO", "CAUTION", or "NO_GO"
    """
    
    checks = []
    
    # 1. 돈이 들어오고 있는가?
    checks.append(check_capital_inflow(stock)['signal'] == "STRONG")
    
    # 2. 혼자가 아닌 군집 상승인가?
    checks.append(check_momentum_quality(stock)['quality'] == "REAL")
    
    # 3. 재료의 수명은 충분한가?
    checks.append(check_time_frame_fit(stock, trade['catalyst'])['fit'])
    
    # 4. 가격 구조가 깨지지 않았는가?
    checks.append(check_price_structure(stock)['structure'] != "BROKEN")
    
    # 5. 시장은 우호적인가?
    checks.append(check_market_environment()['regime'] == "RISK_ON")
    
    # 6. 늦은 테마는 아닌가?
    checks.append(check_theme_fatigue(stock, trade['theme'])['stage'] != "LATE")
    
    # 7. 손절 가격이 명확한가?
    checks.append(trade.get('stop_loss') is not None)
    
    # 8. 기대수익이 손실보다 큰가?
    checks.append(check_risk_reward(trade)['ratio'] >= 2.0)
    
    # 9. 감정이 아닌 규칙으로 매매하는가?
    checks.append(check_prerequisite(trade)['pass'])
    
    # 10. 틀려도 살아남는 구조인가?
    checks.append(check_exit_strategy(trade)['has_plan'])
    
    # 판정
    pass_count = sum(checks)
    
    if pass_count >= 8:
        result = "GO"
        message = f"✅ {pass_count}/10 통과 - 진입 가능"
    elif pass_count >= 6:
        result = "CAUTION"
        message = f"⚠️ {pass_count}/10 통과 - 신중 진입"
    else:
        result = "NO_GO"
        message = f"❌ {pass_count}/10 통과 - 진입 금지"
    
    return {
        "pass_count": pass_count,
        "total": 10,
        "result": result,
        "message": message,
        "details": checks
    }
```

---

## 🎯 마지막으로, 솔직한 조언

### 핵심 메시지

**단기·중기 매매의 목적은 "많이 맞히는 것"이 아니라 "계좌를 지키며 반복하는 것"입니다.**

### 효과

이 체크리스트를 통과한 종목만 거래해도 **불필요한 매매의 70%는 자동으로 걸러집니다.**

### 통계적 근거

```
승률 40% × Risk/Reward 2:1 = 계좌 증가
승률 60% × Risk/Reward 1:1 = 계좌 정체
승률 80% × Risk/Reward 0.5:1 = 계좌 감소
```

👉 **승률보다 Risk/Reward가 중요합니다**

---

## 🎉 결론

Decision Stream의 실전 체크리스트:
- 🛡️ 0단계: 전제 확인으로 감정 매매 차단
- 💰 1단계: 큰 손 확인으로 함정 회피
- ⭐ 2단계: 진짜 모멘텀만 선별
- 📊 3단계: 가격 구조로 진입 타이밍 포착
- ⏰ 4단계: 시간 프레임 정합성 확인
- 📈 5단계: Risk/Reward로 기대값 계산
- 🌍 6단계: 시장 환경 필터
- 🔥 7단계: 테마 피로도 회피
- 🚪 8단계: 출구 전략 필수 확인
- ✅ 최종: 10문장 체크로 종합 판단

**"틀려도 살아남는 구조"를 만드는 것이 Decision Stream의 목표입니다.**
