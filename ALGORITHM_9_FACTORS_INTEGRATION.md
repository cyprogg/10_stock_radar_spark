# 🎯 Decision Stream - 9요소 통합 알고리즘

## 철학: 입체적 시장 분석

**"주가는 가치가 아니라 돈이 움직이는 방향으로 간다"**

Decision Stream은 단순한 밸류에이션이나 모멘텀을 넘어, 시장의 **9가지 핵심 요소**를 통합하여 투자 판단을 지원합니다.

---

## 📊 전체 구조

```
┌─────────────────────────────────────────────────────────────────┐
│                    Decision Stream Engine                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │   Level 1    │───▶│   Level 2    │───▶│   Level 3    │      │
│  │ Market Regime│    │Sector Scoring│    │Stock Funnel  │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│         │                    │                    │              │
│         ▼                    ▼                    ▼              │
│    Risk-On/Off          SURGE 신호         9요소 종합 판단      │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 9가지 핵심 요소                                          │   │
│  │ 1. 자금 흐름 ⭐ | 2. 사이클 | 3. 기업의 질               │   │
│  │ 4. 지배구조 | 5. 서사 | 6. 하방 리스크                  │   │
│  │ 7. 시간 적합성 | 8. 가치 | 9. 모멘텀                    │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Level 1: Market Regime (시장 상태)

### 목적
시장이 Risk-On (공격) vs Risk-Off (방어) 중 어느 국면인지 판단

### 3가지 기준 (2/3 이상 충족 시 Risk-On)

1. **Market Breadth (필수)**: 상승 종목 수 / 하락 종목 수 ≥ 1.2:1
2. **Volatility (중요)**: VKOSPI ≤ 20 또는 하락 추세
3. **Theme Persistence (보조)**: 동일 테마 3일 이상 지속

### 계산 로직

```python
def calculate_market_regime(data):
    """
    Risk-On/Off 판정
    
    Returns:
        state: "RISK_ON" or "RISK_OFF"
        score: 0~3 (충족된 기준 수)
        factors: {breadth: bool, volatility: bool, theme: bool}
    """
    # 1. Breadth 체크
    breadth_ok = (data['up_count'] / data['down_count']) >= 1.2
    
    # 2. Volatility 체크
    volatility_ok = (data['vkospi'] <= 20) or is_declining(data['vkospi'])
    
    # 3. Theme 체크
    theme_ok = check_theme_persistence(data['themes'], days=3)
    
    # 점수 계산
    score = sum([breadth_ok, volatility_ok, theme_ok])
    
    # 판정
    state = "RISK_ON" if score >= 2 else "RISK_OFF"
    
    return {
        "state": state,
        "score": score,
        "max_score": 3,
        "factors": {
            "breadth": breadth_ok,
            "volatility": volatility_ok,
            "theme": theme_ok
        },
        "note": "Risk_ON = 사도 죽지 않을 확률이 높다"
    }
```

---

## 🔥 Level 2: Sector Scoring (섹터 분석)

### 목적
자금이 어디로 흐르는지 추적 (가장 중요한 요소)

### 4가지 구성 요소

1. **Flow (자금 흐름)** - 30% 가중치
   - 거래대금 5~20일 증가율
   - 기관/외국인 순매수 비율
   - ETF 자금 유입

2. **Structure (가격 구조)** - 25% 가중치
   - 고점/저점 상승 여부 (Higher High, Higher Low)
   - 조정 시 거래량 감소
   - 핵심 이평선(20/60) 위 유지

3. **Narrative (서사)** - 25% 가중치
   - 뉴스/정책 키워드 빈도
   - 공시 이벤트 (수주, 가이던스, 실적)
   - 글로벌 담론 연결성

4. **Risk (리스크)** - -20% 가중치
   - 과열/분배 봉 패턴
   - 테마 말기 급등주
   - 유동성/갭 리스크

### 계산 로직

```python
def calculate_sector_score(sector_data):
    """
    섹터 점수 계산 (0~100)
    
    Returns:
        flow_score: 자금 흐름 점수
        flow_signal: "SURGE" (≥70) or "NORMAL"
        duration: 지속 기간
    """
    # 1. Flow Score (30%)
    flow_score = (
        volume_increase_rate(sector_data) * 0.4 +
        institution_net_buy(sector_data) * 0.3 +
        foreign_net_buy(sector_data) * 0.3
    ) * 30
    
    # 2. Structure Score (25%)
    structure_score = (
        check_higher_high(sector_data) * 0.4 +
        check_higher_low(sector_data) * 0.3 +
        check_above_ma(sector_data, [20, 60]) * 0.3
    ) * 25
    
    # 3. Narrative Score (25%)
    narrative_score = (
        news_frequency(sector_data) * 0.4 +
        policy_driver(sector_data) * 0.3 +
        global_theme_link(sector_data) * 0.3
    ) * 25
    
    # 4. Risk Score (-20%)
    risk_score = (
        distribution_pattern(sector_data) * 0.4 +
        late_stage_risk(sector_data) * 0.3 +
        liquidity_risk(sector_data) * 0.3
    ) * -20
    
    # 총점
    total_score = flow_score + structure_score + narrative_score + risk_score
    
    # SURGE 판정
    flow_signal = "SURGE" if total_score >= 70 else "NORMAL"
    
    # 지속 기간
    duration = calculate_surge_duration(sector_data)
    
    return {
        "sector": sector_data['name'],
        "flow_score": round(total_score, 1),
        "flow_signal": flow_signal,
        "duration": duration,
        "components": {
            "flow": flow_score,
            "structure": structure_score,
            "narrative": narrative_score,
            "risk": risk_score
        }
    }
```

---

## 🎯 Level 3: Stock Funnel (종목 분류)

### 목적
9가지 요소 종합하여 Leader / Follower / No-Go 분류

### 9요소 통합 판정

```python
def classify_stock_9_factors(stock, sector):
    """
    9가지 요소 종합 판단
    
    Returns:
        classification: "LEADER", "FOLLOWER", or "NO_GO"
        scores: 각 요소별 점수
        action: 투자 행동 가이드
    """
    
    # ========== 필수 체크 (7가지) ==========
    
    # 1. 자금 흐름 ⭐ (최우선)
    flow_score = calculate_capital_flow(stock)
    # - 거래대금 증가
    # - 기관/외국인 순매수
    # - ETF 자금 유입
    
    # 2. 사이클
    cycle_fit = check_cycle_fit(stock, sector)
    # - 경기 국면 (확장/둔화/침체/회복)
    # - 산업 사이클 (초기/성장/성숙/쇠퇴)
    # - 정책 사이클 (금리, 재정, 지정학)
    
    # 3. 기업의 질
    quality_score = calculate_quality(stock)
    # - 부채 구조 (만기, 금리)
    # - 현금흐름 안정성
    # - 영업이익 반복 가능성
    # - 원가 전가력 (가격 결정권)
    
    # 4. 지배구조
    governance_score = calculate_governance(stock)
    # - 자사주 매입/소각
    # - 주주환원 정책
    # - 대주주 지분 구조
    # - 과거 위기 대응 기록
    
    # 5. 서사 (Narrative)
    narrative_score = calculate_narrative(stock)
    # - 미래 가능성
    # - 시장 이해도
    # - 글로벌 담론 연결성
    
    # 6. 하방 리스크
    risk_score = calculate_downside_risk(stock)
    # - 하방 제한 구조
    # - 악재 반영도
    # - 레버리지/환율/원자재 노출
    
    # 7. 시간 적합성
    time_fit = check_time_fit(stock)
    # - 기업 성장 시간표
    # - 자금 회전 속도
    # - 기회비용
    
    # ========== 보조 체크 (2가지) ==========
    
    # 8. 가치 (Valuation)
    value_score = calculate_valuation(stock)
    # - PER, PBR, PSR
    # - 동종 업계 대비
    # - 역사적 범위
    
    # 9. 모멘텀 품질 (진짜 vs 가짜) ⭐ 중요!
    momentum_quality = calculate_momentum_quality(stock, sector)
    # - 섹터 동반 상승 (가장 중요)
    # - 기관/외국인 동참
    # - 거래대금 지속성
    # - 뉴스 성격 (정책/수주 vs 루머)
    # - 커뮤니티 과열 체크
    # - 과거 패턴 분석
    
    # ========== 종합 판단 ==========
    
    # 필수 7요소 체크
    required_pass = (
        flow_score >= 70 and          # 자금 흐름 최우선
        cycle_fit and                 # 사이클 적합
        quality_score >= 60 and       # 기업 질 기준
        governance_score >= 50 and    # 지배구조 최소
        narrative_score >= 60 and     # 서사 존재
        risk_score <= 30 and          # 하방 리스크 제한
        time_fit                      # 시간 적합
    )
    
    if not required_pass:
        return {
            "classification": "NO_GO",
            "action": "AVOID",
            "reason": "필수 요소 미달"
        }
    
    # 가짜 모멘텀 즉시 탈락 ⭐
    if momentum_quality['quality'] == "FAKE":
        return {
            "classification": "NO_GO",
            "action": "AVOID",
            "reason": "가짜 모멘텀 감지 (혼자 오르는 종목)",
            "momentum_details": momentum_quality
        }
    
    # 진짜 모멘텀 + Follower = Leader로 승격 ⭐
    if momentum_quality['quality'] == "REAL" and momentum_quality['score'] >= 70:
        classification = "LEADER"
        action = "BUY_NOW"  # 진짜 모멘텀이면 즉시 매수
    elif momentum_quality['score'] >= 50:
        classification = "FOLLOWER"
        action = "BUY_PULLBACK"  # 눌림 매수 대기
    else:
        classification = "FOLLOWER"
        action = "WATCH"  # 관찰만
    
    return {
        "classification": classification,
        "action": action,
        "scores": {
            "1_flow": flow_score,
            "2_cycle": cycle_fit,
            "3_quality": quality_score,
            "4_governance": governance_score,
            "5_narrative": narrative_score,
            "6_risk": risk_score,
            "7_time_fit": time_fit,
            "8_value": value_score,
            "9_momentum_quality": momentum_quality['score']
        },
        "momentum_details": momentum_quality,
        "key_message": "혼자 오르면 위험, 같이 오르면 돈 냄새"
    }
            "9_momentum": momentum_score
        }
    }
```

---

## 🎬 실전 예시

### Case 1: 방산 섹터 - LMT (Lockheed Martin)

```python
lmt_analysis = classify_stock_9_factors(
    stock="LMT",
    sector="방산"
)

# 결과:
{
    "classification": "FOLLOWER",
    "action": "BUY_PULLBACK",
    "scores": {
        "1_flow": 97,          # ✅ SURGE
        "2_cycle": True,       # ✅ 지정학 긴장
        "3_quality": 85,       # ✅ 현금흐름 우수
        "4_governance": 80,    # ✅ 주주환원 우수
        "5_narrative": 90,     # ✅ 국방 담론
        "6_risk": 20,          # ✅ 제한적
        "7_time_fit": True,    # ✅ 중기 적합
        "8_value": 70,         # ✅ 적정
        "9_momentum": 62       # ⚠️ 아직 돌파 전
    },
    "recommendation": "섹터는 강하나 종목은 아직 돌파 전. 눌림 매수 기회 대기"
}
```

### Case 2: 헬스케어 - JNJ (Johnson & Johnson)

```python
jnj_analysis = classify_stock_9_factors(
    stock="JNJ",
    sector="헬스케어"
)

# 결과:
{
    "classification": "LEADER",
    "action": "BUY_NOW",
    "scores": {
        "1_flow": 96,          # ✅ SURGE
        "2_cycle": True,       # ✅ 방어 수요
        "3_quality": 90,       # ✅ 최상급
        "4_governance": 95,    # ✅ 배당 귀족주
        "5_narrative": 85,     # ✅ 고령화
        "6_risk": 10,          # ✅ 매우 낮음
        "7_time_fit": True,    # ✅ 중장기 적합
        "8_value": 75,         # ✅ 적정
        "9_momentum": 80       # ✅ 추세 중
    },
    "recommendation": "안정형 투자자 최적. 추세 추종 전략"
}
```

---

## 🎯 투자 성향별 가중치

### 공격적 투자자
```python
AGGRESSIVE_WEIGHTS = {
    "flow": 0.35,        # 자금 흐름
    "momentum": 0.25,    # 모멘텀
    "narrative": 0.20,   # 서사
    "cycle": 0.10,       # 사이클
    "others": 0.10       # 기타
}
```

### 균형 투자자
```python
BALANCED_WEIGHTS = {
    "flow": 0.30,        # 자금 흐름
    "quality": 0.20,     # 기업의 질
    "cycle": 0.15,       # 사이클
    "momentum": 0.15,    # 모멘텀
    "others": 0.20       # 기타
}
```

### 안정형 투자자
```python
CONSERVATIVE_WEIGHTS = {
    "quality": 0.30,      # 기업의 질
    "governance": 0.25,   # 지배구조
    "risk": 0.20,         # 하방 리스크
    "flow": 0.15,         # 자금 흐름
    "others": 0.10        # 기타
}
```

---

## 📚 핵심 메시지

1. **자금 흐름이 최우선** - 돈이 들어오지 않는 가치주는 오래 눌립니다
2. **사이클을 읽어라** - 기업은 혼자 움직이지 않습니다
3. **질이 회복 속도를 결정** - 불황 시 생존율이 다릅니다
4. **지배구조가 수익의 절반** - 회사 실적 ≠ 주주 수익
5. **서사가 없으면 리레이팅 없음** - 주가 = 팩트 + 이야기
6. **하방부터 체크** - 살아남는 것이 우선입니다
7. **시간표가 맞아야** - 좋은 기업 ≠ 지금 좋은 투자
8. **가치는 기본** - 하지만 충분하지 않습니다
9. **모멘텀 품질이 결정적** ⭐ - **혼자 오르면 위험, 같이 오르면 돈 냄새**

---

## 🎉 결론

Decision Stream은 **9가지 요소를 통합**하여:
- 💰 돈의 흐름을 읽고
- 🔄 시장의 사이클을 이해하며
- 🛡️ 리스크를 관리하고
- 📈 최적의 타이밍을 제시하며
- ⭐ **진짜 모멘텀과 가짜 모멘텀을 구분합니다**

**"지금 질문 수준을 보면, 이미 한 단계 위를 보고 계십니다."**

📘 **모멘텀 품질 상세**: [MOMENTUM_QUALITY_FRAMEWORK.md](MOMENTUM_QUALITY_FRAMEWORK.md)
