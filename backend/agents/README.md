# AI Agents Module

## 📋 개요

5개의 AI Agent로 구성된 주식 분석 시스템입니다. 각 Agent는 특정 역할을 수행하며, 함께 작동하여 종합적인 투자 의사결정을 지원합니다.

## 🤖 5개 AI Agents

### 1. Market Regime Analyst 🌍
**역할:** 시장 상태 분석 (RISK_ON / RISK_OFF)

**주요 기능:**
- VIX, 이동평균, 시장 폭 등을 종합하여 시장 상태 판단
- 0~3 점수와 신뢰도 제공
- 상황에 맞는 Playbook 자동 생성

**사용 예시:**
```python
from agents import MarketRegimeAnalyst

analyst = MarketRegimeAnalyst()
result = analyst.analyze(market_data)

print(f"시장 상태: {result['state']}")  # RISK_ON or RISK_OFF
print(f"Playbook: {result['playbook']}")
```

### 2. Sector Scout 🔍
**역할:** 섹터별 자금흐름/강도/뉴스 분석 및 랭킹

**주요 기능:**
- 자금 흐름 점수 (0~100)
- 가격 구조 점수 (0~100)
- 서사 점수 (0~100)
- 섹터 신호: SURGE / NORMAL / WEAK

**사용 예시:**
```python
from agents import SectorScout

scout = SectorScout()
ranked_sectors = scout.rank_sectors(sectors_data)

for sector in ranked_sectors[:3]:
    print(f"{sector['rank']}위: {sector['sector']} ({sector['flow_score']}점)")
```

### 3. Stock Screener 🎯
**역할:** 종목을 Leader/Follower/No-go로 분류

**주요 기능:**
- 9요소 필수 조건 체크
- 6개 No-Go 규칙 적용
- 모멘텀 품질 평가 (0~100)
- 액션 추천: BUY_NOW / BUY_PULLBACK / AVOID

**사용 예시:**
```python
from agents import StockScreener

screener = StockScreener()
result = screener.classify_stock(stock_data)

print(f"분류: {result['classification']}")  # LEADER, FOLLOWER, NO_GO
print(f"액션: {result['action']}")
```

**No-Go 규칙 (6개):**
1. 단일 기사 급등 + 거래대금 폭증
2. 갭 상승 후 장대 음봉
3. 테마 내 5번째 이후 급등주
4. 개인 순매수 80%↑ + 기관 이탈
5. 핵심 이평(20/60) 동시 이탈
6. 손절선 설정 불가 (리스크 50 초과)

### 4. Trade Plan Builder 📋
**역할:** 사용자 맞춤 매매 계획 자동 생성

**주요 기능:**
- 손절가 우선 계산 (ATR 기반)
- 진입가 설정 (돌파/눌림)
- 목표가 설정 (리스크 대비 2~5배)
- 포지션 사이즈 계산 (Kelly Criterion)
- 분할 매매 계획

**사용 예시:**
```python
from agents import TradePlanBuilder

builder = TradePlanBuilder()
user_profile = {
    "period": "단기",
    "risk_profile": "중립",
    "account_size": 10000000
}

trade_plan = builder.build_trade_plan(stock_data, user_profile)

print(f"진입가: {trade_plan['entry']['pullback']:,}원")
print(f"손절가: {trade_plan['stop_loss']:,}원")
print(f"목표가: {trade_plan['targets']['aggressive']:,}원")
print(f"리스크/리워드: 1:{trade_plan['risk_reward_ratio']}")
```

### 5. Devil's Advocate 😈
**역할:** 반론 자동 생성 (최대 3개)

**주요 기능:**
- 밸류에이션 체크
- 리스크 체크
- 모멘텀 품질 체크
- 기술적 구조 체크
- 테마 피로도 체크
- Severity 평가: high / medium / low

**사용 예시:**
```python
from agents import DevilsAdvocate

advocate = DevilsAdvocate()
result = advocate.generate_counter_arguments(recommendation, additional_data)

for counter in result['counter_arguments']:
    print(f"[{counter['category']}] {counter['point']}")

print(f"최종 노트: {result['final_note']}")
```

## 🎼 Agent Orchestrator

5개 Agent를 순차적으로 실행하는 통합 오케스트레이터

**전체 분석 파이프라인:**
```python
from agents.orchestrator import AgentOrchestrator

orchestrator = AgentOrchestrator()

result = orchestrator.run_full_analysis(
    market_data,
    sectors_data,
    stocks_data,
    user_profile
)

# 결과 구조:
# - market_regime: 시장 상태
# - ranked_sectors: 섹터 랭킹
# - screened_stocks: 분류된 종목 (leaders/followers/nogo)
# - recommendations: 매매 계획 + 반론 포함
# - summary: 전체 요약
```

**빠른 단일 종목 분석:**
```python
result = orchestrator.run_quick_analysis(
    market_data,
    stock_data,
    user_profile
)

# Agent 1, 3, 4, 5만 실행 (섹터 분석 제외)
```

## 📊 데이터 형식

### Market Data
```python
market_data = {
    "vix": 15.2,
    "kospi_vs_ma20": 1.02,
    "kospi_vs_ma60": 1.05,
    "breadth_ratio": 1.3,
    "kospi_from_high": -5.2,
    # ... 추가 필드
}
```

### Sector Data
```python
sector_data = {
    "sector": "방산",
    "volume_change_20d": 2.5,
    "foreign_net_buy_5d": 150,
    "inst_net_buy_5d": 200,
    "price_change_20d": 15.2,
    # ... 추가 필드
}
```

### Stock Data
```python
stock_data = {
    "ticker": "012345",
    "name": "ABC전자",
    "sector": "반도체",
    "current_price": 75000,
    "flow_score": 85,
    "cycle_fit": True,
    "quality_score": 90,
    # ... 9요소 + 모멘텀 품질
}
```

### User Profile
```python
user_profile = {
    "period": "단기" | "중기",
    "risk_profile": "보수" | "중립" | "공격",
    "account_size": 10000000  # 선택 사항
}
```

## 🚀 시작하기

### 1. 개별 Agent 사용
```python
from agents import MarketRegimeAnalyst, SectorScout, StockScreener

# Agent 생성
analyst = MarketRegimeAnalyst()
scout = SectorScout()
screener = StockScreener()

# 실행
market_result = analyst.analyze(market_data)
sector_results = scout.rank_sectors(sectors_data)
stock_result = screener.classify_stock(stock_data)
```

### 2. Orchestrator 사용 (권장)
```python
from agents.orchestrator import AgentOrchestrator

orchestrator = AgentOrchestrator()
result = orchestrator.run_full_analysis(
    market_data, sectors_data, stocks_data, user_profile
)

# 전체 워크플로우가 자동으로 실행됩니다
```

### 3. 예제 실행
```bash
cd backend/agents
python example_usage.py
```

## 📁 파일 구조

```
backend/agents/
├── __init__.py                    # 모듈 초기화
├── market_regime_analyst.py       # Agent 1
├── sector_scout.py                # Agent 2
├── stock_screener.py              # Agent 3
├── trade_plan_builder.py          # Agent 4
├── devils_advocate.py             # Agent 5
├── orchestrator.py                # 통합 오케스트레이터
├── example_usage.py               # 사용 예제
└── README.md                      # 이 문서
```

## 🎯 핵심 철학

**"설명 가능한 자동화"**
- 모든 판단에는 근거가 있다
- 모든 근거에는 반대 의견이 있다
- 모든 점수는 0~100으로 통일
- 모든 데이터에는 출처가 있다

## 💡 활용 시나리오

### 시나리오 1: 일일 시장 점검
1. Market Regime Analyst로 시장 상태 확인
2. 결과에 따라 전략 조정 (공격/방어)

### 시나리오 2: 섹터 로테이션
1. Sector Scout로 강한 섹터 파악
2. 상위 3개 섹터의 종목 분석

### 시나리오 3: 종목 발굴
1. Stock Screener로 Leader 종목 필터링
2. Trade Plan Builder로 매매 계획 수립
3. Devil's Advocate로 리스크 검토

### 시나리오 4: 포트폴리오 관리
1. 보유 종목을 Stock Screener로 재평가
2. No-Go 조건 충족 시 청산 고려
3. Trade Plan으로 익절/손절 조정

## ⚠️ 주의사항

1. **실제 거래 전 검증 필수**: Agent의 결과는 참고용이며, 최종 판단은 본인의 책임입니다.
2. **데이터 품질**: 정확한 결과를 위해 신뢰할 수 있는 데이터 소스 사용
3. **리스크 관리**: Trade Plan의 손절가를 반드시 준수
4. **과최적화 주의**: 과거 데이터 기반 로직이므로 미래 성과를 보장하지 않음

## 📚 참고 문서

- [AI_AGENT_ARCHITECTURE.md](../../AI_AGENT_ARCHITECTURE.md) - 전체 아키텍처 설계
- [ALGORITHM_9_FACTORS_INTEGRATION.md](../../ALGORITHM_9_FACTORS_INTEGRATION.md) - 9요소 통합
- [MOMENTUM_QUALITY_FRAMEWORK.md](../../MOMENTUM_QUALITY_FRAMEWORK.md) - 모멘텀 품질 프레임워크

## 🔧 개발 정보

**버전:** 1.0.0  
**언어:** Python 3.8+  
**의존성:** 없음 (표준 라이브러리만 사용)

## 📝 라이선스

이 코드는 Stock Radar Spark 프로젝트의 일부입니다.
