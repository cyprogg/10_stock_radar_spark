"""
Agent Data Provider v2 - 통합 데이터 수집 서비스
Yahoo Finance + 네이버 크롤링 + OpenDART API 조합
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import yfinance as yf
import os
from dotenv import load_dotenv

# 로컬 서비스 import
try:
    from services.naver_stock_scraper import NaverStockScraper
    from services.market_breadth_calculator import MarketBreadthCalculator
    from services.us_stock_service import USStockService
except ImportError:
    from .naver_stock_scraper import NaverStockScraper
    from .market_breadth_calculator import MarketBreadthCalculator
    from .us_stock_service import USStockService

# .env 로드
load_dotenv()


class AgentDataProviderV2:
    """5개 AI Agent를 위한 통합 데이터 제공자"""
    
    def __init__(self):
        self.naver_scraper = NaverStockScraper()
        self.breadth_calc = MarketBreadthCalculator()
        self.us_service = USStockService()
        self.opendart_api_key = os.getenv('OPENDART_API_KEY', '')
    
    # ========== Market Regime Analyst용 데이터 ==========
    
    def get_market_data(self) -> Dict[str, Any]:
        """
        Market Regime Analyst에 필요한 시장 데이터
        
        Returns:
            {
                'vix': 15.2,
                'vkospi': 18.5,
                'kospi': 2650,
                'kospi_vs_ma20': 1.02,
                'kospi_vs_ma60': 1.05,
                'kospi_from_high': -5.2,
                'sp500': 5200,
                'sp500_vs_ma20': 1.03,
                'sp500_vs_ma60': 1.08,
                'kospi_advancers': 650,
                'kospi_decliners': 500,
                'breadth_ratio': 1.3,
                'us_10y': 4.25,
                'usd_krw': 1320
            }
        """
        market_data = {}
        
        try:
            # Yahoo Finance 데이터
            vix = yf.Ticker("^VIX").history(period="1d")['Close'].iloc[-1]
            kospi = yf.Ticker("^KS11").history(period="100d")
            sp500 = yf.Ticker("^GSPC").history(period="100d")
            
            market_data['vix'] = round(vix, 2)
            
            # 코스피 데이터
            kospi_price = kospi['Close'].iloc[-1]
            kospi_ma20 = kospi['Close'].iloc[-20:].mean()
            kospi_ma60 = kospi['Close'].iloc[-60:].mean()
            kospi_high = kospi['Close'].max()
            
            market_data['kospi'] = int(kospi_price)
            market_data['kospi_vs_ma20'] = round(kospi_price / kospi_ma20, 3)
            market_data['kospi_vs_ma60'] = round(kospi_price / kospi_ma60, 3)
            market_data['kospi_from_high'] = round((kospi_price / kospi_high - 1) * 100, 1)
            
            # S&P 500 데이터
            sp500_price = sp500['Close'].iloc[-1]
            sp500_ma20 = sp500['Close'].iloc[-20:].mean()
            sp500_ma60 = sp500['Close'].iloc[-60:].mean()
            
            market_data['sp500'] = int(sp500_price)
            market_data['sp500_vs_ma20'] = round(sp500_price / sp500_ma20, 3)
            market_data['sp500_vs_ma60'] = round(sp500_price / sp500_ma60, 3)
            
            # 시장 폭
            breadth = self.breadth_calc.calculate_kospi_breadth()
            market_data['kospi_advancers'] = breadth['advancers']
            market_data['kospi_decliners'] = breadth['decliners']
            market_data['breadth_ratio'] = breadth['breadth_ratio']
            
            # 환율 (선택)
            try:
                usdkrw = yf.Ticker("USDKRW=X").history(period="1d")['Close'].iloc[-1]
                market_data['usd_krw'] = round(usdkrw, 2)
            except:
                market_data['usd_krw'] = None
            
            market_data['timestamp'] = datetime.now().isoformat()
            
        except Exception as e:
            print(f"❌ Market data collection failed: {e}")
        
        return market_data
    
    # ========== Sector Scout용 데이터 ==========
    
    def get_sectors_data(self, sectors: List[str] = None) -> List[Dict[str, Any]]:
        """
        Sector Scout에 필요한 섹터 데이터
        
        Args:
            sectors: 분석할 섹터 리스트
                (예: ['반도체', '방산', '2차전지'])
        
        Returns:
            섹터별 데이터 리스트
        """
        if sectors is None:
            sectors = ['반도체', '방산', '2차전지', '바이오', 'IT']
        
        sectors_data = []
        
        for sector in sectors:
            try:
                sector_info = self._get_sector_info(sector)
                if sector_info:
                    sectors_data.append(sector_info)
            except Exception as e:
                print(f"⚠️ Sector data fetch failed for {sector}: {e}")
        
        return sectors_data
    
    def _get_sector_info(self, sector: str) -> Optional[Dict[str, Any]]:
        """섹터 정보 조회"""
        # TODO: 실제 섹터 종목 매핑 필요
        # 현재는 샘플 데이터
        
        sector_tickers = {
            '반도체': ['005930', '000660', '006400'],
            '방산': ['012450', '000880', '047810'],
            '2차전지': ['066570', '068270', '247540'],
            '바이오': ['215600', '207940', '086900'],
            'IT': ['005380', '192040', '017800']
        }
        
        tickers = sector_tickers.get(sector, [])
        
        # 이 섹터의 종목들 데이터 수집
        supply_demand = {}
        news_count = 0
        disclosure_count = 0
        
        for ticker in tickers:
            try:
                # 수급 정보
                supply = self.naver_scraper.get_supply_demand(ticker, days=5)
                if supply.get('data'):
                    total_inst = sum(d['inst_net'] for d in supply['data'])
                    total_foreign = sum(d['foreign_net'] for d in supply['data'])
                    supply_demand[ticker] = {
                        'inst_5d': total_inst,
                        'foreign_5d': total_foreign
                    }
                
                # 뉴스
                news = self.naver_scraper.get_news(ticker, limit=5)
                news_count += len(news)
                
                # 공시
                disclosure = self.naver_scraper.get_disclosure(ticker, days=7)
                disclosure_count += len(disclosure)
            except:
                pass
        
        # 섹터 집계
        total_inst = sum(v['inst_5d'] for v in supply_demand.values())
        total_foreign = sum(v['foreign_5d'] for v in supply_demand.values())
        
        return {
            'sector': sector,
            'volume_change_20d': 1.5,  # TODO: 계산 필요
            'foreign_net_buy_5d': round(total_foreign / 100000000),  # 억 단위
            'inst_net_buy_5d': round(total_inst / 100000000),
            'price_change_20d': 5.0,  # TODO: 계산 필요
            'ma20_slope': 0.4,  # TODO: 계산 필요
            'new_high_stocks': 2,  # TODO: 실시간 계산 필요
            'news_count_7d': news_count,
            'policy_keywords': [],  # TODO: 뉴스에서 추출
            'disclosure_count': disclosure_count,
            'duration': 10  # TODO: 테마 지속 기간 계산 필요
        }
    
    # ========== Stock Screener용 데이터 ==========
    
    def get_stock_data(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Stock Screener에 필요한 단일 종목 데이터
        
        Args:
            ticker: 종목 코드 (예: '005930')
        
        Returns:
            종목 상세 데이터
        """
        try:
            # 종목 개요 (네이버)
            overview = self.naver_scraper.get_stock_overview(ticker)
            
            if not overview:
                return None
            
            # 기술적 지표 (Yahoo Finance)
            stock = yf.Ticker(ticker)
            hist = stock.history(period="180d")
            
            if hist.empty:
                return None
            
            # MA, ATR 계산
            close = hist['Close']
            ma20 = close.iloc[-20:].mean()
            ma60 = close.iloc[-60:].mean()
            
            # ATR 계산
            high = hist['High']
            low = hist['Low']
            tr = (high - low).max()
            atr = tr / ma20 * 100  # 백분율
            
            # 수급 정보
            supply = self.naver_scraper.get_supply_demand(ticker, days=5)
            
            return {
                'ticker': ticker,
                'name': overview.get('name'),
                'sector': self._get_sector_by_ticker(ticker),
                
                # 가격 정보
                'current_price': overview.get('current_price'),
                'ma20': int(ma20),
                'ma60': int(ma60),
                'atr_20d': int(tr * 100),  # 원 단위
                'volatility': round(hist['Close'].pct_change().std() * 100, 1),
                
                # 9요소 점수 (TODO: 실제 계산 필요)
                'flow_score': 75,
                'cycle_fit': True,
                'quality_score': 80,
                'governance_score': 70,
                'narrative_score': 65,
                'risk_score': 20,
                'time_fit': True,
                'value_score': overview.get('per', 0) if overview.get('per', 0) > 0 else 60,
                
                # PER/PBR
                'per': overview.get('per', 0),
                'pbr': overview.get('pbr', 0),
                
                # 수급
                'supply_demand': supply,
                
                # 뉴스
                'news_count_7d': len(self.naver_scraper.get_news(ticker, limit=20)),
                'disclosure_count': len(self.naver_scraper.get_disclosure(ticker, days=7))
            }
        
        except Exception as e:
            print(f"❌ Stock data fetch failed for {ticker}: {e}")
            return None
    
    # ========== Trade Plan Builder용 데이터 ==========
    
    def get_trade_data(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Trade Plan Builder에 필요한 거래 계획 데이터
        
        Args:
            ticker: 종목 코드
        
        Returns:
            거래 계획 관련 데이터
        """
        stock_data = self.get_stock_data(ticker)
        if not stock_data:
            return None
        
        # 지지/저항선 (Yahoo Finance 데이터로 계산)
        stock = yf.Ticker(ticker)
        hist = stock.history(period="60d")
        
        if hist.empty:
            return None
        
        # 고점/저점 계산
        high_52w = hist['High'].max()
        low_52w = hist['Low'].min()
        mid_point = (high_52w + low_52w) / 2
        
        return {
            'ticker': ticker,
            'current_price': stock_data['current_price'],
            'atr': stock_data['atr_20d'],
            'volatility': stock_data['volatility'],
            'support_levels': [
                int(low_52w),
                int(low_52w + (mid_point - low_52w) * 0.33)
            ],
            'resistance_levels': [
                int(high_52w - (high_52w - mid_point) * 0.33),
                int(high_52w)
            ],
            'ma20': stock_data['ma20'],
            'ma60': stock_data['ma60'],
            'risk_score': stock_data['risk_score']
        }
    
    # ========== Devil's Advocate용 데이터 ==========
    
    def get_valuation_data(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Devil's Advocate에 필요한 밸류에이션 기준 데이터
        
        Args:
            ticker: 종목 코드
        
        Returns:
            {
                'ticker': '005930',
                'per': 8.5,
                'pbr': 1.2,
                'sector_avg_per': 12.5,
                'sector': '반도체',
                'price_gap': 1.15  # 현재가 대비 이격도
            }
        """
        overview = self.naver_scraper.get_stock_overview(ticker)
        
        if not overview:
            return None
        
        sector = self._get_sector_by_ticker(ticker)
        
        return {
            'ticker': ticker,
            'per': overview.get('per', 0),
            'pbr': overview.get('pbr', 0),
            'sector': sector,
            'sector_avg_per': self._get_sector_avg_per(sector),
            'price_gap': round(overview.get('current_price', 0) / overview.get('per', 1) if overview.get('per') else 1, 2)
        }
    
    # ========== 헬퍼 함수 ==========
    
    def _get_sector_by_ticker(self, ticker: str) -> str:
        """티커로 섹터 조회"""
        sector_map = {
            '005930': '반도체',
            '000660': '반도체',
            '006400': '반도체',
            '012450': '방산',
            '066570': '2차전지',
            '215600': '바이오',
            '005380': 'IT'
        }
        return sector_map.get(ticker, 'Unknown')
    
    def _get_sector_avg_per(self, sector: str) -> float:
        """섹터 평균 PER"""
        sector_avg = {
            '반도체': 12.5,
            '방산': 18.5,
            '2차전지': 25.0,
            '바이오': 30.5,
            'IT': 22.0
        }
        return sector_avg.get(sector, 20.0)


# 테스트
if __name__ == '__main__':
    provider = AgentDataProviderV2()
    
    print("=" * 60)
    print("Agent Data Provider V2 테스트")
    print("=" * 60)
    
    # 1. 시장 데이터
    print("\n[1] Market Regime Analyst용 시장 데이터")
    market = provider.get_market_data()
    print(f"  VIX: {market.get('vix')}")
    print(f"  코스피: {market.get('kospi')}")
    print(f"  상승/하락 비율: {market.get('breadth_ratio')}")
    
    # 2. 섹터 데이터
    print("\n[2] Sector Scout용 섹터 데이터")
    sectors = provider.get_sectors_data(['반도체'])
    for s in sectors:
        print(f"  {s['sector']}: 뉴스 {s['news_count_7d']}건, 공시 {s['disclosure_count']}건")
    
    # 3. 종목 데이터
    print("\n[3] Stock Screener용 종목 데이터")
    stock = provider.get_stock_data('005930')
    if stock:
        print(f"  {stock['name']}: {stock['current_price']}원")
        print(f"  PER: {stock['per']}, PBR: {stock['pbr']}")
    
    # 4. 거래 데이터
    print("\n[4] Trade Plan Builder용 거래 데이터")
    trade = provider.get_trade_data('005930')
    if trade:
        print(f"  현재가: {trade['current_price']}원")
        print(f"  지지선: {trade['support_levels']}")
        print(f"  저항선: {trade['resistance_levels']}")
    
    # 5. 밸류에이션 데이터
    print("\n[5] Devil's Advocate용 밸류에이션 데이터")
    val = provider.get_valuation_data('005930')
    if val:
        print(f"  PER: {val['per']} (섹터평균: {val['sector_avg_per']})")
