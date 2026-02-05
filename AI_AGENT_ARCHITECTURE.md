# AI Agent 아키텍처 - Decision Stream

## 🎯 핵심 철학

**"설명 가능한 자동화"**
- 모든 판단에는 근거가 있다
- 모든 근거에는 반대 의견이 있다
- 모든 점수는 0~100으로 통일
- 모든 데이터에는 출처가 있다

---

## 🤖 5개 AI Agent 설계

### Agent 1: Market Regime Analyst 🌍
**역할:** "오늘 장이 어떤 장인지" 규칙 + 요약

#### 입력 데이터
```python
{
  # 금리
  "us_10y": 4.25,           # 미국 10년물 국채 수익률
  "us_10y_change_20d": -0.15, # 최근 20일 변화율
  
  # 환율
  "usd_krw": 1320,
  "usd_krw_change_20d": 0.8,
  
  # 지수
  "kospi": 2650,
  "kospi_vs_ma20": 1.02,    # 20일 이평 대비
  "kospi_vs_ma60": 1.05,    # 60일 이평 대비
  "kospi_from_high": -5.2,  # 고점 대비 낙폭 (%)
  
  "sp500": 5200,
  "sp500_vs_ma20": 1.03,
  "sp500_vs_ma60": 1.08,
  
  # 변동성
  "vix": 15.2,
  "vkospi": 18.5,
  
  # 시장 폭
  "kospi_advancers": 650,   # 상승 종목
  "kospi_decliners": 500,   # 하락 종목
  "breadth_ratio": 1.3      # 상승/하락 비율
}
```

#### 출력
```python
{
  "state": "RISK_ON" | "RISK_OFF",
  "score": 3,              # 0~3 (강도)
  "max_score": 3,
  "confidence": 85,        # 신뢰도 (%)
  
  "playbook": "눌림 매수 대기. 20일선 지지 확인 후 진입.",
  
  "signals": {
    "positive": [
      "VIX 15 이하 (안정)",
      "코스피 20일선/60일선 위",
      "상승/하락 비율 1.3:1"
    ],
    "negative": [
      "고점 대비 -5% (조정 중)"
    ]
  },
  
  "lasting_themes": ["방산", "헬스케어"],  # 2주 이상 지속 테마
  
  "sources": [
    {"type": "api", "name": "Yahoo Finance", "timestamp": "2026-01-27T09:00:00Z"},
    {"type": "api", "name": "KRX", "timestamp": "2026-01-27T09:05:00Z"}
  ]
}
```

#### 로직
```python
def calculate_market_regime(data):
    score = 0
    signals_pos = []
    signals_neg = []
    
    # 1) VIX 체크
    if data['vix'] < 15:
        score += 1
        signals_pos.append("VIX 15 이하 (안정)")
    elif data['vix'] > 25:
        score -= 1
        signals_neg.append("VIX 25 초과 (공포)")
    
    # 2) 이동평균 체크
    if data['kospi_vs_ma20'] > 1 and data['kospi_vs_ma60'] > 1:
        score += 1
        signals_pos.append("코스피 20일선/60일선 위")
    
    # 3) 시장 폭 체크
    if data['breadth_ratio'] > 1.2:
        score += 1
        signals_pos.append(f"상승/하락 비율 {data['breadth_ratio']:.1f}:1")
    
    # 4) 낙폭 체크
    if data['kospi_from_high'] < -10:
        signals_neg.append(f"고점 대비 {data['kospi_from_high']:.1f}% (과매도)")
    
    state = "RISK_ON" if score >= 2 else "RISK_OFF"
    
    return {
        "state": state,
        "score": max(0, min(3, score)),
        "signals": {"positive": signals_pos, "negative": signals_neg}
    }
```

---

### Agent 2: Sector Scout 🔍
**역할:** 섹터별 자금흐름/강도/뉴스를 합쳐 랭킹

#### 입력 데이터
```python
{
  "sector": "방산",
  
  # 자금 흐름
  "volume_change_20d": 2.5,      # 거래대금 20일 변화율 (배수)
  "foreign_net_buy_5d": 150,     # 외국인 5일 순매수 (억원)
  "inst_net_buy_5d": 200,        # 기관 5일 순매수 (억원)
  
  # 가격 강도
  "price_change_20d": 15.2,      # 20일 수익률 (%)
  "ma20_slope": 0.8,             # 20일선 기울기
  "new_high_stocks": 3,          # 신고가 종목 수
  
  # 뉴스/이벤트
  "news_count_7d": 25,           # 7일간 뉴스 건수
  "policy_keywords": ["수출", "계약"], # 정책 키워드
  "disclosure_count": 2          # 공시 건수
}
```

#### 출력
```python
{
  "sector": "방산",
  "flow_score": 97,       # 0~100
  "signal": "SURGE" | "NORMAL" | "WEAK",
  "duration": "2주",      # 테마 지속 기간
  
  "rank": 1,             # 전체 섹터 중 순위
  
  "breakdown": {
    "flow": 97,          # 자금 흐름 점수
    "structure": 85,     # 가격 구조 점수
    "narrative": 80      # 서사 점수
  },
  
  "why": [
    "거래대금 2.5배 증가 (20일 기준)",
    "외국인 150억 + 기관 200억 순매수",
    "정책 키워드 '수출/계약' 25건"
  ],
  
  "counter": [
    "신고가 종목 3개로 제한적",
    "테마 지속 2주차 (피로도 체크 필요)"
  ],
  
  "confidence": 88
}
```

#### 로직
```python
def score_sector(sector_data):
    # 1) 자금 흐름 점수 (0~100)
    flow = 0
    if sector_data['volume_change_20d'] > 2:
        flow += 40
    if sector_data['foreign_net_buy_5d'] > 100:
        flow += 30
    if sector_data['inst_net_buy_5d'] > 100:
        flow += 30
    
    # 2) 가격 구조 점수 (0~100)
    structure = 0
    if sector_data['price_change_20d'] > 10:
        structure += 50
    if sector_data['ma20_slope'] > 0.5:
        structure += 30
    structure += min(20, sector_data['new_high_stocks'] * 5)
    
    # 3) 서사 점수 (0~100)
    narrative = 0
    narrative += min(50, sector_data['news_count_7d'] * 2)
    narrative += len(sector_data['policy_keywords']) * 15
    narrative += min(20, sector_data['disclosure_count'] * 10)
    
    # 신호 판정
    signal = "SURGE" if flow >= 80 else ("NORMAL" if flow >= 50 else "WEAK")
    
    return {
        "flow_score": flow,
        "signal": signal,
        "breakdown": {
            "flow": flow,
            "structure": structure,
            "narrative": narrative
        }
    }
```

---

### Agent 3: Stock Screener 🎯
**역할:** 섹터 내부 종목을 Leader/Follower/No-go로 분류

#### 입력 데이터
```python
{
  "ticker": "005930",
  "name": "삼성전자",
  "sector": "반도체",
  
  # 9요소
  "flow_score": 85,          # Agent 계산
  "cycle_fit": True,         # 사이클 적합
  "quality_score": 90,
  "governance_score": 80,
  "narrative_score": 75,
  "risk_score": 15,
  "time_fit": True,
  
  # 모멘텀 품질
  "momentum_quality": {
    "sector_sync": True,     # 섹터 동반 상승
    "inst_participation": True,  # 기관 참여
    "news_type": "fundamental",  # fundamental | rumor | single
    "group_rally": True      # 여러 종목 동시 상승
  },
  
  # No-Go 체크
  "gap_up_with_distribution": False,
  "single_rumor": False,
  "late_theme": False,       # 3~5번째 급등주
  "no_structure": False      # 손절선 설정 불가
}
```

#### 출력
```python
{
  "classification": "LEADER" | "FOLLOWER" | "NO_GO",
  "action": "BUY_NOW" | "BUY_PULLBACK" | "AVOID",
  
  "scores": {
    "1_flow": 85,
    "2_cycle": True,
    "3_quality": 90,
    "4_governance": 80,
    "5_narrative": 75,
    "6_risk": 15,
    "7_time_fit": True,
    "8_value": 70,
    "9_momentum": 92        # ⭐ 모멘텀 품질
  },
  
  "why_leader": [
    "섹터 전체 상승 (진짜 모멘텀)",
    "기관/외국인 동시 매수",
    "펀더멘털 기반 뉴스 (수주/실적)"
  ],
  
  "counter": [
    "밸류에이션 고평가 구간",
    "단기 급등으로 조정 가능성"
  ],
  
  "confidence": 85
}
```

#### 로직 (핵심 6개 No-Go 규칙)
```python
def classify_stock(stock_data):
    # ========== No-Go 판정 (우선) ==========
    nogo_flags = []
    
    # 1) 단일 기사 급등 + 거래대금 폭증
    if (stock_data['momentum_quality']['news_type'] == 'single' and 
        stock_data['flow_score'] > 90):
        nogo_flags.append("단일 기사 급등")
    
    # 2) 갭 상승 후 장대 음봉
    if stock_data['gap_up_with_distribution']:
        nogo_flags.append("갭 상승 후 분배")
    
    # 3) 테마 내 5번째 이후 급등주
    if stock_data['late_theme']:
        nogo_flags.append("테마 말기")
    
    # 4) 개인 순매수 80%↑ + 기관 이탈
    if (stock_data.get('retail_dominance', 0) > 0.8 and 
        not stock_data['momentum_quality']['inst_participation']):
        nogo_flags.append("개인 독주")
    
    # 5) 핵심 이평(20/60) 동시 이탈
    if stock_data['no_structure']:
        nogo_flags.append("구조 파손")
    
    # 6) 손절선이 구조적으로 설정 불가
    if stock_data['risk_score'] > 50:
        nogo_flags.append("손절 불가")
    
    # 하나라도 해당 시 No-Go
    if nogo_flags:
        return {
            "classification": "NO_GO",
            "action": "AVOID",
            "reason": " | ".join(nogo_flags)
        }
    
    # ========== 9요소 필수 조건 체크 ==========
    mandatory_pass = (
        stock_data['flow_score'] >= 70 and
        stock_data['cycle_fit'] and
        stock_data['quality_score'] >= 60 and
        stock_data['governance_score'] >= 50 and
        stock_data['narrative_score'] >= 60 and
        stock_data['risk_score'] <= 30 and
        stock_data['time_fit']
    )
    
    if not mandatory_pass:
        return {
            "classification": "NO_GO",
            "action": "AVOID",
            "reason": "필수 요소 미달"
        }
    
    # ========== 모멘텀 품질로 Leader/Follower 구분 ==========
    momentum_score = calculate_momentum_quality(stock_data['momentum_quality'])
    
    if momentum_score >= 85:
        return {
            "classification": "LEADER",
            "action": "BUY_NOW",
            "scores": {...}
        }
    else:
        return {
            "classification": "FOLLOWER",
            "action": "BUY_PULLBACK",
            "scores": {...}
        }


def calculate_momentum_quality(mq):
    """모멘텀 품질 점수 계산 (0~100)"""
    score = 0
    
    # 진짜 모멘텀 조건
    if mq['sector_sync']:           # 섹터 동반 상승
        score += 35
    if mq['inst_participation']:    # 기관 참여
        score += 30
    if mq['news_type'] == 'fundamental':  # 펀더멘털 뉴스
        score += 25
    if mq['group_rally']:           # 여러 종목 동시 상승
        score += 10
    
    # 가짜 모멘텀 패널티
    if mq['news_type'] == 'rumor':
        score -= 50
    if mq['news_type'] == 'single':
        score -= 30
    
    return max(0, min(100, score))
```

---

### Agent 4: Trade Plan Builder 📋
**역할:** 사용자의 기간/성향에 맞춰 진입·손절·익절·분할 자동 설계

#### 입력
```python
{
  "ticker": "005930",
  "current_price": 75000,
  
  # 가격 구조
  "support_levels": [72000, 70000],  # 지지선
  "resistance_levels": [78000, 80000],  # 저항선
  "ma20": 73000,
  "ma60": 71000,
  
  # 변동성
  "atr_20d": 2500,           # 20일 평균 진폭
  "volatility": 3.2,         # 일간 변동성 (%)
  
  # 사용자 입력
  "period": "단기" | "중기",
  "risk_profile": "보수" | "중립" | "공격",
  "account_size": 10000000   # 선택 입력
}
```

#### 출력
```python
{
  "entry": {
    "breakout": 78500,       # 돌파 진입
    "pullback": 73500        # 눌림 진입
  },
  
  "stop_loss": 71500,        # ⚠️ 손절 먼저 고정
  
  "targets": {
    "conservative": 79500,   # 보수 목표
    "aggressive": 82000      # 공격 목표
  },
  
  "position_size": {
    "percent": 20,           # 계좌 대비 (%)
    "shares": 26,            # 주식 수
    "amount": 1950000        # 금액 (원)
  },
  
  "split_plan": [
    {"action": "진입", "percent": 50, "price": 73500},
    {"action": "추가", "percent": 50, "price": 72000},
    {"action": "익절", "percent": 50, "price": 79500},
    {"action": "익절", "percent": 50, "price": 82000}
  ],
  
  "why": [
    "20일선 73,000원 지지",
    "ATR 기반 손절 -4.7%",
    "리스크/리워드 1:2.5"
  ]
}
```

#### 로직
```python
def build_trade_plan(stock, user):
    # ========== 1) 손절 먼저 고정 (가장 중요) ==========
    if stock['ma20'] > stock['ma60']:
        stop_loss = stock['ma20'] * 0.98  # 20일선 -2%
    else:
        stop_loss = stock['support_levels'][0] * 0.97
    
    stop_loss = max(
        stop_loss,
        stock['current_price'] - 2 * stock['atr_20d']  # ATR 기반
    )
    
    # ========== 2) 진입가 설정 ==========
    entry_breakout = stock['resistance_levels'][0] * 1.005  # 저항 +0.5%
    entry_pullback = stock['ma20'] * 1.005                  # 20일선 +0.5%
    
    # ========== 3) 목표가 설정 (손절 대비 2배 이상) ==========
    risk = stock['current_price'] - stop_loss
    
    if user['risk_profile'] == '보수':
        target_conservative = stock['current_price'] + risk * 2
        target_aggressive = stock['current_price'] + risk * 3
    elif user['risk_profile'] == '공격':
        target_conservative = stock['current_price'] + risk * 3
        target_aggressive = stock['current_price'] + risk * 5
    else:  # 중립
        target_conservative = stock['current_price'] + risk * 2.5
        target_aggressive = stock['current_price'] + risk * 4
    
    # ========== 4) 포지션 사이즈 계산 ==========
    if user.get('account_size'):
        # 변동성 기반 계산 (Kelly Criterion 간소화)
        max_risk_per_trade = 0.02  # 거래당 최대 리스크 2%
        risk_amount = user['account_size'] * max_risk_per_trade
        
        position_size = risk_amount / risk
        position_percent = (position_size / user['account_size']) * 100
    else:
        # 기본값
        position_percent = 20 if user['risk_profile'] == '보수' else 30
    
    return {
        "entry": {...},
        "stop_loss": stop_loss,
        "targets": {...},
        "position_size": {...}
    }
```

---

### Agent 5: Devil's Advocate 😈
**역할:** "왜 이 판단이 틀릴 수 있는지" 2~3개 자동 제시

#### 입력
```python
{
  "recommendation": {
    "ticker": "005930",
    "action": "BUY_PULLBACK",
    "classification": "FOLLOWER",
    "scores": {...},
    "why": [...]
  }
}
```

#### 출력
```python
{
  "counter_arguments": [
    {
      "category": "밸류에이션",
      "point": "PER 25배로 업종 평균(18배) 대비 고평가",
      "severity": "medium",
      "source": "재무제표 분석"
    },
    {
      "category": "기술적",
      "point": "20일 이평 급등 후 이격도 8% (과열)",
      "severity": "low",
      "source": "차트 구조"
    },
    {
      "category": "모멘텀",
      "point": "섹터 내 3번째 급등주 (테마 피로도 체크 필요)",
      "severity": "high",
      "source": "섹터 분석"
    }
  ],
  
  "final_note": "⚠️ 이 종목은 FOLLOWER로 분류되었지만, 테마 피로도가 높아 진입 타이밍을 신중히 검토하세요. 눌림 매수 대기 권장."
}
```

#### 로직
```python
def generate_counter_arguments(recommendation):
    counters = []
    
    scores = recommendation['scores']
    
    # 1) 밸류에이션 체크
    if scores.get('8_value', 100) < 50:
        counters.append({
            "category": "밸류에이션",
            "point": "PER/PBR 기준 고평가 구간",
            "severity": "medium"
        })
    
    # 2) 리스크 체크
    if scores['6_risk'] > 20:
        counters.append({
            "category": "리스크",
            "point": f"하방 리스크 점수 {scores['6_risk']} (변동성 주의)",
            "severity": "high" if scores['6_risk'] > 30 else "medium"
        })
    
    # 3) 모멘텀 품질 체크
    if scores['9_momentum'] < 70:
        counters.append({
            "category": "모멘텀",
            "point": "모멘텀 품질 중간 수준 (진위 의심)",
            "severity": "high"
        })
    
    # 4) 테마 피로도 체크 (외부 데이터 필요)
    # ...
    
    return {"counter_arguments": counters[:3]}  # 최대 3개
```

---

## 📊 점수 엔진 (0~100 통일)

### 1) 자금 유입 점수 (Flow Score)
```python
def calculate_flow_score(data):
    score = 0
    
    # 거래대금 증가 (0~40점)
    if data['volume_change_5d'] > 1.5:
        score += 20
    if data['volume_change_20d'] > 2:
        score += 20
    
    # 외국인 순매수 (0~30점)
    if data['foreign_net_buy_5d'] > 0:
        score += 15
    if data['foreign_net_buy_20d'] > 0:
        score += 15
    
    # 기관 순매수 (0~30점)
    if data['inst_net_buy_5d'] > 0:
        score += 15
    if data['inst_net_buy_20d'] > 0:
        score += 15
    
    return min(100, score)
```

### 2) 가격 구조 점수 (Structure Score)
```python
def calculate_structure_score(data):
    score = 0
    
    # 고점/저점 상승 (0~30점)
    if data['higher_highs'] and data['higher_lows']:
        score += 30
    
    # 조정 시 거래량 감소 (0~20점)
    if data['pullback_with_low_volume']:
        score += 20
    
    # 이평선 위 유지 (0~50점)
    if data['price_vs_ma20'] > 1:
        score += 25
    if data['price_vs_ma60'] > 1:
        score += 25
    
    return min(100, score)
```

### 3) 서사 점수 (Narrative Score)
```python
def calculate_narrative_score(data):
    score = 0
    
    # 뉴스 빈도 (0~40점)
    score += min(40, data['news_count_7d'] * 2)
    
    # 정책 키워드 (0~30점)
    score += len(data['policy_keywords']) * 10
    
    # 공시 이벤트 (0~30점)
    if data.get('disclosure_type') in ['수주', '실적']:
        score += 30
    
    return min(100, score)
```

### 4) 리스크 점수 (Risk Score) ⚠️ 낮을수록 좋음
```python
def calculate_risk_score(data):
    score = 0
    
    # 과열/분배 봉 (0~40점)
    if data['gap_up_with_distribution']:
        score += 40
    
    # 테마 말기 (0~30점)
    if data['theme_rank'] >= 3:  # 3~5번째 급등주
        score += 30
    
    # 유동성 리스크 (0~30점)
    if data['avg_daily_volume'] < 1000000000:  # 10억 미만
        score += 30
    
    return min(100, score)
```

---

## 💰 월 9,900원 현실형 데이터 파이프라인

### 한국 시장 (무료 중심)
```python
DATA_SOURCES_KR = {
    # 1) 가격/거래량 (무료)
    "price": {
        "source": "KRX 정보데이터시스템",
        "url": "http://data.krx.co.kr",
        "cost": 0,
        "delay": "20분",
        "limit": "호출 제한 있음 (캐싱 필수)"
    },
    
    # 2) 투자자별 매매동향 (무료)
    "flow": {
        "source": "KRX 투자자별 매매동향",
        "url": "http://data.krx.co.kr/contents/MDC/MDI/mdiLoader",
        "cost": 0,
        "fields": ["외국인", "기관", "개인"],
        "limit": "일별 데이터만"
    },
    
    # 3) 공시/실적 (무료)
    "disclosure": {
        "source": "OpenDART API",
        "url": "https://opendart.fss.or.kr",
        "cost": 0,
        "api_key": "무료 발급",
        "limit": "일 10,000건"
    },
    
    # 4) 뉴스 (무료/제한적)
    "news": {
        "source": "네이버 금융 RSS",
        "url": "https://finance.naver.com/rss",
        "cost": 0,
        "limit": "크롤링 규칙 준수 필요"
    }
}
```

### 미국 시장 (EOD/지연 중심)
```python
DATA_SOURCES_US = {
    # 1) EOD 가격 (무료)
    "price": {
        "source": "Yahoo Finance API",
        "cost": 0,
        "delay": "15분~EOD",
        "limit": "2,000 calls/hour"
    },
    
    # 2) 펀더멘털 (무료)
    "fundamental": {
        "source": "Alpha Vantage (Free Tier)",
        "cost": 0,
        "limit": "5 API calls/minute",
        "note": "재무제표, PER, PBR 등"
    },
    
    # 3) 매크로 지표 (무료)
    "macro": {
        "source": "FRED API (Federal Reserve)",
        "url": "https://fred.stlouisfed.org/docs/api",
        "cost": 0,
        "fields": ["금리", "VIX", "실업률"]
    }
}
```

### 데이터 수집 전략
```python
# 1) 캐싱 전략 (비용 절감)
CACHE_POLICY = {
    "price": "5분",          # 5분마다 갱신
    "flow": "1시간",         # 1시간마다 갱신
    "disclosure": "30분",
    "news": "15분",
    "macro": "1일"           # 매크로는 하루 1회
}

# 2) 호출 우선순위
PRIORITY = [
    "1. KRX 투자자별 매매동향 (가장 중요)",
    "2. OpenDART 공시",
    "3. 가격/거래량",
    "4. 뉴스"
]

# 3) 에러 처리
ERROR_HANDLING = {
    "rate_limit": "캐시 데이터 반환",
    "api_down": "최근 1시간 캐시 사용",
    "timeout": "재시도 3회 → 실패 시 경고"
}
```

---

## 🚀 MVP 범위 (바로 개발 가능)

### Phase 1: 핵심 기능 (2주)
```
✅ Agent 1: Market Regime Analyst
✅ Agent 2: Sector Scout (상위 3개 섹터)
✅ Agent 3: Stock Screener (섹터당 10개 종목)
✅ Agent 5: Devil's Advocate
✅ 점수 엔진 (0~100 통일)
✅ Why Drawer (1클릭 근거 공개)
```

### Phase 2: 자동화 (1주)
```
✅ Agent 4: Trade Plan Builder
✅ No-Go 자동 판정 (6개 규칙)
✅ 데이터 수집 파이프라인 (KRX + OpenDART)
```

### Phase 3: UX 완성 (1주)
```
✅ 수동 입력 최소화 (2개 토글)
✅ 반응형 디자인
✅ 로딩 상태 표시
```

---

## 📈 V2 차별화 (업셀 요소)

### Premium Features (₩19,900/월)
```
🔔 조건 알림 (Leader 진입, 눌림 매수 타이밍)
📊 성과 기록 (과거 추천 종목 승률 추적)
🤖 개인화 체크리스트 (사용자 패턴 학습)
📈 실시간 미국 데이터 (15분 지연 → 실시간)
```

### Elite Features (₩29,900/월)
```
🎯 포트폴리오 자동 리밸런싱
🧠 AI 시뮬레이션 (내 계좌 기준 백테스트)
📡 증권사 API 연동 (자동 매매 준비)
```

---

## 🎯 핵심 성공 지표

```python
SUCCESS_METRICS = {
    # 1) 정확도
    "leader_accuracy": "> 60%",      # Leader 추천 승률
    "nogo_avoidance": "> 80%",       # No-Go 회피 성공률
    
    # 2) 사용성
    "decision_time": "< 3분",        # 종목 선택 → 매매 계획
    "manual_input": "2개 (기간/성향)",
    
    # 3) 신뢰도
    "source_transparency": "100%",   # 모든 점수에 출처
    "counter_presence": "100%",      # 모든 추천에 반대 의견
    
    # 4) 비용
    "data_cost": "< ₩5,000/월",     # 데이터 비용
    "server_cost": "< ₩3,000/월"    # 서버 비용
}
```

---

## 🔐 안전 장치

### 1) AI 검색 사용 규칙
```python
AI_SEARCH_POLICY = {
    "primary": "공식 API (KRX, OpenDART, FRED)",
    "secondary": "뉴스 크롤링 (출처 명시)",
    "forbidden": "커뮤니티, 루머, 비공식 소스",
    
    "audit_log": {
        "timestamp": True,
        "source": True,
        "confidence": True
    }
}
```

### 2) 법적 고지
```
⚠️ Decision Stream은 투자 판단 보조 도구입니다.
   - 매수·매도 권유를 하지 않습니다.
   - 수익을 보장하지 않습니다.
   - 모든 투자 결정은 사용자 책임입니다.
```

---

## 📝 다음 단계

1. **backend/agents/** 폴더 생성
2. 5개 Agent 코드 구현
3. 점수 엔진 통합
4. 데이터 파이프라인 구축
5. 프론트엔드 연동

**시작 명령:**
```bash
cd backend
mkdir agents
python -m agents.market_regime
python -m agents.sector_scout
```

---

**마지막 한마디:**

> **"선동 앱이 아니라 판단 도구"**  
> 모든 추천에는 근거와 반대 의견이 있다.  
> 모든 점수에는 출처가 있다.  
> 사용자는 "확정"만 한다.

이것이 Decision Stream의 차별화 포인트입니다. 🚀
