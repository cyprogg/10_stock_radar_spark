# MVP 로드맵 - Decision Stream

## 🎯 목표

**"월 9,900원으로 운영 가능한 AI 기반 투자 의사결정 시스템"**

- 무료 데이터 중심 (KRX + OpenDART + Yahoo Finance)
- 설명 가능한 자동화 (모든 판단에 근거)
- 수동 입력 최소화 (2개 토글)
- 단기/중기 스윙 투자 최적화

---

## 📅 4주 개발 계획

### Week 1: 핵심 엔진 구축 ⚙️

#### Day 1-2: 데이터 파이프라인
```bash
# 생성 파일
backend/data/
├── krx_collector.py          # KRX 투자자별 매매동향
├── dart_collector.py         # OpenDART 공시
├── yahoo_collector.py        # Yahoo Finance 가격
└── cache_manager.py          # 캐싱 시스템
```

**기능:**
- KRX 투자자별 매매동향 수집 (외국인/기관/개인)
- OpenDART 공시 수집 (수주/실적/공시)
- Yahoo Finance EOD 가격
- Redis 캐싱 (호출 제한 대응)

**테스트:**
```python
# test_data_pipeline.py
def test_krx_collector():
    data = collect_krx_flow("005930", days=20)
    assert 'foreign_net_buy' in data
    assert data['timestamp'] is not None
```

---

#### Day 3-4: 점수 엔진
```bash
backend/scoring/
├── flow_score.py             # 자금 흐름 점수 (0~100)
├── structure_score.py        # 가격 구조 점수
├── narrative_score.py        # 서사 점수
├── risk_score.py             # 리스크 점수
└── momentum_quality.py       # 모멘텀 품질 (진짜 vs 가짜)
```

**기능:**
- 모든 점수 0~100 통일
- 점수 계산 로직 + 근거 반환
- 모멘텀 품질 판별 (섹터 동반 상승/기관 참여 체크)

**테스트:**
```python
def test_flow_score():
    data = {
        'volume_change_20d': 2.5,
        'foreign_net_buy_5d': 150,
        'inst_net_buy_5d': 200
    }
    result = calculate_flow_score(data)
    assert result['score'] >= 80
    assert len(result['why']) >= 2
```

---

#### Day 5-7: AI Agent 구현
```bash
backend/agents/
├── market_regime.py          # Agent 1
├── sector_scout.py           # Agent 2
├── stock_screener.py         # Agent 3
├── trade_plan_builder.py    # Agent 4
└── devils_advocate.py        # Agent 5
```

**Agent 1: Market Regime Analyst**
```python
# market_regime.py
def analyze_regime(data):
    score = calculate_regime_score(data)
    playbook = generate_playbook(score)
    
    return {
        "state": "RISK_ON" if score >= 2 else "RISK_OFF",
        "score": score,
        "playbook": playbook,
        "signals": {"positive": [...], "negative": [...]},
        "confidence": 85
    }
```

**Agent 2: Sector Scout**
```python
# sector_scout.py
def scout_sectors(market_data):
    sectors = []
    for sector in ALL_SECTORS:
        flow = calculate_flow_score(sector)
        structure = calculate_structure_score(sector)
        narrative = calculate_narrative_score(sector)
        
        sectors.append({
            "name": sector['name'],
            "flow_score": flow,
            "signal": "SURGE" if flow >= 80 else "NORMAL",
            "breakdown": {flow, structure, narrative}
        })
    
    return sorted(sectors, key=lambda x: x['flow_score'], reverse=True)
```

**Agent 3: Stock Screener**
```python
# stock_screener.py
def screen_stocks(sector, stocks):
    leader = []
    follower = []
    nogo = []
    
    for stock in stocks:
        # No-Go 체크 (핵심 6개 규칙)
        if check_nogo_rules(stock):
            nogo.append(stock)
            continue
        
        # 9요소 체크
        if not check_mandatory_factors(stock):
            nogo.append(stock)
            continue
        
        # 모멘텀 품질로 Leader/Follower 분류
        momentum = calculate_momentum_quality(stock)
        if momentum >= 85:
            leader.append(stock)
        else:
            follower.append(stock)
    
    return {"leader": leader, "follower": follower, "nogo": nogo}
```

**Agent 4: Trade Plan Builder**
```python
# trade_plan_builder.py
def build_plan(stock, user_input):
    # 1) 손절 먼저 고정
    stop_loss = calculate_stop_loss(stock)
    
    # 2) 진입가 설정
    entry = calculate_entry_prices(stock)
    
    # 3) 목표가 설정 (손절 대비 2배 이상)
    targets = calculate_targets(stock, stop_loss, user_input['risk_profile'])
    
    # 4) 포지션 사이즈
    position = calculate_position_size(stock, user_input.get('account_size'))
    
    return {
        "entry": entry,
        "stop_loss": stop_loss,
        "targets": targets,
        "position_size": position,
        "split_plan": [...]
    }
```

**Agent 5: Devil's Advocate**
```python
# devils_advocate.py
def generate_counter(recommendation):
    counters = []
    
    # 밸류에이션 체크
    if recommendation['scores']['8_value'] < 50:
        counters.append({
            "category": "밸류에이션",
            "point": "PER/PBR 고평가",
            "severity": "medium"
        })
    
    # 리스크 체크
    if recommendation['scores']['6_risk'] > 20:
        counters.append({
            "category": "리스크",
            "point": "변동성 주의",
            "severity": "high"
        })
    
    return {"counter_arguments": counters[:3]}
```

---

### Week 2: No-Go 시스템 + API 연동 🚫

#### Day 8-10: No-Go 판정 엔진
```bash
backend/nogo/
├── nogo_rules.py             # 핵심 6개 규칙
├── momentum_validator.py     # 모멘텀 진위 판별
└── theme_tracker.py          # 테마 피로도 추적
```

**핵심 6개 No-Go 규칙:**
```python
# nogo_rules.py
NOGO_RULES = {
    "rule_1": {
        "name": "단일 기사 급등 + 거래대금 폭증",
        "check": lambda s: s['news_type'] == 'single' and s['flow_score'] > 90
    },
    "rule_2": {
        "name": "갭 상승 후 장대 음봉",
        "check": lambda s: s['gap_up_with_distribution']
    },
    "rule_3": {
        "name": "테마 내 5번째 이후 급등주",
        "check": lambda s: s['theme_rank'] >= 5
    },
    "rule_4": {
        "name": "개인 순매수 80%↑ + 기관 이탈",
        "check": lambda s: s['retail_ratio'] > 0.8 and not s['inst_buy']
    },
    "rule_5": {
        "name": "핵심 이평(20/60) 동시 이탈",
        "check": lambda s: s['below_ma20'] and s['below_ma60']
    },
    "rule_6": {
        "name": "손절선 설정 불가",
        "check": lambda s: s['risk_score'] > 50
    }
}

def check_nogo(stock):
    flags = []
    for rule_id, rule in NOGO_RULES.items():
        if rule['check'](stock):
            flags.append(rule['name'])
    
    return {
        "is_nogo": len(flags) > 0,
        "reasons": flags
    }
```

**모멘텀 진위 판별:**
```python
# momentum_validator.py
def validate_momentum(stock, sector_data):
    """진짜 vs 가짜 모멘텀 판별"""
    
    # 진짜 모멘텀 조건
    real_signals = []
    
    # 1) 섹터 동반 상승
    if len(sector_data['rising_stocks']) >= 3:
        real_signals.append("섹터 동반 상승")
    
    # 2) 기관/외국인 동참
    if stock['inst_net_buy'] > 0 and stock['foreign_net_buy'] > 0:
        real_signals.append("기관/외국인 동참")
    
    # 3) 펀더멘털 뉴스
    if stock['news_type'] in ['fundamental', 'policy']:
        real_signals.append("펀더멘털 뉴스")
    
    # 가짜 모멘텀 체크
    fake_signals = []
    
    if stock['news_type'] == 'rumor':
        fake_signals.append("루머성 재료")
    
    if stock['retail_ratio'] > 0.8:
        fake_signals.append("개인 독주")
    
    is_real = len(real_signals) >= 2 and len(fake_signals) == 0
    
    return {
        "is_real": is_real,
        "real_signals": real_signals,
        "fake_signals": fake_signals,
        "quality_score": len(real_signals) * 30 - len(fake_signals) * 40
    }
```

---

#### Day 11-14: API 서버 구축
```bash
backend/api/
├── routes/
│   ├── regime.py             # GET /regime
│   ├── sectors.py            # GET /sectors
│   ├── funnel.py             # GET /funnel?sector=방산
│   ├── checklist.py          # GET /checklist?ticker=005930
│   └── plan.py               # POST /plan
└── server.py                 # FastAPI 메인
```

**API 엔드포인트:**
```python
# server.py
from fastapi import FastAPI
from api.routes import regime, sectors, funnel, checklist, plan

app = FastAPI(title="Decision Stream API")

app.include_router(regime.router, prefix="/regime")
app.include_router(sectors.router, prefix="/sectors")
app.include_router(funnel.router, prefix="/funnel")
app.include_router(checklist.router, prefix="/checklist")
app.include_router(plan.router, prefix="/plan")

# /regime
@app.get("/regime")
async def get_regime():
    data = collect_market_data()
    result = analyze_regime(data)
    return result

# /sectors
@app.get("/sectors")
async def get_sectors():
    data = collect_sector_data()
    sectors = scout_sectors(data)
    return sectors[:10]  # Top 10

# /funnel?sector=방산
@app.get("/funnel")
async def get_funnel(sector: str):
    stocks = collect_sector_stocks(sector)
    result = screen_stocks(sector, stocks)
    return result

# /checklist?ticker=005930
@app.get("/checklist")
async def get_checklist(ticker: str):
    stock = get_stock_data(ticker)
    
    # 9요소 체크
    checks = check_all_factors(stock)
    
    # Devil's Advocate
    counter = generate_counter({"scores": checks})
    
    return {
        "checks": checks,
        "counter": counter,
        "confidence": 85
    }

# POST /plan
@app.post("/plan")
async def create_plan(request: dict):
    stock = get_stock_data(request['ticker'])
    plan = build_plan(stock, request['user_input'])
    return plan
```

---

### Week 3: 프론트엔드 통합 🎨

#### Day 15-17: Why Drawer (근거 토글)
```javascript
// index.html에 추가
function renderWhyDrawer(score, data) {
  return `
    <div class="score-badge" onclick="toggleWhyDrawer('${data.id}')">
      ${score}
      <span class="info-icon">ℹ️</span>
    </div>
    
    <div id="drawer-${data.id}" class="why-drawer hidden">
      <div class="drawer-section">
        <h4>📊 데이터 출처</h4>
        ${data.sources.map(s => `
          <a href="${s.url}" target="_blank">${s.name}</a>
        `).join('')}
      </div>
      
      <div class="drawer-section">
        <h4>✅ 근거 (3개)</h4>
        <ul>
          ${data.why.map(w => `<li>${w}</li>`).join('')}
        </ul>
      </div>
      
      <div class="drawer-section">
        <h4>⚠️ 반대 근거 (2개)</h4>
        <ul>
          ${data.counter.map(c => `<li>${c.point}</li>`).join('')}
        </ul>
      </div>
      
      <div class="drawer-section">
        <h4>🎯 신뢰도</h4>
        <div class="confidence-bar">
          <div style="width: ${data.confidence}%">${data.confidence}%</div>
        </div>
      </div>
    </div>
  `;
}

function toggleWhyDrawer(id) {
  const drawer = document.getElementById(`drawer-${id}`);
  drawer.classList.toggle('hidden');
}
```

**CSS:**
```css
.why-drawer {
  margin-top: 12px;
  padding: 16px;
  background: rgba(255,255,255,0.05);
  border-left: 3px solid var(--accent);
  border-radius: 8px;
  animation: slideDown 0.3s ease;
}

.why-drawer.hidden {
  display: none;
}

@keyframes slideDown {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

.drawer-section {
  margin-bottom: 16px;
}

.drawer-section h4 {
  font-size: 13px;
  color: var(--accent);
  margin-bottom: 8px;
}

.confidence-bar {
  height: 24px;
  background: rgba(255,255,255,0.1);
  border-radius: 4px;
  overflow: hidden;
}

.confidence-bar div {
  height: 100%;
  background: linear-gradient(90deg, #4ade80, #22c55e);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
}
```

---

#### Day 18-19: No-Go 라벨 UI
```javascript
function renderNoGoLabel(stock) {
  const icons = {
    "과열": "🔥",
    "단일 기사": "📰",
    "테마 말기": "📈",
    "유동성 부족": "💧",
    "개인 독주": "🏃",
    "구조 파손": "⚠️"
  };
  
  const labels = stock.nogo_reasons.map(reason => {
    const [category] = reason.split(':');
    const icon = icons[category] || "❌";
    
    return `
      <span class="nogo-label" title="${reason}">
        ${icon} ${category}
      </span>
    `;
  }).join('');
  
  return `
    <div class="stock-item nogo">
      <div class="stock-header">
        <div>${stock.name}</div>
        <div class="nogo-labels">${labels}</div>
      </div>
      <div class="small muted">
        ${stock.nogo_reasons.join(' | ')}
      </div>
    </div>
  `;
}
```

**CSS:**
```css
.nogo-label {
  display: inline-block;
  padding: 4px 8px;
  background: rgba(239, 68, 68, 0.2);
  border: 1px solid #ef4444;
  border-radius: 4px;
  font-size: 11px;
  margin-right: 4px;
  cursor: help;
}

.stock-item.nogo {
  border-left: 3px solid #ef4444;
  opacity: 0.7;
}
```

---

#### Day 20-21: Trade Plan Builder UI
```javascript
async function renderTradePlan(ticker) {
  const plan = await fetch(`${API}/plan`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      ticker: ticker,
      user_input: {
        period: getUserPeriod(),      // 단기/중기
        risk_profile: getUserRisk(),  // 보수/중립/공격
        account_size: getUserAccount() || null
      }
    })
  }).then(r => r.json());
  
  return `
    <div class="trade-plan-card">
      <h4>📋 매매 계획 - ${ticker}</h4>
      
      <div class="plan-section">
        <div class="plan-label">진입가 (2안)</div>
        <div class="plan-values">
          <div class="plan-option">
            <span class="badge breakout">돌파 진입</span>
            ${formatPrice(plan.entry.breakout)}
          </div>
          <div class="plan-option">
            <span class="badge pullback">눌림 진입</span>
            ${formatPrice(plan.entry.pullback)}
          </div>
        </div>
      </div>
      
      <div class="plan-section highlight">
        <div class="plan-label">손절가 (1안) ⚠️</div>
        <div class="plan-values">
          <div class="stop-loss">
            ${formatPrice(plan.stop_loss)}
            <span class="small muted">
              (-${((1 - plan.stop_loss / plan.entry.pullback) * 100).toFixed(1)}%)
            </span>
          </div>
        </div>
      </div>
      
      <div class="plan-section">
        <div class="plan-label">목표가 (2안)</div>
        <div class="plan-values">
          <div class="plan-option">
            <span class="badge conservative">보수</span>
            ${formatPrice(plan.targets.conservative)}
          </div>
          <div class="plan-option">
            <span class="badge aggressive">공격</span>
            ${formatPrice(plan.targets.aggressive)}
          </div>
        </div>
      </div>
      
      <div class="plan-section">
        <div class="plan-label">포지션 사이즈</div>
        <div class="plan-values">
          <div>${plan.position_size.percent}%</div>
          <div class="small muted">
            ${plan.position_size.shares}주 
            (${formatPrice(plan.position_size.amount)})
          </div>
        </div>
      </div>
      
      <div class="plan-section">
        <div class="plan-label">분할 계획</div>
        <div class="split-plan">
          ${plan.split_plan.map((s, i) => `
            <div class="split-step">
              <span class="step-num">${i+1}</span>
              <span class="step-action">${s.action}</span>
              <span class="step-percent">${s.percent}%</span>
              <span class="step-price">${formatPrice(s.price)}</span>
            </div>
          `).join('')}
        </div>
      </div>
      
      <div class="plan-why">
        <div class="small">📝 계획 근거</div>
        <ul>
          ${plan.why.map(w => `<li>${w}</li>`).join('')}
        </ul>
      </div>
    </div>
  `;
}
```

---

### Week 4: 테스트 + 문서화 + 배포 🚀

#### Day 22-24: 통합 테스트
```bash
tests/
├── test_data_pipeline.py
├── test_scoring_engine.py
├── test_agents.py
├── test_nogo_rules.py
└── test_api.py
```

**테스트 시나리오:**
```python
# test_end_to_end.py
def test_full_workflow():
    """전체 워크플로우 테스트"""
    
    # 1) Market Regime
    regime = analyze_regime(get_market_data())
    assert regime['state'] in ['RISK_ON', 'RISK_OFF']
    
    # 2) Sector Scout
    sectors = scout_sectors(get_sector_data())
    assert len(sectors) >= 5
    assert sectors[0]['flow_score'] >= 70
    
    # 3) Stock Screener
    funnel = screen_stocks('방산', get_stocks('방산'))
    assert 'leader' in funnel
    assert 'follower' in funnel
    assert 'nogo' in funnel
    
    # 4) Trade Plan
    plan = build_plan(funnel['leader'][0], {
        'period': '단기',
        'risk_profile': '중립'
    })
    assert plan['stop_loss'] < plan['entry']['pullback']
    assert plan['targets']['conservative'] > plan['entry']['pullback']
    
    # 5) Devil's Advocate
    counter = generate_counter({'scores': funnel['leader'][0]})
    assert len(counter['counter_arguments']) >= 2
```

---

#### Day 25-26: 문서화
```bash
docs/
├── USER_GUIDE.md             # 사용자 가이드
├── API_REFERENCE.md          # API 문서
├── SCORING_LOGIC.md          # 점수 계산 로직
└── DATA_SOURCES.md           # 데이터 출처
```

**USER_GUIDE.md:**
```markdown
# Decision Stream 사용 가이드

## 🚀 빠른 시작

1. 투자 기간 선택: 단기 (1~2주) / 중기 (1~3개월)
2. 리스크 성향 선택: 보수 / 중립 / 공격
3. Market Regime 확인 → Risk-On/Off
4. SURGE 섹터 클릭
5. Leader/Follower 종목 선택
6. 매매 계획 확인 (진입/손절/목표)
7. "확정" 버튼 클릭

## 📊 점수 해석

- **Flow Score (자금 흐름)**: 80+ = 강한 유입
- **Structure Score (가격 구조)**: 70+ = 견고한 상승
- **Narrative Score (서사)**: 60+ = 충분한 근거
- **Risk Score (리스크)**: 30- = 안전

## ⚠️ No-Go 종목

다음 종목은 자동으로 회피됩니다:
- 단일 기사 급등
- 갭 상승 후 분배
- 테마 말기 (5번째 이후)
- 개인 독주 (기관 이탈)
- 구조 파손
- 손절 불가

## 🎯 매매 계획 활용

1. **진입**: 돌파 OR 눌림 중 선택
2. **손절**: 반드시 지킬 것 (예외 없음)
3. **목표**: 보수 50% 익절 → 공격 목표 대기
4. **포지션**: 자동 계산된 비중 준수
```

---

#### Day 27-28: 배포
```bash
# Railway 배포
railway login
railway init
railway up

# 환경 변수 설정
railway variables set API_KEY=ds-test-2026
railway variables set REDIS_URL=...
```

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "backend.api.server:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 📊 MVP 완성 체크리스트

### 핵심 기능 ✅
- [ ] Market Regime Analyst
- [ ] Sector Scout (Top 10)
- [ ] Stock Screener (Leader/Follower/No-Go)
- [ ] Trade Plan Builder
- [ ] Devil's Advocate

### 점수 엔진 ✅
- [ ] Flow Score (0~100)
- [ ] Structure Score (0~100)
- [ ] Narrative Score (0~100)
- [ ] Risk Score (0~100)
- [ ] Momentum Quality (진짜 vs 가짜)

### No-Go 시스템 ✅
- [ ] 핵심 6개 규칙 구현
- [ ] 모멘텀 진위 판별
- [ ] 테마 피로도 추적

### 데이터 파이프라인 ✅
- [ ] KRX 투자자별 매매동향
- [ ] OpenDART 공시
- [ ] Yahoo Finance EOD
- [ ] 캐싱 시스템

### UI/UX ✅
- [ ] Why Drawer (1클릭 근거)
- [ ] No-Go 라벨
- [ ] Trade Plan Card
- [ ] 수동 입력 2개 (기간/성향)

### 문서 ✅
- [ ] 사용자 가이드
- [ ] API 문서
- [ ] 점수 로직 설명

---

## 💰 예상 비용

```
데이터:
- KRX: 무료
- OpenDART: 무료
- Yahoo Finance: 무료
합계: ₩0

서버:
- Railway Hobby: $5/월 (₩6,500)
- Redis Cloud Free: 무료
합계: ₩6,500/월

총 운영비: ₩6,500/월
→ 9,900원 구독 시 월 3,400원 이익
```

---

## 📈 V2 업그레이드 (차별화)

### Premium (₩19,900/월)
- 조건 알림 (Slack/Email)
- 성과 기록 추적
- 실시간 미국 데이터 (15분 지연)

### Elite (₩29,900/월)
- 포트폴리오 리밸런싱
- AI 백테스트
- 증권사 API 연동

---

## 🎯 성공 지표

**4주 후 목표:**
- [ ] Leader 추천 승률 > 55%
- [ ] No-Go 회피 성공률 > 75%
- [ ] 의사결정 시간 < 3분
- [ ] 모든 점수에 출처 100%
- [ ] 모든 추천에 반대 의견 100%

---

## 🚀 시작하기

```bash
# 1) 백엔드 설정
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2) 데이터 수집 테스트
python -m data.krx_collector
python -m data.dart_collector

# 3) Agent 테스트
python -m agents.market_regime
python -m agents.sector_scout

# 4) API 서버 실행
uvicorn api.server:app --reload

# 5) 프론트엔드 열기
# index.html을 브라우저에서 열기
```

---

**마지막 점검:**

> ✅ 무료 데이터만 사용  
> ✅ 모든 판단에 근거  
> ✅ 수동 입력 2개만  
> ✅ 설명 가능한 자동화  
> ✅ 선동이 아닌 판단 도구

**Let's build! 🚀**
