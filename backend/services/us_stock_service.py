"""
미국 주식 데이터 수집 서비스
yfinance + Alpha Vantage 통합
"""

import yfinance as yf
import requests
import os
from typing import Optional, List, Dict
from datetime import datetime

class USStockService:
    """
    미국 주식 데이터 수집 통합 서비스
    
    우선순위:
    1. yfinance (무료, 제한 없음)
    2. Alpha Vantage (무료 25회/일, 실시간)
    """
    
    def __init__(self, alpha_vantage_key: Optional[str] = None):
        self.alpha_vantage_key = alpha_vantage_key or os.getenv('ALPHA_VANTAGE_KEY')
        self.alpha_vantage_base = "https://www.alphavantage.co/query"
    
    def get_current_price_yf(self, ticker: str) -> dict:
        """
        yfinance로 현재가 조회
        (15분 지연, 무료 무제한)
        
        Args:
            ticker: 티커 심볼 (예: 'AAPL', 'MSFT')
        
        Returns:
            {
                'ticker': 'AAPL',
                'name': 'Apple Inc.',
                'price': 185.50,
                'change': 1.2,
                'volume': 45678900,
                'high': 186.00,
                'low': 184.50,
                'open': 185.00,
                'market_cap': 2900000000000
            }
        """
        stock = yf.Ticker(ticker)
        info = stock.info
        
        return {
            'ticker': ticker,
            'name': info.get('longName', ticker),
            'price': info.get('currentPrice', info.get('regularMarketPrice', 0)),
            'change': info.get('regularMarketChangePercent', 0),
            'volume': info.get('volume', 0),
            'high': info.get('dayHigh', 0),
            'low': info.get('dayLow', 0),
            'open': info.get('open', info.get('regularMarketOpen', 0)),
            'market_cap': info.get('marketCap', 0)
        }
    
    def get_current_price_av(self, symbol: str) -> dict:
        """
        Alpha Vantage로 현재가 조회
        (실시간, 무료 25회/일)
        
        Args:
            symbol: 티커 심볼
        
        Returns:
            동일한 형식의 dict
        """
        if not self.alpha_vantage_key:
            raise ValueError("Alpha Vantage API 키가 설정되지 않았습니다.")
        
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": self.alpha_vantage_key
        }
        
        response = requests.get(self.alpha_vantage_base, params=params)
        response.raise_for_status()
        
        data = response.json()
        quote = data.get('Global Quote', {})
        
        return {
            'ticker': symbol,
            'name': symbol,  # Alpha Vantage는 회사명 미제공
            'price': float(quote.get('05. price', 0)),
            'change': float(quote.get('10. change percent', '0').replace('%', '')),
            'volume': int(quote.get('06. volume', 0)),
            'high': float(quote.get('03. high', 0)),
            'low': float(quote.get('04. low', 0)),
            'open': float(quote.get('02. open', 0)),
            'market_cap': 0
        }
    
    def get_current_price(self, ticker: str, use_alpha_vantage: bool = False) -> dict:
        """
        현재가 조회 (통합 메서드)
        
        Args:
            ticker: 티커 심볼
            use_alpha_vantage: True면 Alpha Vantage 사용 (실시간)
        
        Returns:
            주가 정보 dict
        """
        if use_alpha_vantage and self.alpha_vantage_key:
            return self.get_current_price_av(ticker)
        else:
            return self.get_current_price_yf(ticker)
    
    def get_daily_data(self, ticker: str, period: str = "1mo") -> List[dict]:
        """
        일봉 데이터 조회 (yfinance)
        
        Args:
            ticker: 티커 심볼
            period: 기간 (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        
        Returns:
            [
                {
                    'date': '2024-01-21',
                    'open': 185.0,
                    'high': 186.0,
                    'low': 184.5,
                    'close': 185.5,
                    'volume': 45678900
                },
                ...
            ]
        """
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        
        result = []
        for date, row in df.iterrows():
            result.append({
                'date': date.strftime('%Y-%m-%d'),
                'open': float(row['Open']),
                'high': float(row['High']),
                'low': float(row['Low']),
                'close': float(row['Close']),
                'volume': int(row['Volume'])
            })
        
        return result
    
    def get_multiple_prices(self, tickers: List[str]) -> Dict[str, dict]:
        """
        여러 종목 현재가 일괄 조회
        
        Args:
            tickers: 티커 심볼 리스트 ['AAPL', 'MSFT', 'GOOGL']
        
        Returns:
            {
                'AAPL': {...},
                'MSFT': {...},
                'GOOGL': {...}
            }
        """
        result = {}
        
        for ticker in tickers:
            try:
                result[ticker] = self.get_current_price(ticker)
            except Exception as e:
                print(f"⚠️ {ticker} 조회 실패: {e}")
                result[ticker] = None
        
        return result


# ========== 사용 예제 ==========

if __name__ == "__main__":
    # 서비스 인스턴스 생성
    service = USStockService()
    
    # 예제 1: Apple 현재가 조회 (yfinance)
    print("=" * 50)
    print("예제 1: Apple 현재가 조회 (yfinance)")
    print("=" * 50)
    
    aapl = service.get_current_price('AAPL')
    print(f"종목명: {aapl['name']}")
    print(f"현재가: ${aapl['price']:.2f}")
    print(f"등락률: {aapl['change']:+.2f}%")
    print(f"거래량: {aapl['volume']:,}주")
    print(f"시가총액: ${aapl['market_cap']:,}")
    print()
    
    # 예제 2: Microsoft 현재가 조회
    print("=" * 50)
    print("예제 2: Microsoft 현재가 조회")
    print("=" * 50)
    
    msft = service.get_current_price('MSFT')
    print(f"종목명: {msft['name']}")
    print(f"현재가: ${msft['price']:.2f}")
    print(f"등락률: {msft['change']:+.2f}%")
    print()
    
    # 예제 3: 여러 종목 일괄 조회
    print("=" * 50)
    print("예제 3: 주요 기술주 일괄 조회")
    print("=" * 50)
    
    tech_stocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA']
    prices = service.get_multiple_prices(tech_stocks)
    
    for ticker, data in prices.items():
        if data:
            print(f"{ticker}: ${data['price']:.2f} ({data['change']:+.2f}%)")
    print()
    
    # 예제 4: 방산 주요 종목
    print("=" * 50)
    print("예제 4: 방산 섹터 주요 종목")
    print("=" * 50)
    
    defense_stocks = ['LMT', 'RTX', 'BA', 'NOC', 'GD']
    defense_prices = service.get_multiple_prices(defense_stocks)
    
    for ticker, data in defense_prices.items():
        if data:
            print(f"{ticker}: ${data['price']:.2f} ({data['change']:+.2f}%)")
    print()
    
    # 예제 5: Lockheed Martin 일봉 데이터 (최근 5일)
    print("=" * 50)
    print("예제 5: Lockheed Martin 일봉 데이터 (최근 5일)")
    print("=" * 50)
    
    daily = service.get_daily_data('LMT', period='5d')
    for item in daily:
        print(f"{item['date']}: 시가 ${item['open']:.2f}, 종가 ${item['close']:.2f}, 거래량 {item['volume']:,}")
    print()
    
    # 예제 6: Alpha Vantage 사용 (실시간, API 키 필요)
    print("=" * 50)
    print("예제 6: Alpha Vantage로 실시간 조회")
    print("=" * 50)
    
    if service.alpha_vantage_key:
        try:
            aapl_av = service.get_current_price('AAPL', use_alpha_vantage=True)
            print(f"AAPL (실시간): ${aapl_av['price']:.2f}")
        except Exception as e:
            print(f"Alpha Vantage 조회 실패: {e}")
    else:
        print("Alpha Vantage API 키가 설정되지 않았습니다.")
        print("환경변수 ALPHA_VANTAGE_KEY를 설정하세요.")
    
    print()
    print("✅ 모든 예제 완료!")
    print("=" * 50)
