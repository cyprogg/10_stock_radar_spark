"""
AI Agents 사용 예제

5개 AI Agent를 개별적으로 또는 통합하여 사용하는 방법을 보여줍니다.
"""

from agents import (
    MarketRegimeAnalyst,
    SectorScout,
    StockScreener,
    TradePlanBuilder,
    DevilsAdvocate
)
from agents.orchestrator import AgentOrchestrator


def example_1_market_regime():
    """예제 1: 시장 상태 분석"""
    print("\n" + "="*60)
    print("예제 1: Market Regime Analyst")
    print("="*60)
    
    analyst = MarketRegimeAnalyst()
    
    # 샘플 시장 데이터
    market_data = {
        "us_10y": 4.25,
        "us_10y_change_20d": -0.15,
        "usd_krw": 1320,
        "usd_krw_change_20d": 0.8,
        "kospi": 2650,
        "kospi_vs_ma20": 1.02,
        "kospi_vs_ma60": 1.05,
        "kospi_from_high": -5.2,
        "sp500": 5200,
        "sp500_vs_ma20": 1.03,
        "sp500_vs_ma60": 1.08,
        "vix": 15.2,
        "vkospi": 18.5,
        "kospi_advancers": 650,
        "kospi_decliners": 500,
        "breadth_ratio": 1.3
    }
    
    result = analyst.analyze(market_data)
    
    print(f"\n시장 상태: {result['state']}")
    print(f"점수: {result['score']}/{result['max_score']}")
    print(f"신뢰도: {result['confidence']}%")
    print(f"\nPlaybook: {result['playbook']}")
    print(f"\n긍정 신호:")
    for signal in result['signals']['positive']:
        print(f"  ✓ {signal}")
    print(f"\n부정 신호:")
    for signal in result['signals']['negative']:
        print(f"  ✗ {signal}")


def example_2_sector_scout():
    """예제 2: 섹터 분석 및 랭킹"""
    print("\n" + "="*60)
    print("예제 2: Sector Scout")
    print("="*60)
    
    scout = SectorScout()
    
    # 샘플 섹터 데이터
    sectors_data = [
        {
            "sector": "방산",
            "volume_change_20d": 2.5,
            "foreign_net_buy_5d": 150,
            "inst_net_buy_5d": 200,
            "price_change_20d": 15.2,
            "ma20_slope": 0.8,
            "new_high_stocks": 3,
            "news_count_7d": 25,
            "policy_keywords": ["수출", "계약"],
            "disclosure_count": 2,
            "duration": 14
        },
        {
            "sector": "반도체",
            "volume_change_20d": 1.8,
            "foreign_net_buy_5d": 300,
            "inst_net_buy_5d": 150,
            "price_change_20d": 8.5,
            "ma20_slope": 0.5,
            "new_high_stocks": 5,
            "news_count_7d": 15,
            "policy_keywords": ["AI", "반도체"],
            "disclosure_count": 1,
            "duration": 7
        }
    ]
    
    ranked_sectors = scout.rank_sectors(sectors_data)
    
    print(f"\n섹터 랭킹:")
    for sector in ranked_sectors:
        print(f"\n{sector['rank']}위: {sector['sector']}")
        print(f"  자금 흐름: {sector['flow_score']}/100")
        print(f"  신호: {sector['signal']}")
        print(f"  지속: {sector['duration']}")
        print(f"  신뢰도: {sector['confidence']}%")
        print(f"  Why: {', '.join(sector['why'][:2])}")


def example_3_stock_screener():
    """예제 3: 종목 스크리닝"""
    print("\n" + "="*60)
    print("예제 3: Stock Screener")
    print("="*60)
    
    screener = StockScreener()
    
    # 샘플 종목 데이터 (리더 후보)
    stock_data_leader = {
        "ticker": "012345",
        "name": "ABC전자",
        "sector": "반도체",
        "flow_score": 85,
        "cycle_fit": True,
        "quality_score": 90,
        "governance_score": 80,
        "narrative_score": 75,
        "risk_score": 15,
        "time_fit": True,
        "value_score": 70,
        "momentum_quality": {
            "sector_sync": True,
            "inst_participation": True,
            "news_type": "fundamental",
            "group_rally": True
        },
        "gap_up_with_distribution": False,
        "single_rumor": False,
        "late_theme": False,
        "no_structure": False,
        "retail_dominance": 0.3
    }
    
    result = screener.classify_stock(stock_data_leader)
    
    print(f"\n종목: {result['name']} ({result['ticker']})")
    print(f"분류: {result['classification']}")
    print(f"액션: {result['action']}")
    print(f"신뢰도: {result['confidence']}%")
    print(f"\n9요소 점수:")
    for key, value in result['scores'].items():
        print(f"  {key}: {value}")
    print(f"\n선정 이유:")
    for why in result.get('why_leader', result.get('why_follower', [])):
        print(f"  • {why}")


def example_4_trade_plan():
    """예제 4: 매매 계획 생성"""
    print("\n" + "="*60)
    print("예제 4: Trade Plan Builder")
    print("="*60)
    
    builder = TradePlanBuilder()
    
    # 샘플 종목 데이터
    stock_data = {
        "ticker": "012345",
        "name": "ABC전자",
        "current_price": 75000,
        "support_levels": [72000, 70000],
        "resistance_levels": [78000, 80000],
        "ma20": 73000,
        "ma60": 71000,
        "atr_20d": 2500,
        "volatility": 3.2
    }
    
    # 사용자 프로필
    user_profile = {
        "period": "단기",
        "risk_profile": "중립",
        "account_size": 10000000
    }
    
    trade_plan = builder.build_trade_plan(stock_data, user_profile)
    
    print(f"\n종목: {trade_plan['name']} ({trade_plan['ticker']})")
    print(f"현재가: {trade_plan['current_price']:,}원")
    print(f"\n진입가:")
    print(f"  돌파: {trade_plan['entry']['breakout']:,}원")
    print(f"  눌림: {trade_plan['entry']['pullback']:,}원")
    print(f"\n손절가: {trade_plan['stop_loss']:,}원")
    print(f"\n목표가:")
    print(f"  보수: {trade_plan['targets']['conservative']:,}원")
    print(f"  공격: {trade_plan['targets']['aggressive']:,}원")
    print(f"\n포지션 사이즈:")
    print(f"  비중: {trade_plan['position_size']['percent']}%")
    print(f"  주식수: {trade_plan['position_size']['shares']}주")
    print(f"  금액: {trade_plan['position_size']['amount']:,}원")
    print(f"\n리스크/리워드: 1:{trade_plan['risk_reward_ratio']}")
    print(f"\n분할 매매 계획:")
    for step in trade_plan['split_plan']:
        print(f"  {step['action']} {step['percent']}% @ {step['price']:,}원 ({step['condition']})")


def example_5_devils_advocate():
    """예제 5: 반론 생성"""
    print("\n" + "="*60)
    print("예제 5: Devil's Advocate")
    print("="*60)
    
    advocate = DevilsAdvocate()
    
    # 샘플 추천 결과
    recommendation = {
        "ticker": "012345",
        "name": "ABC전자",
        "action": "BUY_PULLBACK",
        "classification": "FOLLOWER",
        "scores": {
            "1_flow": 85,
            "2_cycle": True,
            "3_quality": 90,
            "4_governance": 80,
            "5_narrative": 75,
            "6_risk": 25,
            "7_time_fit": True,
            "8_value": 45,
            "9_momentum": 68
        },
        "why": ["섹터 동반 상승", "기관 참여 확인"]
    }
    
    additional_data = {
        "sector_rank": 3,
        "theme_duration": 18,
        "per": 25,
        "sector_avg_per": 18,
        "price_gap": 9.5
    }
    
    result = advocate.generate_counter_arguments(recommendation, additional_data)
    
    print(f"\n반론 사항:")
    for i, counter in enumerate(result['counter_arguments'], 1):
        print(f"\n{i}. [{counter['category']}] {counter['severity'].upper()}")
        print(f"   {counter['point']}")
        print(f"   출처: {counter['source']}")
    
    print(f"\n최종 노트:")
    print(f"  {result['final_note']}")


def example_6_orchestrator():
    """예제 6: 전체 파이프라인 실행"""
    print("\n" + "="*60)
    print("예제 6: Agent Orchestrator (전체 파이프라인)")
    print("="*60)
    
    orchestrator = AgentOrchestrator()
    
    # 샘플 데이터 준비
    market_data = {
        "vix": 15.2,
        "kospi_vs_ma20": 1.02,
        "kospi_vs_ma60": 1.05,
        "breadth_ratio": 1.3,
        "kospi_from_high": -5.2,
        "sp500_vs_ma20": 1.03,
        "sp500_vs_ma60": 1.08
    }
    
    sectors_data = [
        {
            "sector": "방산",
            "volume_change_20d": 2.5,
            "foreign_net_buy_5d": 150,
            "inst_net_buy_5d": 200,
            "price_change_20d": 15.2,
            "ma20_slope": 0.8,
            "new_high_stocks": 3,
            "news_count_7d": 25,
            "policy_keywords": ["수출", "계약"],
            "disclosure_count": 2,
            "duration": 14
        }
    ]
    
    stocks_data = [
        {
            "ticker": "012345",
            "name": "ABC전자",
            "sector": "방산",
            "current_price": 75000,
            "support_levels": [72000, 70000],
            "resistance_levels": [78000, 80000],
            "ma20": 73000,
            "ma60": 71000,
            "atr_20d": 2500,
            "volatility": 3.2,
            "flow_score": 85,
            "cycle_fit": True,
            "quality_score": 90,
            "governance_score": 80,
            "narrative_score": 75,
            "risk_score": 15,
            "time_fit": True,
            "value_score": 70,
            "momentum_quality": {
                "sector_sync": True,
                "inst_participation": True,
                "news_type": "fundamental",
                "group_rally": True
            }
        }
    ]
    
    user_profile = {
        "period": "단기",
        "risk_profile": "중립",
        "account_size": 10000000
    }
    
    result = orchestrator.run_full_analysis(
        market_data, sectors_data, stocks_data, user_profile
    )
    
    print(f"\n전체 분석 요약:")
    summary = result['summary']
    print(f"  시장 상태: {summary['market_state']} ({summary['market_score']})")
    print(f"  Playbook: {summary['playbook']}")
    print(f"  상위 섹터: {', '.join(summary['top_sectors'])}")
    print(f"  리더: {summary['leaders_count']}개")
    print(f"  팔로워: {summary['followers_count']}개")
    print(f"  No-Go: {summary['nogo_count']}개")
    
    if summary['top_recommendations']:
        print(f"\n추천 종목:")
        for rec in summary['top_recommendations']:
            print(f"  • {rec['name']} ({rec['ticker']})")
            print(f"    분류: {rec['classification']} | 액션: {rec['action']} | 신뢰도: {rec['confidence']}%")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("AI Agents 사용 예제")
    print("="*60)
    
    # 개별 Agent 예제
    example_1_market_regime()
    example_2_sector_scout()
    example_3_stock_screener()
    example_4_trade_plan()
    example_5_devils_advocate()
    
    # 통합 Orchestrator 예제
    example_6_orchestrator()
    
    print("\n" + "="*60)
    print("예제 실행 완료!")
    print("="*60 + "\n")
