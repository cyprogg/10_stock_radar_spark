"""
Agent Orchestrator
5개 AI Agent를 순차적으로 실행하는 통합 오케스트레이터
"""

from typing import Dict, List, Any
from .market_regime_analyst import MarketRegimeAnalyst
from .sector_scout import SectorScout
from .stock_screener import StockScreener
from .trade_plan_builder import TradePlanBuilder
from .devils_advocate import DevilsAdvocate


class AgentOrchestrator:
    """AI Agent 통합 실행 오케스트레이터"""
    
    def __init__(self):
        self.market_analyst = MarketRegimeAnalyst()
        self.sector_scout = SectorScout()
        self.stock_screener = StockScreener()
        self.trade_plan_builder = TradePlanBuilder()
        self.devils_advocate = DevilsAdvocate()
        
    def run_full_analysis(self, 
                         market_data: Dict[str, Any],
                         sectors_data: List[Dict[str, Any]],
                         stocks_data: List[Dict[str, Any]],
                         user_profile: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        전체 분석 파이프라인 실행
        
        Args:
            market_data: 시장 데이터
            sectors_data: 섹터 데이터 리스트
            stocks_data: 종목 데이터 리스트
            user_profile: 사용자 프로필 (선택)
            
        Returns:
            전체 분석 결과
        """
        # 기본 사용자 프로필
        if user_profile is None:
            user_profile = {
                "period": "단기",
                "risk_profile": "중립",
                "account_size": 0
            }
        
        # ========== Step 1: Market Regime Analysis ==========
        print("🌍 Step 1: Analyzing market regime...")
        market_regime = self.market_analyst.analyze(market_data)
        
        # ========== Step 2: Sector Scouting ==========
        print("🔍 Step 2: Ranking sectors...")
        ranked_sectors = self.sector_scout.rank_sectors(sectors_data)
        
        # ========== Step 3: Stock Screening ==========
        print("🎯 Step 3: Screening stocks...")
        screened_stocks = self.stock_screener.screen_stocks(stocks_data)
        
        # ========== Step 4: Trade Plan Building ==========
        print("📋 Step 4: Building trade plans...")
        trade_plans = []
        
        # 리더와 팔로워 종목에 대해 매매 계획 생성
        for stock in screened_stocks['leaders'][:5]:  # 상위 5개만
            # 종목 데이터를 trade_plan_builder 형식으로 변환
            stock_data_for_plan = self._prepare_stock_data_for_trade_plan(
                stock, stocks_data
            )
            trade_plan = self.trade_plan_builder.build_trade_plan(
                stock_data_for_plan, user_profile
            )
            trade_plans.append({
                **stock,
                "trade_plan": trade_plan
            })
        
        # ========== Step 5: Devil's Advocate ==========
        print("😈 Step 5: Generating counter-arguments...")
        final_recommendations = []
        
        for plan in trade_plans:
            with_counter = self.devils_advocate.analyze_recommendation(
                plan, 
                additional_data=self._get_additional_data(plan, ranked_sectors)
            )
            final_recommendations.append(with_counter)
        
        # ========== Final Result ==========
        # Summary 생성 (원본 screened_stocks 사용)
        summary = self._generate_summary(
            market_regime, ranked_sectors, screened_stocks, final_recommendations
        )
        
        return {
            "timestamp": market_regime.get("sources", [{}])[0].get("timestamp", ""),
            "market_regime": market_regime,
            "ranked_sectors": ranked_sectors[:10],  # 상위 10개 섹터
            "screened_stocks": {
                "leaders": screened_stocks['leaders'][:10],
                "followers": screened_stocks['followers'][:10],
                "nogo_count": len(screened_stocks['nogo'])
            },
            "recommendations": final_recommendations,
            "summary": summary
        }
    
    def run_quick_analysis(self,
                          market_data: Dict[str, Any],
                          stock_data: Dict[str, Any],
                          user_profile: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        단일 종목 빠른 분석 (Agent 1, 3, 4, 5만 실행)
        
        Args:
            market_data: 시장 데이터
            stock_data: 단일 종목 데이터
            user_profile: 사용자 프로필
            
        Returns:
            종목 분석 결과
        """
        if user_profile is None:
            user_profile = {
                "period": "단기",
                "risk_profile": "중립",
                "account_size": 0
            }
        
        # Step 1: Market Regime
        market_regime = self.market_analyst.analyze(market_data)
        
        # Step 3: Stock Classification
        stock_classification = self.stock_screener.classify_stock(stock_data)
        
        # 진입 가능한 종목인 경우만 매매 계획 생성
        trade_plan = None
        if stock_classification['classification'] != 'NO_GO':
            stock_data_for_plan = self._prepare_stock_data_for_trade_plan(
                stock_classification, [stock_data]
            )
            trade_plan = self.trade_plan_builder.build_trade_plan(
                stock_data_for_plan, user_profile
            )
        
        # Step 5: Devil's Advocate
        recommendation = {
            **stock_classification,
            "trade_plan": trade_plan
        }
        final_result = self.devils_advocate.analyze_recommendation(recommendation)
        
        return {
            "market_regime": market_regime,
            "stock_analysis": final_result
        }
    
    def _prepare_stock_data_for_trade_plan(self, 
                                          stock_result: Dict[str, Any],
                                          stocks_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """종목 데이터를 trade plan builder 형식으로 변환"""
        ticker = stock_result.get('ticker', '')
        
        # 원본 데이터에서 찾기
        original_data = next(
            (s for s in stocks_data if s.get('ticker') == ticker),
            {}
        )
        
        return {
            "ticker": ticker,
            "name": stock_result.get('name', ''),
            "currency": stock_result.get('currency') or original_data.get('currency', 'KRW'),  # stock_result 우선, 없으면 original_data
            "current_price": original_data.get('current_price', 0),
            "support_levels": original_data.get('support_levels', []),
            "resistance_levels": original_data.get('resistance_levels', []),
            "ma20": original_data.get('ma20', 0),
            "ma60": original_data.get('ma60', 0),
            "atr_20d": original_data.get('atr_20d', 0),
            "volatility": original_data.get('volatility', 0)
        }
    
    def _get_additional_data(self, 
                            stock_result: Dict[str, Any],
                            ranked_sectors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Devil's Advocate를 위한 추가 데이터 준비"""
        sector = stock_result.get('sector', '')
        
        # 섹터 정보 찾기
        sector_info = next(
            (s for s in ranked_sectors if s.get('sector') == sector),
            {}
        )
        
        return {
            "sector_rank": 0,  # 실제로는 섹터 내 종목 순위 필요
            "theme_duration": sector_info.get('duration', 0),
            "per": 0,  # 실제 데이터 필요
            "pbr": 0,  # 실제 데이터 필요
            "sector_avg_per": 0,  # 실제 데이터 필요
            "price_gap": 0  # 실제 데이터 필요
        }
    
    def _generate_summary(self,
                         market_regime: Dict[str, Any],
                         ranked_sectors: List[Dict[str, Any]],
                         screened_stocks: Dict[str, Any],
                         recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """전체 분석 요약 생성"""
        # screened_stocks가 원본 형태인지 변형된 형태인지 확인
        nogo_count = screened_stocks.get('nogo_count', len(screened_stocks.get('nogo', [])))
        
        return {
            "market_state": market_regime.get('state', 'UNKNOWN'),
            "market_score": f"{market_regime.get('score', 0)}/{market_regime.get('max_score', 3)}",
            "playbook": market_regime.get('playbook', ''),
            "top_sectors": [s['sector'] for s in ranked_sectors[:3]],
            "leaders_count": len(screened_stocks['leaders']),
            "followers_count": len(screened_stocks['followers']),
            "nogo_count": nogo_count,
            "top_recommendations": [
                {
                    "ticker": r.get('ticker', ''),
                    "name": r.get('name', ''),
                    "classification": r.get('classification', ''),
                    "action": r.get('action', ''),
                    "confidence": r.get('confidence', 0)
                }
                for r in recommendations[:3]
            ]
        }
