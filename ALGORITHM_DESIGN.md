# 중기 스윙 투자 알고리즘 설계서

## 📐 전체 프레임워크 구조

```
┌─────────────────────────────────────────────────────────────┐
│                    Decision Stream Engine                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Level 1    │───▶│   Level 2    │───▶│   Level 3    │  │
│  │ Market Regime│    │Sector Scoring│    │Stock Funnel  │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                    │                    │          │
│         ▼                    ▼                    ▼          │
│    Risk-On/Off          SURGE 신호         Leader/Follower  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Level 1: Market Regime Algorithm

### **목적**
시장이 Risk-On (공격) vs Risk-Off (방어) 중 어느 국면인지 판단

### **입력 데이터**
1. **금리** (Interest Rate)
   - 10년물 국채 수익률
   - 최근 20일 변화율

2. **환율** (FX Rate)
   - USD/KRW (원/달러)
   - 최근 20일 변화율

3. **지수** (Index)
   - KOSPI / S&P 500
   - 20일/60일 이동평균선 위치
   - 고점 대비 낙폭

4. **변동성** (Volatility)
   - VIX 지수
   - KOSPI 변동성 지수 (VKOSPI)

### **계산 로직**

```python
def calculate_market_regime(data):
    """
    Market Regime 점수 계산 (0~100)
    """
    score = 0
    factors = []
    
    # 1) 금리 점수 (25점 만점)
    interest_rate_score = 0
    if data['interest_rate_change_20d'] < -5:  # 금리 하락
        interest_rate_score = 25
        factors.append("금리 하락 (완화)")
    elif data['interest_rate_change_20d'] < 0:
        interest_rate_score = 15
        factors.append("금리 안정")
    elif data['interest_rate_change_20d'] > 5:  # 금리 급등
        interest_rate_score = 0
        factors.append("금리 급등 (긴축)")
    else:
        interest_rate_score = 10
        factors.append("금리 소폭 상승")
    
    # 2) 환율 점수 (20점 만점)
    fx_score = 0
    if data['usdkrw_change_20d'] < -2:  # 원화 강세
        fx_score = 20
        factors.append("원화 강세")
    elif data['usdkrw_change_20d'] < 0:
        fx_score = 15
        factors.append("환율 안정")
    elif data['usdkrw_change_20d'] > 3:  # 원화 약세
        fx_score = 5
        factors.append("원화 약세")
    else:
        fx_score = 10
        factors.append("환율 보합")
    
    # 3) 지수 점수 (35점 만점)
    index_score = 0
    
    # 3-1) 이동평균선 배치 (15점)
    if data['index_above_ma20'] and data['index_above_ma60']:
        index_score += 15
        factors.append("지수 이평선 상승 배치")
    elif data['index_above_ma20']:
        index_score += 10
        factors.append("지수 20일선 위")
    else:
        index_score += 0
        factors.append("지수 20일선 하락")
    
    # 3-2) 고점 대비 낙폭 (20점)
    drawdown = data['index_drawdown_from_high']
    if drawdown < 5:  # 고점 근처
        index_score += 20
        factors.append("지수 고점 근처")
    elif drawdown < 10:
        index_score += 15
        factors.append("지수 소폭 조정")
    elif drawdown < 20:
        index_score += 10
        factors.append("지수 중간 조정")
    else:
        index_score += 5
        factors.append("지수 약세")
    
    # 4) 변동성 점수 (20점 만점) - 역산
    vix_score = 0
    if data['vix'] < 15:  # 낮은 변동성 = 안정
        vix_score = 20
        factors.append("변동성 낮음 (안정)")
    elif data['vix'] < 20:
        vix_score = 15
        factors.append("변동성 보통")
    elif data['vix'] < 30:
        vix_score = 10
        factors.append("변동성 상승")
    else:
        vix_score = 0
        factors.append("변동성 급등 (공포)")
    
    # 총점 계산
    score = interest_rate_score + fx_score + index_score + vix_score
    
    # Risk-On / Risk-Off 판정
    if score >= 70:
        state = "RISK_ON"
        playbook = "공격적 진입"
    elif score >= 50:
        state = "RISK_ON"
        playbook = "눌림 매수"
    elif score >= 30:
        state = "RISK_OFF"
        playbook = "선별 매수"
    else:
        state = "RISK_OFF"
        playbook = "현금 대기"
    
    return {
        "state": state,
        "risk_score": score,
        "playbook": playbook,
        "factors": factors,
        "breakdown": {
            "interest_rate": interest_rate_score,
            "fx": fx_score,
            "index": index_score,
            "volatility": vix_score
        }
    }
```

---

## 🔥 Level 2: Sector Scoring Algorithm

### **목적**
어느 섹터에 자금이 집중되는지 4가지 요소로 점수화

### **섹터 점수 = Flow(30%) + Structure(25%) + Narrative(25%) - Risk(20%)**

### **2-1) Flow Score (자금 유입 점수) - 30점 만점**

```python
def calculate_flow_score(sector_data):
    """
    자금 유입 점수 계산
    """
    score = 0
    
    # 1) 거래대금 증가율 (5일 vs 20일 평균) - 15점
    volume_increase = sector_data['volume_5d'] / sector_data['volume_20d']
    if volume_increase > 1.5:  # 50% 이상 증가
        score += 15
    elif volume_increase > 1.2:
        score += 10
    elif volume_increase > 1.0:
        score += 5
    
    # 2) 외국인 순매수 (10점)
    foreign_net_buy = sector_data['foreign_net_buy_5d']
    if foreign_net_buy > 0 and sector_data['foreign_net_buy_20d'] > 0:
        score += 10  # 지속적 매수
    elif foreign_net_buy > 0:
        score += 5   # 최근 매수 전환
    
    # 3) 기관 순매수 (5점)
    institution_net_buy = sector_data['institution_net_buy_5d']
    if institution_net_buy > 0:
        score += 5
    
    return score
```

### **2-2) Structure Score (가격 구조 점수) - 25점 만점**

```python
def calculate_structure_score(sector_data):
    """
    가격 구조 점수 계산
    """
    score = 0
    
    # 1) 고점/저점 상승 (10점)
    if sector_data['higher_high'] and sector_data['higher_low']:
        score += 10  # 상승 추세
    elif sector_data['higher_low']:
        score += 5   # 바닥 다지기
    
    # 2) 조정 시 거래량 감소 (5점)
    if sector_data['volume_on_pullback'] < sector_data['volume_on_rally'] * 0.7:
        score += 5  # 건강한 조정
    
    # 3) 핵심 이평선 (20일/60일) 위 유지 (10점)
    if sector_data['above_ma20'] and sector_data['above_ma60']:
        score += 10
    elif sector_data['above_ma20']:
        score += 5
    
    return score
```

### **2-3) Narrative Score (서사 점수) - 25점 만점**

```python
def calculate_narrative_score(sector_data, news_db):
    """
    뉴스/정책 서사 점수 계산
    """
    score = 0
    
    # 1) 뉴스 키워드 빈도 (15점)
    keyword_count = count_news_keywords(sector_data['sector'], news_db, days=30)
    
    if keyword_count > 50:
        news_score = 15
    elif keyword_count > 30:
        news_score = 10
    elif keyword_count > 10:
        news_score = 5
    else:
        news_score = 0
    
    # 2) 신뢰도 가중치 (×0.5 ~ ×1.5)
    reliability = calculate_news_reliability(sector_data['sector'], news_db)
    # reliability = 정책/공시(1.5) > 계약(1.2) > 전망(0.8) > 루머(0.5)
    
    news_score = news_score * reliability
    score += min(news_score, 15)  # 최대 15점
    
    # 3) 공시 이벤트 (10점)
    events = sector_data['disclosure_events_30d']
    event_score = 0
    
    if '수주' in events or '실적' in events:
        event_score += 5
    if '가이던스' in events or '투자' in events:
        event_score += 5
    
    score += event_score
    
    return score

def calculate_news_reliability(sector, news_db):
    """
    뉴스 신뢰도 가중치
    """
    high_reliability = ['정책', '법안', '계약', '공시', '수주']
    medium_reliability = ['투자', '실적', '가이던스']
    low_reliability = ['전망', '예상', '가능성']
    
    recent_news = get_recent_news(sector, news_db, days=30)
    
    high_count = sum(1 for n in recent_news if any(k in n['title'] for k in high_reliability))
    medium_count = sum(1 for n in recent_news if any(k in n['title'] for k in medium_reliability))
    low_count = sum(1 for n in recent_news if any(k in n['title'] for k in low_reliability))
    
    total = high_count + medium_count + low_count
    if total == 0:
        return 1.0
    
    weighted = (high_count * 1.5 + medium_count * 1.0 + low_count * 0.5) / total
    return weighted
```

### **2-4) Risk Score (리스크 점수) - -20점 (감점)**

```python
def calculate_risk_score(sector_data):
    """
    리스크 점수 계산 (감점 요소)
    """
    penalty = 0
    
    # 1) 과열/분배 봉 패턴 (-10점)
    if sector_data['has_distribution_candle']:  # 장대 음봉
        penalty += 10
    
    # 2) 테마 말기 패턴 (-5점)
    # 3~5번째 급등주가 나타나면 테마 말기
    if sector_data['late_movers_count'] >= 3:
        penalty += 5
    
    # 3) 유동성 리스크 (-3점)
    if sector_data['avg_daily_volume'] < sector_data['threshold_volume']:
        penalty += 3
    
    # 4) 갭 리스크 (-2점)
    if sector_data['gap_up_days_5d'] >= 3:  # 5일 중 3일 갭상승
        penalty += 2
    
    return -penalty
```

### **2-5) 최종 섹터 점수**

```python
def calculate_sector_final_score(sector_data, news_db):
    """
    섹터 최종 점수 계산
    """
    flow = calculate_flow_score(sector_data)          # 0~30
    structure = calculate_structure_score(sector_data) # 0~25
    narrative = calculate_narrative_score(sector_data, news_db)  # 0~25
    risk = calculate_risk_score(sector_data)          # -20~0
    
    total = flow + structure + narrative + risk  # 최대 100점
    total = max(0, total)  # 음수 방지
    
    # SURGE 신호 판정
    if total >= 80 and flow >= 20:
        signal = "SURGE"
    elif total >= 60:
        signal = "NORMAL"
    elif total >= 40:
        signal = "WARN"
    else:
        signal = "WEAK"
    
    return {
        "sector": sector_data['sector'],
        "total_score": total,
        "signal": signal,
        "breakdown": {
            "flow": flow,
            "structure": structure,
            "narrative": narrative,
            "risk": risk
        }
    }
```

---

## 🎯 Level 3: Stock Funnel Algorithm

### **목적**
섹터 내 종목을 Leader / Follower / No-Go로 자동 분류

### **분류 기준**

| 구분 | Leader (선도주) | Follower (추종주) | No-Go (회피) |
|------|----------------|------------------|-------------|
| **상대강도** | RS > 110 | 100 < RS < 110 | RS < 100 |
| **신고가 여부** | 20일 신고가 | 20일 고점 근처 | 조정 중 |
| **거래량** | 평균 200% 이상 | 평균 120% 이상 | 평균 이하 |
| **이평선** | 20일/60일 위 | 20일선 위 | 20일선 아래 |

### **계산 로직**

```python
def calculate_relative_strength(stock, sector_index, period=20):
    """
    상대강도 (RS) 계산
    RS = (종목 수익률 / 섹터 수익률) × 100
    """
    stock_return = (stock['close'] - stock['close_20d_ago']) / stock['close_20d_ago']
    sector_return = (sector_index['close'] - sector_index['close_20d_ago']) / sector_index['close_20d_ago']
    
    if sector_return == 0:
        return 100
    
    rs = (stock_return / sector_return) * 100
    return rs

def classify_stock(stock, sector_index):
    """
    종목 분류: Leader / Follower / No-Go
    """
    # 1) 상대강도 계산
    rs = calculate_relative_strength(stock, sector_index)
    
    # 2) 신고가 여부
    is_new_high_20d = stock['close'] >= stock['high_20d'] * 0.98
    
    # 3) 거래량
    volume_ratio = stock['volume'] / stock['avg_volume_20d']
    
    # 4) 이평선 위치
    above_ma20 = stock['close'] > stock['ma20']
    above_ma60 = stock['close'] > stock['ma60']
    
    # 분류 로직
    if rs > 110 and is_new_high_20d and volume_ratio > 2.0 and above_ma20 and above_ma60:
        return "LEADER"
    
    elif rs > 100 and volume_ratio > 1.2 and above_ma20:
        return "FOLLOWER"
    
    else:
        return "NO_GO"

def rank_stocks_in_funnel(stocks, sector_index):
    """
    Funnel 내 종목 랭킹
    """
    results = {"leader": [], "follower": [], "no_go": []}
    
    for stock in stocks:
        category = classify_stock(stock, sector_index)
        
        # 점수 계산 (정렬용)
        score = calculate_stock_score(stock, sector_index)
        
        stock_info = {
            "ticker": stock['ticker'],
            "name": stock['name'],
            "price": stock['close'],
            "rs": calculate_relative_strength(stock, sector_index),
            "score": score
        }
        
        if category == "LEADER":
            results["leader"].append(stock_info)
        elif category == "FOLLOWER":
            results["follower"].append(stock_info)
        else:
            results["no_go"].append(stock_info)
    
    # 점수 순 정렬
    results["leader"].sort(key=lambda x: x['score'], reverse=True)
    results["follower"].sort(key=lambda x: x['score'], reverse=True)
    
    return results

def calculate_stock_score(stock, sector_index):
    """
    종목 종합 점수 (0~100)
    """
    score = 0
    
    # RS (40점)
    rs = calculate_relative_strength(stock, sector_index)
    score += min((rs - 100) * 2, 40)  # RS 110 = 20점, RS 120 = 40점
    
    # 거래량 (30점)
    volume_ratio = stock['volume'] / stock['avg_volume_20d']
    score += min(volume_ratio * 10, 30)  # 3배 = 30점
    
    # 가격 위치 (20점)
    price_position = (stock['close'] - stock['low_20d']) / (stock['high_20d'] - stock['low_20d'])
    score += price_position * 20
    
    # 이평선 배치 (10점)
    if stock['close'] > stock['ma60']:
        score += 10
    elif stock['close'] > stock['ma20']:
        score += 5
    
    return min(score, 100)
```

---

## 📊 알고리즘 출력 형식

### **Market Regime**
```json
{
  "state": "RISK_ON",
  "risk_score": 72,
  "playbook": "눌림 매수",
  "factors": ["금리 안정", "환율 안정", "지수 20일선 위", "변동성 낮음"],
  "breakdown": {
    "interest_rate": 15,
    "fx": 15,
    "index": 25,
    "volatility": 17
  }
}
```

### **Sector Score**
```json
{
  "sector": "방산",
  "total_score": 87,
  "signal": "SURGE",
  "breakdown": {
    "flow": 28,
    "structure": 23,
    "narrative": 22,
    "risk": -6
  },
  "evidence": {
    "pro": [
      "거래대금 5일 평균 50% 증가",
      "외국인 3일 연속 순매수",
      "폴란드 방산 수출 계약 체결"
    ],
    "con": [
      "5일 중 2일 갭상승 (갭 리스크)",
      "단기 과열 신호 (RSI 70 초과 종목 30%)"
    ]
  }
}
```

### **Stock Funnel**
```json
{
  "sector": "방산",
  "leader": [
    {
      "ticker": "012450",
      "name": "한화에어로스페이스",
      "price": 185000,
      "rs": 125,
      "score": 88
    }
  ],
  "follower": [
    {
      "ticker": "272210",
      "name": "한화시스템",
      "price": 28500,
      "rs": 108,
      "score": 72
    }
  ],
  "no_go": []
}
```

---

## 🎯 알고리즘 구현 우선순위

### **Phase 1: 기본 계산 엔진**
1. Market Regime 계산 (금리/환율/지수/변동성)
2. Sector Flow Score (거래대금/순매수)
3. Stock RS & 분류 로직

### **Phase 2: 고급 분석**
1. Structure Score (가격 구조 분석)
2. Narrative Score (뉴스 키워드 분석)
3. Risk Score (과열/테마 말기 감지)

### **Phase 3: 신뢰도 & 근거**
1. 점수 클릭 시 근거 3개 + 반대 근거 2개
2. 출처 링크 (뉴스/공시)
3. 히스토리 트래킹 (점수 변화 추이)

---

## 📝 다음 단계

1. **데이터 소스 확보**
   - 금리/환율/지수 API
   - 거래대금/순매수 데이터
   - 뉴스 크롤링

2. **백엔드 구현**
   - Python 계산 엔진 (backend/algorithms/)
   - 일일 자동 업데이트

3. **프론트엔드 연동**
   - 점수 클릭 → 상세 분해 모달
   - 차트 시각화
   - 근거 표시

이 설계서를 기반으로 구현을 시작하시겠습니까?
