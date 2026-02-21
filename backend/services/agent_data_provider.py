"""
Agent Data Provider
AI Agent를 위한 데이터 수집 및 가공 서비스
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import os

# 미국 주식 서비스 import
try:
    from services.us_stock_service import USStockService
except ImportError:
    from .us_stock_service import USStockService


class AgentDataProvider:
    """Agent를 위한 데이터 제공자"""
    
    def __init__(self, use_real_us_data: bool = True):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_dir = os.path.join(self.base_dir, "data")
        
        # 미국 주식 서비스 초기화
        self.use_real_us_data = use_real_us_data
        if use_real_us_data:
            try:
                self.us_stock_service = USStockService()
                print("✅ US Stock Service initialized (yfinance)")
            except Exception as e:
                print(f"⚠️ US Stock Service initialization failed: {e}")
                self.us_stock_service = None
        else:
            self.us_stock_service = None
        
    def get_market_data(self) -> Dict[str, Any]:
        """
        시장 데이터 수집
        
        Returns:
            Market Regime Analyst에 필요한 시장 데이터
        """
        # TODO: 실제 API 연동 필요
        # 현재는 샘플 데이터 반환
        
        return {
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
    
    def get_sectors_data(self, sectors: List[str] = None) -> List[Dict[str, Any]]:
        """
        섹터별 데이터 수집
        
        Args:
            sectors: 분석할 섹터 리스트 (None이면 전체)
            
        Returns:
            Sector Scout에 필요한 섹터 데이터 리스트
        """
        # TODO: 실제 섹터 데이터 수집 로직 구현
        
        # 기본 섹터 리스트
        default_sectors = ["반도체", "방산", "2차전지", "바이오", "IT"]
        
        if sectors is None:
            sectors = default_sectors
        
        sectors_data = []
        
        for sector in sectors:
            sector_data = self._get_sector_data(sector)
            if sector_data:
                sectors_data.append(sector_data)
        
        return sectors_data
    
    def get_stocks_data(self, tickers: List[str]) -> List[Dict[str, Any]]:
        """
        종목 데이터 수집
        
        Args:
            tickers: 종목 코드 리스트
            
        Returns:
            Stock Screener에 필요한 종목 데이터 리스트
        """
        stocks_data = []
        
        for ticker in tickers:
            stock_data = self._get_stock_data(ticker)
            if stock_data:
                stocks_data.append(stock_data)
        
        return stocks_data
    
    def _get_sector_data(self, sector: str) -> Optional[Dict[str, Any]]:
        """섹터 데이터 생성"""
        # TODO: 실제 데이터 수집 로직 구현
        
        # 샘플 데이터 (섹터별 차별화)
        sector_configs = {
            "반도체": {
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
            },
            "방산": {
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
            "2차전지": {
                "volume_change_20d": 1.5,
                "foreign_net_buy_5d": 200,
                "inst_net_buy_5d": 100,
                "price_change_20d": 5.8,
                "ma20_slope": 0.3,
                "new_high_stocks": 2,
                "news_count_7d": 12,
                "policy_keywords": ["ESG", "친환경"],
                "disclosure_count": 1,
                "duration": 21
            },
            "바이오": {
                "volume_change_20d": 2.2,
                "foreign_net_buy_5d": 80,
                "inst_net_buy_5d": 120,
                "price_change_20d": 12.3,
                "ma20_slope": 0.6,
                "new_high_stocks": 4,
                "news_count_7d": 18,
                "policy_keywords": ["신약", "임상"],
                "disclosure_count": 3,
                "duration": 10
            },
            "IT": {
                "volume_change_20d": 1.3,
                "foreign_net_buy_5d": 180,
                "inst_net_buy_5d": 90,
                "price_change_20d": 6.5,
                "ma20_slope": 0.4,
                "new_high_stocks": 3,
                "news_count_7d": 10,
                "policy_keywords": ["클라우드", "SaaS"],
                "disclosure_count": 1,
                "duration": 15
            }
        }
        
        config = sector_configs.get(sector)
        if not config:
            return None
        
        return {
            "sector": sector,
            **config
        }
    
    def _get_stock_data(self, ticker: str) -> Optional[Dict[str, Any]]:
        """종목 데이터 생성"""
        # 한국 주식 감지 (6자리 숫자)
        is_korean_stock = ticker and ticker.isdigit() and len(ticker) == 6
        
        # 미국 주식 감지 (알파벳으로 시작)
        is_us_stock = ticker and not ticker[0].isdigit()
        
        # 실시간 데이터 사용 가능한 경우
        if self.us_stock_service and (is_us_stock or is_korean_stock):
            try:
                if is_korean_stock:
                    # 한국 주식: Yahoo Finance (.KS)
                    return self._get_kr_stock_data_real(ticker)
                else:
                    # 미국 주식: Yahoo Finance
                    return self._get_us_stock_data_real(ticker)
            except Exception as e:
                print(f"⚠️ Failed to fetch real data for {ticker}: {e}")
                print("   Falling back to mock data...")
        
        # Mock 데이터 사용 (실패 시)
        return self._get_stock_data_mock(ticker)
    
    def _get_us_stock_data_real(self, ticker: str) -> Dict[str, Any]:
        """미국 주식 실제 데이터 조회 (Yahoo Finance)"""
        # 일봉 데이터 가져오기 (전일 종가용)
        daily_data = self.us_stock_service.get_daily_data(ticker, period="3mo")
        
        if not daily_data or len(daily_data) == 0:
            raise Exception(f"No data available for {ticker}")
        
        # 전일 종가 = 일봉 데이터의 마지막 close
        last_close = daily_data[-1]['close']
        
        # 종목명 가져오기
        try:
            price_data = self.us_stock_service.get_current_price(ticker)
            stock_name = price_data['name']
        except:
            stock_name = ticker
        
        # 기술적 지표 계산
        closes = [d['close'] for d in daily_data[-60:]] if len(daily_data) >= 60 else []
        ma20 = sum(closes[-20:]) / 20 if len(closes) >= 20 else last_close * 0.97
        ma60 = sum(closes) / 60 if len(closes) >= 60 else last_close * 0.95
        
        # ATR 계산 (간단 버전)
        highs = [d['high'] for d in daily_data[-20:]] if len(daily_data) >= 20 else []
        lows = [d['low'] for d in daily_data[-20:]] if len(daily_data) >= 20 else []
        if highs and lows:
            ranges = [h - l for h, l in zip(highs, lows)]
            atr_20d = sum(ranges) / len(ranges)
        else:
            atr_20d = last_close * 0.03
        
        # Volatility 계산
        if len(closes) >= 20:
            returns = [(closes[i] - closes[i-1]) / closes[i-1] for i in range(1, len(closes))]
            volatility = (sum(r**2 for r in returns) / len(returns)) ** 0.5 * 100
        else:
            volatility = 3.0
        
        # Agent가 필요한 형식으로 변환
        return {
            "ticker": ticker,
            "name": stock_name,
            "sector": self._guess_sector(ticker),  # 섹터는 추정
            "currency": "USD",
            "current_price": round(last_close, 2),  # 전일 종가
            "support_levels": [
                round(last_close * 0.97, 2),
                round(last_close * 0.94, 2)
            ],
            "resistance_levels": [
                round(last_close * 1.03, 2),
                round(last_close * 1.06, 2)
            ],
            "ma20": round(ma20, 2),
            "ma60": round(ma60, 2),
            "atr_20d": round(atr_20d, 2),
            "volatility": round(volatility, 1),
            # 나머지는 기본값 (추후 실제 데이터로 대체 가능)
            "flow_score": 85,
            "cycle_fit": True,
            "quality_score": 90,
            "governance_score": 85,
            "narrative_score": 80,
            "risk_score": 18,
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
    
    def _get_kr_stock_data_real(self, ticker: str) -> Dict[str, Any]:
        """한국 주식 실제 데이터 조회 (Yahoo Finance .KS)"""
        # Yahoo Finance는 한국 주식에 .KS 접미사 사용
        yahoo_ticker = f"{ticker}.KS"
        
        # 일봉 데이터 가져오기 (전일 종가용)
        daily_data = self.us_stock_service.get_daily_data(yahoo_ticker, period="3mo")
        
        if not daily_data or len(daily_data) == 0:
            raise Exception(f"No data available for {ticker}")
        
        # 전일 종가 = 일봉 데이터의 마지막 close
        last_close = daily_data[-1]['close']
        
        # 종목명 가져오기
        try:
            price_data = self.us_stock_service.get_current_price(yahoo_ticker)
            stock_name = price_data['name']
        except:
            stock_name = ticker
        
        # 기술적 지표 계산
        closes = [d['close'] for d in daily_data[-60:]] if len(daily_data) >= 60 else []
        ma20 = sum(closes[-20:]) / 20 if len(closes) >= 20 else last_close * 0.97
        ma60 = sum(closes) / 60 if len(closes) >= 60 else last_close * 0.95
        
        # ATR 계산 (간단 버전)
        highs = [d['high'] for d in daily_data[-20:]] if len(daily_data) >= 20 else []
        lows = [d['low'] for d in daily_data[-20:]] if len(daily_data) >= 20 else []
        if highs and lows:
            ranges = [h - l for h, l in zip(highs, lows)]
            atr_20d = sum(ranges) / len(ranges)
        else:
            atr_20d = last_close * 0.03
        
        # Volatility 계산
        if len(closes) >= 20:
            returns = [(closes[i] - closes[i-1]) / closes[i-1] for i in range(1, len(closes))]
            volatility = (sum(r**2 for r in returns) / len(returns)) ** 0.5 * 100
        else:
            volatility = 3.0
        
        # Agent가 필요한 형식으로 변환 (한국 주식은 KRW)
        return {
            "ticker": ticker,
            "name": stock_name,
            "sector": self._guess_sector_kr(ticker),  # 한국 주식 섹터 추정
            "currency": "KRW",
            "current_price": round(last_close, 0),  # 전일 종가
            "support_levels": [
                round(last_close * 0.97, 0),
                round(last_close * 0.94, 0)
            ],
            "resistance_levels": [
                round(last_close * 1.03, 0),
                round(last_close * 1.06, 0)
            ],
            "ma20": round(ma20, 0),
            "ma60": round(ma60, 0),
            "atr_20d": round(atr_20d, 0),
            "volatility": round(volatility, 1),
            # 나머지는 기본값
            "flow_score": 85,
            "cycle_fit": True,
            "quality_score": 90,
            "governance_score": 85,
            "narrative_score": 80,
            "risk_score": 18,
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
    
    def _guess_sector(self, ticker: str) -> str:
        """티커로 섹터 추정 (간단 버전)"""
        sector_map = {
            'NVDA': 'AI 반도체',
            'AMD': 'AI 반도체',
            'INTC': 'AI 반도체',
            'LMT': '방산',
            'RTX': '방산',
            'BA': '방산',
            'NOC': '방산',
            'GD': '방산',
            'JNJ': '헬스케어',
            'PFE': '헬스케어',
            'UNH': '헬스케어',
            'AAPL': 'IT',
            'MSFT': 'IT',
            'GOOGL': 'IT',
            'AMZN': 'IT',
            'TSLA': '전기차'
        }
        return sector_map.get(ticker, 'IT')
    
    def _guess_sector_kr(self, ticker: str) -> str:
        """한국 주식 티커로 섹터 추정"""
        sector_map = {
            '005930': '반도체',      # 삼성전자
            '000660': '반도체',      # SK하이닉스
            '207940': '바이오',      # 삼성바이오로직스
            '068270': '제약',        # 셀트리온
            '035720': 'IT',          # 카카오
            '035420': 'IT',          # NAVER
            '051910': '화학',        # LG화학
            '006400': '철강',        # 삼성SDI
            '005380': '자동차',      # 현대차
            '000270': '항공',        # 기아
            '012330': '자동차부품',  # 현대모비스
            '079550': '방산',        # LIG넥스원
            '047810': '방산',        # 한화에어로스페이스
        }
        return sector_map.get(ticker, 'IT')
    
    def _get_stock_data_mock(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Mock 데이터 생성 (기존 로직)"""
        # 샘플 데이터 (주요 종목별 차별화)
        stock_configs = {
            "005930": {  # 삼성전자
                "name": "삼성전자",
                "sector": "반도체",
                "currency": "KRW",
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
                "governance_score": 85,
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
            },
            "000660": {  # SK하이닉스
                "name": "SK하이닉스",
                "sector": "반도체",
                "currency": "KRW",
                "current_price": 180000,
                "support_levels": [175000, 170000],
                "resistance_levels": [185000, 190000],
                "ma20": 178000,
                "ma60": 175000,
                "atr_20d": 6000,
                "volatility": 3.8,
                "flow_score": 82,
                "cycle_fit": True,
                "quality_score": 88,
                "governance_score": 80,
                "narrative_score": 78,
                "risk_score": 18,
                "time_fit": True,
                "value_score": 65,
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
                "retail_dominance": 0.35
            },
            "012450": {  # 한화에어로스페이스
                "name": "한화에어로스페이스",
                "sector": "방산",
                "currency": "KRW",
                "current_price": 350000,
                "support_levels": [340000, 330000],
                "resistance_levels": [360000, 370000],
                "ma20": 345000,
                "ma60": 340000,
                "atr_20d": 15000,
                "volatility": 4.5,
                "flow_score": 92,
                "cycle_fit": True,
                "quality_score": 85,
                "governance_score": 78,
                "narrative_score": 88,
                "risk_score": 22,
                "time_fit": True,
                "value_score": 60,
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
                "retail_dominance": 0.4
            },
            # 미국 주식 추가
            "NVDA": {  # NVIDIA
                "name": "NVIDIA",
                "sector": "AI 반도체",
                "currency": "USD",
                "current_price": 875.00,
                "support_levels": [850.00, 820.00],
                "resistance_levels": [900.00, 925.00],
                "ma20": 860.00,
                "ma60": 840.00,
                "atr_20d": 25.00,
                "volatility": 3.5,
                "flow_score": 95,
                "cycle_fit": True,
                "quality_score": 95,
                "governance_score": 90,
                "narrative_score": 92,
                "risk_score": 18,
                "time_fit": True,
                "value_score": 55,
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
                "retail_dominance": 0.25
            },
            "LMT": {  # Lockheed Martin
                "name": "Lockheed Martin",
                "sector": "방산",
                "currency": "USD",
                "current_price": 445.50,
                "support_levels": [435.00, 425.00],
                "resistance_levels": [455.00, 465.00],
                "ma20": 440.00,
                "ma60": 435.00,
                "atr_20d": 8.50,
                "volatility": 2.8,
                "flow_score": 88,
                "cycle_fit": True,
                "quality_score": 92,
                "governance_score": 88,
                "narrative_score": 85,
                "risk_score": 16,
                "time_fit": True,
                "value_score": 68,
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
                "retail_dominance": 0.2
            },
            "AAPL": {  # Apple
                "name": "Apple",
                "sector": "IT",
                "currency": "USD",
                "current_price": 185.25,
                "support_levels": [180.00, 175.00],
                "resistance_levels": [190.00, 195.00],
                "ma20": 182.50,
                "ma60": 180.00,
                "atr_20d": 4.50,
                "volatility": 2.5,
                "flow_score": 82,
                "cycle_fit": True,
                "quality_score": 95,
                "governance_score": 92,
                "narrative_score": 78,
                "risk_score": 14,
                "time_fit": True,
                "value_score": 72,
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
                "retail_dominance": 0.35
            }
        }
        
        config = stock_configs.get(ticker)
        if not config:
            # 기본 템플릿 (한국 주식 기본)
            config = {
                "name": f"종목{ticker}",
                "sector": "기타",
                "currency": "KRW",
                "current_price": 50000,
                "support_levels": [48000, 46000],
                "resistance_levels": [52000, 54000],
                "ma20": 49000,
                "ma60": 48000,
                "atr_20d": 2000,
                "volatility": 3.5,
                "flow_score": 70,
                "cycle_fit": True,
                "quality_score": 75,
                "governance_score": 70,
                "narrative_score": 65,
                "risk_score": 25,
                "time_fit": True,
                "value_score": 60,
                "momentum_quality": {
                    "sector_sync": False,
                    "inst_participation": True,
                    "news_type": "fundamental",
                    "group_rally": False
                },
                "gap_up_with_distribution": False,
                "single_rumor": False,
                "late_theme": False,
                "no_structure": False,
                "retail_dominance": 0.5
            }
        
        return {
            "ticker": ticker,
            **config
        }
    
    def save_analysis_result(self, result: Dict[str, Any], filename: str = None):
        """
        분석 결과를 파일로 저장
        
        Args:
            result: Agent 분석 결과
            filename: 저장할 파일명 (None이면 자동 생성)
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"agent_analysis_{timestamp}.json"
        
        output_dir = os.path.join(self.base_dir, "output", "agent_results")
        os.makedirs(output_dir, exist_ok=True)
        
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"✅ 분석 결과 저장: {filepath}")
        return filepath
