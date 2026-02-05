# 🤖 AI Agent Architecture
## Decision Stream 자동화 시스템 설계서

> **핵심 철학**: "선동 앱"이 아니라 **"판단 도구"**  
> 모든 판단에는 근거 + 반대 근거(Devil's Advocate)를 함께 제공

---

## 📊 전체 아키텍처

```
[Data Pipeline] → [5 AI Agents] → [Scoring Engine] → [UI]
       ↓              ↓               ↓              ↓
   KRX/DART    Market Regime    0~100 점수      설명 가능한
   EOD Data    Sector Scout     + 근거         자동 판단
```

---

## 🎯 5개 AI 에이전트 (Agent-Based Architecture)

### 1️⃣ Agent 1: Market Regime Analyst
**역할**: "오늘 장이 어떤 장인지" 자동 판단

**입력 데이터**:
- 코스피/S&P 500 지수 (20일/60일 이동평균 대비 위치)
- VKOSPI/VIX (변동성 지수)
- 원/달러 환율 (20일 변화율)
- 10년물 국채 수익률 (추세)
- 시장 너비 (상승/하락 종목 수 비율)

**판단 로직**:
```python
def analyze_market_regime():
    """
    Risk-On: 지수 상승 + 변동성 하락 + 시장 너비 확산
    Risk-Off: 지수 하락 + 변동성 상승 + 방어 섹터 강세
    """
    score = 0  # 0~3점
    
    # 1) 지수 위치 (20/60일선 대비)
    if kospi > ma20 and kospi > ma60:
        score += 1
    
    # 2) 변동성
    if vkospi < 20:  # 안정
        score += 1
    
    # 3) 시장 너비
    if breadth_ratio > 1.2:  # 상승 우위
        score += 1
    
    if score >= 2:
        return "RISK_ON", score
    else:
        return "RISK_OFF", score
```

**출력**:
- State: RISK_ON / RISK_OFF
- Score: 0~3 (신호 강도)
- Playbook: 공격적 진입 / 방어 대기 / 현금 확보

**근거 제공**:
- ✅ 지수가 20일선 위 (상승 추세)
- ✅ 변동성 18 (안정)
- ⚠️ 단, 외국인 3일 연속 순매도

---

### 2️⃣ Agent 2: Sector Scout
**역할**: 섹터별 자금 흐름/강도/뉴스를 합쳐 랭킹

**입력 데이터**:
- 섹터별 거래대금 (5일/20일 증가율)
- 기관/외국인 순매수 (섹터 단위)
- 섹터 ETF 흐름 (KODEX 방산, 헬스케어 등)
- 뉴스 키워드 빈도 (정책/수주/실적 관련)

**판단 로직**:
```python
def score_sector(sector):
    """
    섹터 점수 = 자금 흐름(40%) + 가격 구조(30%) + 서사(30%)
    """
    flow_score = calculate_flow_score(sector)      # 0~100
    structure_score = calculate_structure(sector)  # 0~100
    narrative_score = calculate_narrative(sector)  # 0~100
    
    total = (flow_score * 0.4 + 
             structure_score * 0.3 + 
             narrative_score * 0.3)
    
    # SURGE 판정
    if total >= 70 and flow_score >= 80:
        signal = "SURGE"  # 자금 급유입
    elif total >= 50:
        signal = "NORMAL"
    else:
        signal = "WEAK"
    
    return {
        "sector": sector,
        "total_score": total,
        "signal": signal,
        "flow_score": flow_score,
        "structure_score": structure_score,
        "narrative_score": narrative_score,
        "duration": estimate_theme_duration(sector)  # 1주/2주/3주
    }
```

**출력**:
- Top 5 섹터 (점수 순)
- SURGE 섹터 (자금 급유입)
- 각 섹터별 지속 가능성 (1주/2주/3주)

**근거 제공**:
- ✅ 방산: 거래대금 5일 +350% (flow_score: 97)
- ✅ 기관 3일 연속 순매수 +1,200억
- ✅ 정책 키워드 ("방위비", "수출") 20건
- ⚠️ 단, 이미 2주차 상승 (말기 위험)

---

### 3️⃣ Agent 3: Stock Screener
**역할**: 섹터 내 종목을 Leader/Follower/No-Go로 자동 분류

**입력 데이터**:
- 종목별 가격/거래대금 (5일/20일)
- 기관/외국인/개인 매매 비중
- 차트 구조 (20일선/60일선, 고점/저점)
- 공시 이벤트 (수주/실적 가이던스)
- 뉴스 빈도 (단일 기사 vs 연쇄 보도)

**판단 로직**:
```python
def classify_stock(stock, sector):
    """
    Leader: 섹터 선도 + 구조 완성 + 기관 동참
    Follower: 구조 형성 중 + 눌림 매수 구간
    No-Go: 과열/가짜 모멘텀/구조 파손
    """
    # 1) No-Go 우선 체크 (12개 규칙 중 핵심 6개)
    if check_nogo_rules(stock):
        return "NO_GO", get_nogo_reason(stock)
    
    # 2) 9요소 점수 계산
    scores = calculate_9_factors(stock, sector)
    
    # 3) 모멘텀 품질 판별 (진짜 vs 가짜)
    momentum_quality = check_momentum_quality(stock, sector)
    
    if momentum_quality == "FAKE":
        return "NO_GO", "가짜 모멘텀 (단일 기사/혼자 급등)"
    
    # 4) Leader vs Follower
    if scores['momentum'] >= 70 and scores['flow'] >= 70:
        return "LEADER", scores
    elif scores['flow'] >= 60 and scores['structure'] >= 60:
        return "FOLLOWER", scores
    else:
        return "NO_GO", "필수 요소 미달"
```

**No-Go 판정 규칙 (12개 중 핵심 6개)**:
```python
def check_nogo_rules(stock):
    """
    하나라도 해당 시 No-Go 자동 이동
    """
    rules = {
        "단일 기사 급등": (
            stock.news_count == 1 and 
            stock.volume_surge > 5  # 5배 폭증
        ),
        "갭 상승 후 장대 음봉": (
            stock.gap_up > 5 and 
            stock.last_candle == "DISTRIBUTION"
        ),
        "테마 내 5번째 이후 급등주": (
            stock.sector_rank >= 5
        ),
        "개인 80%↑ + 기관 이탈": (
            stock.retail_ratio > 80 and 
            stock.inst_net_buying < 0
        ),
        "핵심 이평 동시 이탈": (
            stock.price < stock.ma20 and 
            stock.price < stock.ma60
        ),
        "손절선 설정 불가": (
            stock.support_level is None or
            stock.atr_ratio > 0.15  # 변동성 너무 큼
        )
    }
    
    for rule_name, condition in rules.items():
        if condition:
            return True, rule_name
    
    return False, None
```

**출력**:
- Leader: 2~3종목 (섹터 대표주)
- Follower: 5~10종목 (눌림 매수 대기)
- No-Go: 회피 종목 + 이유

**근거 제공** (Leader 예시):
- ✅ 한화에어로스페이스 (방산)
  - 자금 흐름: 95점 (기관 5일 +800억)
  - 가격 구조: 88점 (20/60일선 위, 고점/저점 상승)
  - 모멘텀: 진짜 (정책 + 수주 + 섹터 동반 상승)
- ⚠️ 반대 근거: 이미 20% 상승, 단기 과열 가능성

---

### 4️⃣ Agent 4: Trade Plan Builder
**역할**: 사용자의 기간/성향에 맞춰 진입·손절·익절·분할 자동 설계

**입력**:
- 투자기간: 단기(수일~2주) / 중기(1~3개월)
- 리스크 성향: 보수 / 중립 / 공격
- (선택) 계좌 규모

**판단 로직**:
```python
def build_trade_plan(stock, period, risk_profile):
    """
    핵심: 손절 먼저 고정 → 진입 → 목표 순서
    """
    # 1) 손절선 (구조 기반)
    support = find_support_level(stock)  # 20일선 or 최근 저점
    stop_loss = support * 0.97  # 지지선 -3%
    
    # 2) 진입 2안
    entry_breakout = stock.recent_high * 1.01  # 돌파 진입
    entry_pullback = stock.ma20  # 눌림 매수
    
    # 3) 목표 2안 (리스크 성향별)
    risk_reward = {
        "보수": 2.0,   # 손실:수익 = 1:2
        "중립": 2.5,
        "공격": 3.0
    }
    
    risk_amount = stock.price - stop_loss
    target_conservative = stock.price + (risk_amount * risk_reward[risk_profile])
    target_aggressive = stock.price + (risk_amount * risk_reward[risk_profile] * 1.5)
    
    # 4) 포지션 사이즈 (변동성 기반)
    if account_size:
        max_loss = account_size * 0.02  # 계좌의 2%
        position_size = max_loss / risk_amount
    else:
        position_size = 0.2  # 기본 20%
    
    # 5) 분할 매도
    exit_plan = [
        (target_conservative, 0.5, "1차 목표 50% 매도"),
        (target_aggressive, 0.3, "2차 목표 30% 매도"),
        ("trailing", 0.2, "나머지 20% 추세 추종")
    ]
    
    return {
        "entry_breakout": entry_breakout,
        "entry_pullback": entry_pullback,
        "stop_loss": stop_loss,
        "target_conservative": target_conservative,
        "target_aggressive": target_aggressive,
        "position_size": position_size,
        "exit_plan": exit_plan,
        "max_holding_days": 10 if period == "단기" else 60
    }
```

**출력 (카드 형식)**:
```
📌 매매 계획 (중기 / 중립 성향)

진입 2안:
  ✓ 돌파 진입: 190,000원 (최근 고점 돌파 시)
  ✓ 눌림 매수: 180,000원 (20일선 지지 시)

손절:
  ✗ 175,000원 (구조 이탈 시 무조건 손절)

목표 2안:
  ✓ 1차 목표: 205,000원 (50% 매도)
  ✓ 2차 목표: 220,000원 (30% 매도)
  ✓ 나머지 20%: 추세 추종

포지션 사이즈: 20% (변동성 고려)
최대 보유 기간: 60일
```

---

### 5️⃣ Agent 5: Devil's Advocate
**역할**: "왜 이 판단이 틀릴 수 있는지" 2~3개 자동 제시

**판단 로직**:
```python
def generate_counter_arguments(stock, sector, regime):
    """
    모든 긍정 판단에 대한 반대 근거 자동 생성
    """
    counter = []
    
    # 1) 시장 환경 리스크
    if regime.state == "RISK_ON" and regime.score <= 2:
        counter.append(
            "⚠️ Risk-On이지만 신호 약함 (2점). "
            "급격한 Risk-Off 전환 시 전체 하락 가능."
        )
    
    # 2) 섹터 말기 리스크
    if sector.duration >= 2:  # 2주 이상
        counter.append(
            f"⚠️ {sector.name} 테마 이미 {sector.duration}주차. "
            "조정 또는 자금 이동 가능성 주의."
        )
    
    # 3) 종목 과열 리스크
    if stock.volume_5d_ratio > 3:  # 5일 평균 대비 3배
        counter.append(
            "⚠️ 거래대금 급증 (5일 평균 대비 3배). "
            "단기 과열 후 조정 가능성."
        )
    
    # 4) 기관 이탈 리스크
    if stock.inst_net_buying_3d < 0:
        counter.append(
            "⚠️ 기관 3일 연속 순매도. "
            "개인 주도 상승은 지속성 약함."
        )
    
    # 5) 손절 여유 부족
    risk_reward = (stock.target - stock.price) / (stock.price - stock.stop_loss)
    if risk_reward < 2:
        counter.append(
            f"⚠️ 리스크 대비 수익 {risk_reward:.1f}배 (2배 미만). "
            "진입 타이밍 재검토 필요."
        )
    
    return counter[:3]  # 최대 3개
```

**출력 예시**:
```
⚠️ 반대 근거 (Devil's Advocate)

1. 방산 테마 이미 2주차. 조정 또는 자금 이동 가능성.
2. 거래대금 급증 (5일 평균 대비 4배). 단기 과열 우려.
3. 외국인 3일 연속 순매도. 지속 상승 여력 제한.
```

---

## 💾 데이터 파이프라인 (월 9,900원 현실형)

### 한국 시장 (공식/무료 우선)

| 데이터 | 출처 | 비용 | 업데이트 주기 |
|--------|------|------|--------------|
| **시세** | KIS API (무료) | 무료 | 실시간 |
| **수급** | KRX 투자자별 매매동향 | 무료 | 일 1회 |
| **공시** | OpenDART API | 무료 | 실시간 |
| **실적** | OpenDART (사업보고서) | 무료 | 분기 |
| **뉴스** | Naver 금융 (크롤링) | 무료 | 실시간 |

**장점**: 한국은 "수급+공시"가 강해서 섹터/종목 판단에 매우 유리

**구현**:
```python
# backend/services/korea_data_pipeline.py
class KoreaDataPipeline:
    """
    한국 시장 데이터 자동 수집 (무료/공식)
    """
    def __init__(self):
        self.kis_api = KoreaInvestmentAPI()
        self.dart_api = OpenDARTAPI()
    
    async def collect_daily_data(self):
        """
        매일 장 마감 후 자동 수집
        """
        # 1) 시세 (KIS API)
        prices = await self.kis_api.get_market_prices()
        
        # 2) 수급 (KRX 웹)
        supply_demand = await self.scrape_krx_supply_demand()
        
        # 3) 공시 (OpenDART)
        disclosures = await self.dart_api.get_today_disclosures()
        
        # 4) 섹터 분류 (GICS)
        sectors = self.classify_sectors(prices)
        
        return {
            "prices": prices,
            "supply_demand": supply_demand,
            "disclosures": disclosures,
            "sectors": sectors
        }
    
    async def scrape_krx_supply_demand(self):
        """
        KRX 투자자별 매매동향 수집
        """
        url = "http://data.krx.co.kr/comm/bldAttendant/..."
        # 웹 스크래핑 로직
        return data
```

---

### 미국 시장 (EOD/지연 기반)

| 데이터 | 출처 | 비용 | 업데이트 주기 |
|--------|------|------|--------------|
| **EOD 시세** | Alpha Vantage (무료) | 무료 | 일 1회 |
| **지연 시세** | yfinance | 무료 | 15분 지연 |
| **섹터 ETF** | yfinance (SPY, QQQ 등) | 무료 | 15분 지연 |
| **실적/뉴스** | Alpha Vantage | 무료 (제한) | 일 1회 |

**제약**: 실시간 불가, 초단타 불가  
**전략**: 중기 스윙 의사결정 중심 (손절/구조 기반)

**구현**:
```python
# backend/services/us_data_pipeline.py
class USDataPipeline:
    """
    미국 시장 데이터 자동 수집 (무료/지연)
    """
    def __init__(self):
        self.alpha_vantage_key = os.getenv("ALPHA_VANTAGE_KEY")
    
    async def collect_eod_data(self):
        """
        EOD (종가) 데이터 수집
        """
        # 1) 주요 지수 (S&P 500, Nasdaq)
        indices = await self.get_indices()
        
        # 2) 섹터 ETF (XLK, XLV, XLE 등)
        sectors = await self.get_sector_etfs()
        
        # 3) 개별 종목 (관심 종목)
        stocks = await self.get_watchlist_stocks()
        
        return {
            "indices": indices,
            "sectors": sectors,
            "stocks": stocks
        }
```

---

## 🎯 점수 엔진 (0~100, 설명 가능)

### 핵심 원칙
1. **모든 점수는 0~100으로 통일**
2. **1클릭으로 근거 + 반대 근거 공개**
3. **사람이 이해할 수 있는 언어**

### (1) 자금 유입 점수 (Flow Score)

```python
def calculate_flow_score(stock):
    """
    자금 흐름 = 거래대금 증가 + 기관/외국인 순매수
    """
    score = 0
    reasons = []
    
    # 1) 거래대금 (40점)
    volume_5d_ratio = stock.volume_5d / stock.volume_avg_20d
    if volume_5d_ratio >= 3:
        score += 40
        reasons.append(f"거래대금 5일 평균 {volume_5d_ratio:.1f}배 급증")
    elif volume_5d_ratio >= 2:
        score += 30
        reasons.append(f"거래대금 증가 ({volume_5d_ratio:.1f}배)")
    elif volume_5d_ratio >= 1.5:
        score += 20
        reasons.append(f"거래대금 소폭 증가 ({volume_5d_ratio:.1f}배)")
    
    # 2) 기관 순매수 (30점)
    if stock.inst_net_buying_5d > 0:
        inst_ratio = stock.inst_net_buying_5d / stock.avg_volume
        if inst_ratio > 0.1:  # 평균 거래량의 10%
            score += 30
            reasons.append(f"기관 5일 대량 순매수 ({inst_ratio*100:.1f}%)")
        else:
            score += 20
            reasons.append("기관 순매수 전환")
    
    # 3) 외국인 순매수 (30점)
    if stock.foreign_net_buying_5d > 0:
        score += 30
        reasons.append("외국인 순매수 동참")
    
    return score, reasons
```

**출력 예시**:
```
자금 흐름: 95/100

근거:
✅ 거래대금 5일 평균 4.2배 급증
✅ 기관 5일 대량 순매수 (12.5%)
✅ 외국인 순매수 동참

반대 근거:
⚠️ 개인 매수 비중 65% (과열 우려)
```

---

### (2) 가격 구조 점수 (Structure Score)

```python
def calculate_structure_score(stock):
    """
    가격 구조 = 추세 + 고저점 + 조정 패턴
    """
    score = 0
    reasons = []
    
    # 1) 이동평균 (40점)
    if stock.price > stock.ma20 and stock.price > stock.ma60:
        score += 40
        reasons.append("20일선, 60일선 위 (상승 추세)")
    elif stock.price > stock.ma20:
        score += 20
        reasons.append("20일선 위 (단기 상승)")
    
    # 2) 고점/저점 (30점)
    recent_high = max(stock.prices[-20:])
    recent_low = min(stock.prices[-20:])
    if stock.price >= recent_high * 0.95:
        score += 30
        reasons.append("최근 20일 고점 근처")
    
    # 3) 조정 시 거래량 (30점)
    if stock.pullback_volume_ratio < 0.7:  # 조정 시 거래량 감소
        score += 30
        reasons.append("조정 시 거래량 감소 (건전)")
    
    return score, reasons
```

---

### (3) 서사 점수 (Narrative Score)

```python
def calculate_narrative_score(stock, sector):
    """
    서사 = 뉴스 빈도 + 정책 연관 + 실적 이벤트
    """
    score = 0
    reasons = []
    
    # 1) 뉴스 빈도 (40점)
    news_count = count_news_last_7d(stock)
    if news_count >= 10:
        score += 40
        reasons.append(f"최근 7일 뉴스 {news_count}건 (고빈도)")
    elif news_count >= 5:
        score += 20
        reasons.append(f"뉴스 {news_count}건")
    
    # 2) 정책/제도 키워드 (30점)
    policy_keywords = ["수주", "정책", "규제", "지원"]
    if any(kw in stock.news_text for kw in policy_keywords):
        score += 30
        reasons.append("정책/제도 관련 재료")
    
    # 3) 실적 이벤트 (30점)
    if stock.has_guidance or stock.has_disclosure:
        score += 30
        reasons.append("실적 가이던스 또는 공시")
    
    return score, reasons
```

---

### (4) 리스크 점수 (Risk Score)

```python
def calculate_risk_score(stock):
    """
    리스크 = 과열 + 테마 말기 + 유동성
    (점수가 낮을수록 좋음)
    """
    score = 0
    warnings = []
    
    # 1) 과열 (40점)
    if stock.rsi > 70:
        score += 20
        warnings.append(f"RSI {stock.rsi} (과열)")
    
    if stock.last_candle == "DISTRIBUTION":  # 분배 봉
        score += 20
        warnings.append("장대 음봉 (분배 신호)")
    
    # 2) 테마 말기 (30점)
    if stock.sector_rank >= 5:
        score += 30
        warnings.append(f"테마 내 {stock.sector_rank}번째 급등주 (늦음)")
    
    # 3) 유동성 (30점)
    if stock.avg_volume_daily < 1_000_000_000:  # 10억 미만
        score += 30
        warnings.append(f"일평균 거래대금 {stock.avg_volume_daily/1e8:.0f}억 (유동성 부족)")
    
    return score, warnings
```

---

## 🎨 UI 구현 (설명 가능성)

### Why Drawer (근거 토글)

```html
<!-- 점수 클릭 시 드로어 오픈 -->
<div class="score-card" onclick="openWhyDrawer('flow', 95)">
  자금 흐름: <span class="score">95</span>/100
</div>

<!-- Why Drawer -->
<div id="why-drawer" class="drawer">
  <h3>🔍 자금 흐름 95점 근거</h3>
  
  <div class="evidence">
    <h4>✅ 근거 (3개)</h4>
    <ul>
      <li>거래대금 5일 평균 4.2배 급증</li>
      <li>기관 5일 대량 순매수 (12.5%)</li>
      <li>외국인 순매수 동참</li>
    </ul>
  </div>
  
  <div class="counter-evidence">
    <h4>⚠️ 반대 근거 (2개) - Devil's Advocate</h4>
    <ul>
      <li>개인 매수 비중 65% (기관 이탈 시 급락 위험)</li>
      <li>거래대금 급증은 지속성 낮을 수 있음</li>
    </ul>
  </div>
  
  <div class="sources">
    <h4>📊 데이터 출처</h4>
    <ul>
      <li><a href="http://data.krx.co.kr/...">KRX 투자자별 매매동향</a></li>
      <li><a href="...">네이버 금융 시세</a></li>
    </ul>
  </div>
  
  <div class="confidence">
    <h4>🎯 신뢰도</h4>
    <div class="confidence-bar">
      <div class="confidence-fill" style="width: 85%">85%</div>
    </div>
    <div class="small">공식 데이터 + 검증된 로직</div>
  </div>
</div>
```

---

## 📦 MVP 구현 우선순위

### Phase 1: 핵심 기능 (2주)
- [x] Market Regime Analyst (Agent 1)
- [x] Sector Scout (Agent 2)
- [ ] Stock Screener with No-Go (Agent 3)
- [ ] 점수 엔진 (Flow, Structure, Narrative, Risk)
- [ ] Why Drawer (근거 토글) UI

### Phase 2: 자동화 강화 (2주)
- [ ] Trade Plan Builder (Agent 4)
- [ ] Devil's Advocate (Agent 5)
- [ ] 한국 데이터 파이프라인 (KRX + OpenDART)
- [ ] 미국 데이터 파이프라인 (EOD)

### Phase 3: 차별화 (1주)
- [ ] 알림 시스템 (조건 충족 시)
- [ ] 성과 기록 (백테스팅)
- [ ] 개인화 (맞춤 체크리스트)

---

## 💰 비용 구조 (월 9,900원 모델)

| 항목 | 비용 | 비고 |
|------|------|------|
| 한국 데이터 | 무료 | KRX + OpenDART |
| 미국 EOD | 무료 | Alpha Vantage |
| AI 요약 | ~5,000원 | GPT-4 API (월 500건) |
| 서버 | ~5,000원 | Railway Basic |
| **합계** | **~10,000원** | 적자 없음 |

**업셀 구조**:
- 19,900원: 실시간 미국 시세 (15분 → 실시간)
- 29,900원: 프리미엄 데이터 + 백테스팅 + 알림

---

## 🎯 핵심 메시지

> **"선동 앱"이 아니라 "판단 도구"**

1. **모든 판단에 근거 + 반대 근거**
2. **설명 가능한 자동화**
3. **사용자 보호 우선 (No-Go 명시)**
4. **데이터 출처 투명 공개**
5. **월 9,900원으로 가능한 현실적 설계**

---

## 다음 단계

1. ✅ **이 문서 검토 및 피드백**
2. ⏳ **Agent 3 (Stock Screener) 구현**
3. ⏳ **점수 엔진 (0~100) 구현**
4. ⏳ **Why Drawer UI 구현**
5. ⏳ **한국 데이터 파이프라인 구축**

---

**작성일**: 2026-01-27  
**버전**: v1.0  
**담당**: Decision Stream Team
