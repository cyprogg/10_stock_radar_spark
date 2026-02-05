"""
한국 주식 기술적 분석 서비스
차트 패턴, 보조지표, 캔들 패턴 분석
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from korea_investment_api import KoreaInvestmentAPI

class TechnicalAnalysisService:
    """
    기술적 분석 종합 서비스
    
    제공 기능:
    1. 이동평균선 (MA5, MA20, MA60, MA120)
    2. 볼린저 밴드
    3. RSI (Relative Strength Index)
    4. MACD
    5. 거래량 분석
    6. 캔들 패턴 인식
    7. 지지/저항선
    """
    
    def __init__(self):
        self.api = KoreaInvestmentAPI()
    
    def get_chart_data(self, ticker: str, days: int = 120) -> pd.DataFrame:
        """
        차트 데이터 조회 및 기술적 지표 계산
        
        Args:
            ticker: 종목코드
            days: 조회 일수 (기본 120일)
        
        Returns:
            DataFrame with columns:
            - date, open, high, low, close, volume
            - ma5, ma20, ma60, ma120
            - bb_upper, bb_middle, bb_lower
            - rsi
            - macd, macd_signal, macd_hist
        """
        # 일봉 데이터 조회
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=days+60)).strftime('%Y%m%d')
        
        data = self.api.get_daily_price(ticker, start_date, end_date)
        
        if not data:
            raise ValueError(f"데이터 조회 실패: {ticker}")
        
        # DataFrame 생성
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date').reset_index(drop=True)
        
        # 기술적 지표 계산
        df = self._calculate_moving_averages(df)
        df = self._calculate_bollinger_bands(df)
        df = self._calculate_rsi(df)
        df = self._calculate_macd(df)
        df = self._calculate_volume_indicators(df)
        
        return df.tail(days).reset_index(drop=True)
    
    def _calculate_moving_averages(self, df: pd.DataFrame) -> pd.DataFrame:
        """이동평균선 계산"""
        df['ma5'] = df['close'].rolling(window=5).mean()
        df['ma20'] = df['close'].rolling(window=20).mean()
        df['ma60'] = df['close'].rolling(window=60).mean()
        df['ma120'] = df['close'].rolling(window=120).mean()
        return df
    
    def _calculate_bollinger_bands(self, df: pd.DataFrame, period: int = 20) -> pd.DataFrame:
        """볼린저 밴드 계산"""
        df['bb_middle'] = df['close'].rolling(window=period).mean()
        std = df['close'].rolling(window=period).std()
        df['bb_upper'] = df['bb_middle'] + (std * 2)
        df['bb_lower'] = df['bb_middle'] - (std * 2)
        return df
    
    def _calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """RSI 계산"""
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        return df
    
    def _calculate_macd(self, df: pd.DataFrame) -> pd.DataFrame:
        """MACD 계산"""
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = exp1 - exp2
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        df['macd_hist'] = df['macd'] - df['macd_signal']
        return df
    
    def _calculate_volume_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """거래량 지표 계산"""
        df['volume_ma5'] = df['volume'].rolling(window=5).mean()
        df['volume_ma20'] = df['volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['volume'] / df['volume_ma20']
        return df
    
    def analyze_trend(self, df: pd.DataFrame) -> Dict:
        """
        추세 분석
        
        Returns:
            {
                'short_trend': 'UP/DOWN/NEUTRAL',  # MA5 vs MA20
                'mid_trend': 'UP/DOWN/NEUTRAL',     # MA20 vs MA60
                'long_trend': 'UP/DOWN/NEUTRAL',    # MA60 vs MA120
                'ma_arrangement': 'GOLDEN/DEAD/NEUTRAL',
                'support': float,  # 지지선
                'resistance': float  # 저항선
            }
        """
        latest = df.iloc[-1]
        
        # 단기 추세 (MA5 vs MA20)
        if latest['ma5'] > latest['ma20']:
            short_trend = 'UP'
        elif latest['ma5'] < latest['ma20']:
            short_trend = 'DOWN'
        else:
            short_trend = 'NEUTRAL'
        
        # 중기 추세 (MA20 vs MA60)
        if latest['ma20'] > latest['ma60']:
            mid_trend = 'UP'
        elif latest['ma20'] < latest['ma60']:
            mid_trend = 'DOWN'
        else:
            mid_trend = 'NEUTRAL'
        
        # 장기 추세 (MA60 vs MA120)
        if pd.notna(latest['ma120']):
            if latest['ma60'] > latest['ma120']:
                long_trend = 'UP'
            elif latest['ma60'] < latest['ma120']:
                long_trend = 'DOWN'
            else:
                long_trend = 'NEUTRAL'
        else:
            long_trend = 'NEUTRAL'
        
        # 이평선 정배열/역배열
        if latest['ma5'] > latest['ma20'] > latest['ma60']:
            ma_arrangement = 'GOLDEN'
        elif latest['ma5'] < latest['ma20'] < latest['ma60']:
            ma_arrangement = 'DEAD'
        else:
            ma_arrangement = 'NEUTRAL'
        
        # 지지선/저항선 (최근 20일 기준)
        recent = df.tail(20)
        support = recent['low'].min()
        resistance = recent['high'].max()
        
        return {
            'short_trend': short_trend,
            'mid_trend': mid_trend,
            'long_trend': long_trend,
            'ma_arrangement': ma_arrangement,
            'support': support,
            'resistance': resistance
        }
    
    def analyze_momentum(self, df: pd.DataFrame) -> Dict:
        """
        모멘텀 분석 (RSI, MACD)
        
        Returns:
            {
                'rsi': float,
                'rsi_signal': 'OVERBOUGHT/OVERSOLD/NEUTRAL',
                'macd_signal': 'BULLISH/BEARISH/NEUTRAL',
                'volume_signal': 'SURGE/NORMAL/LOW'
            }
        """
        latest = df.iloc[-1]
        
        # RSI 신호
        rsi = latest['rsi']
        if rsi > 70:
            rsi_signal = 'OVERBOUGHT'  # 과매수
        elif rsi < 30:
            rsi_signal = 'OVERSOLD'  # 과매도
        else:
            rsi_signal = 'NEUTRAL'
        
        # MACD 신호
        if latest['macd'] > latest['macd_signal'] and latest['macd_hist'] > 0:
            macd_signal = 'BULLISH'  # 상승
        elif latest['macd'] < latest['macd_signal'] and latest['macd_hist'] < 0:
            macd_signal = 'BEARISH'  # 하락
        else:
            macd_signal = 'NEUTRAL'
        
        # 거래량 신호
        if latest['volume_ratio'] > 1.5:
            volume_signal = 'SURGE'  # 급증
        elif latest['volume_ratio'] < 0.7:
            volume_signal = 'LOW'  # 저조
        else:
            volume_signal = 'NORMAL'
        
        return {
            'rsi': rsi,
            'rsi_signal': rsi_signal,
            'macd_signal': macd_signal,
            'volume_signal': volume_signal
        }
    
    def detect_candle_patterns(self, df: pd.DataFrame) -> List[str]:
        """
        캔들 패턴 인식
        
        Returns:
            ['DOJI', 'HAMMER', 'SHOOTING_STAR', ...]
        """
        patterns = []
        
        if len(df) < 3:
            return patterns
        
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        open_price = latest['open']
        close = latest['close']
        high = latest['high']
        low = latest['low']
        
        body = abs(close - open_price)
        upper_shadow = high - max(open_price, close)
        lower_shadow = min(open_price, close) - low
        
        # 도지 (Doji)
        if body < (high - low) * 0.1:
            patterns.append('DOJI')
        
        # 망치형 (Hammer)
        if (lower_shadow > body * 2) and (upper_shadow < body * 0.5) and close > open_price:
            patterns.append('HAMMER')
        
        # 역망치형 (Inverted Hammer)
        if (upper_shadow > body * 2) and (lower_shadow < body * 0.5) and close > open_price:
            patterns.append('INVERTED_HAMMER')
        
        # 유성형 (Shooting Star)
        if (upper_shadow > body * 2) and (lower_shadow < body * 0.5) and close < open_price:
            patterns.append('SHOOTING_STAR')
        
        # 강세 장악형 (Bullish Engulfing)
        if (prev['close'] < prev['open'] and 
            close > open_price and 
            close > prev['open'] and 
            open_price < prev['close']):
            patterns.append('BULLISH_ENGULFING')
        
        # 약세 장악형 (Bearish Engulfing)
        if (prev['close'] > prev['open'] and 
            close < open_price and 
            close < prev['open'] and 
            open_price > prev['close']):
            patterns.append('BEARISH_ENGULFING')
        
        return patterns
    
    def get_comprehensive_analysis(self, ticker: str) -> Dict:
        """
        종합 기술적 분석
        
        Returns:
            {
                'ticker': str,
                'current_price': float,
                'chart_data': DataFrame,
                'trend': {...},
                'momentum': {...},
                'patterns': [...],
                'summary': str,
                'recommendation': 'BUY/SELL/HOLD'
            }
        """
        # 차트 데이터 조회
        df = self.get_chart_data(ticker, days=120)
        
        # 현재가
        current = self.api.get_current_price(ticker)
        
        # 분석
        trend = self.analyze_trend(df)
        momentum = self.analyze_momentum(df)
        patterns = self.detect_candle_patterns(df)
        
        # 종합 판단
        recommendation = self._make_recommendation(trend, momentum, patterns)
        summary = self._generate_summary(current['name'], trend, momentum, patterns, recommendation)
        
        return {
            'ticker': ticker,
            'name': current['name'],
            'current_price': current['price'],
            'change': current['change'],
            'chart_data': df,
            'trend': trend,
            'momentum': momentum,
            'patterns': patterns,
            'summary': summary,
            'recommendation': recommendation
        }
    
    def _make_recommendation(self, trend: Dict, momentum: Dict, patterns: List[str]) -> str:
        """매매 추천"""
        score = 0
        
        # 추세 점수
        if trend['ma_arrangement'] == 'GOLDEN':
            score += 3
        elif trend['ma_arrangement'] == 'DEAD':
            score -= 3
        
        if trend['short_trend'] == 'UP':
            score += 2
        elif trend['short_trend'] == 'DOWN':
            score -= 2
        
        # 모멘텀 점수
        if momentum['rsi_signal'] == 'OVERSOLD':
            score += 2
        elif momentum['rsi_signal'] == 'OVERBOUGHT':
            score -= 2
        
        if momentum['macd_signal'] == 'BULLISH':
            score += 2
        elif momentum['macd_signal'] == 'BEARISH':
            score -= 2
        
        # 캔들 패턴 점수
        bullish_patterns = ['HAMMER', 'INVERTED_HAMMER', 'BULLISH_ENGULFING']
        bearish_patterns = ['SHOOTING_STAR', 'BEARISH_ENGULFING']
        
        for pattern in patterns:
            if pattern in bullish_patterns:
                score += 1
            elif pattern in bearish_patterns:
                score -= 1
        
        # 최종 판단
        if score >= 5:
            return 'BUY'
        elif score <= -5:
            return 'SELL'
        else:
            return 'HOLD'
    
    def _generate_summary(self, name: str, trend: Dict, momentum: Dict, patterns: List[str], recommendation: str) -> str:
        """분석 요약"""
        summary = f"{name} 기술적 분석 요약:\n\n"
        
        # 추세
        summary += f"📈 추세 분석:\n"
        summary += f"- 단기: {trend['short_trend']}\n"
        summary += f"- 중기: {trend['mid_trend']}\n"
        summary += f"- 장기: {trend['long_trend']}\n"
        summary += f"- 이평선 배열: {trend['ma_arrangement']}\n"
        summary += f"- 지지선: {trend['support']:,}원\n"
        summary += f"- 저항선: {trend['resistance']:,}원\n\n"
        
        # 모멘텀
        summary += f"💪 모멘텀 분석:\n"
        summary += f"- RSI: {momentum['rsi']:.1f} ({momentum['rsi_signal']})\n"
        summary += f"- MACD: {momentum['macd_signal']}\n"
        summary += f"- 거래량: {momentum['volume_signal']}\n\n"
        
        # 캔들 패턴
        if patterns:
            summary += f"🕯️ 캔들 패턴: {', '.join(patterns)}\n\n"
        
        # 추천
        if recommendation == 'BUY':
            summary += f"✅ 종합 판단: 매수 고려 (추세+모멘텀 양호)"
        elif recommendation == 'SELL':
            summary += f"🚫 종합 판단: 매도 고려 (추세+모멘텀 악화)"
        else:
            summary += f"⏸️ 종합 판단: 관망 (추가 신호 대기)"
        
        return summary


# ========== 사용 예제 ==========

if __name__ == "__main__":
    service = TechnicalAnalysisService()
    
    # 예제 1: 삼성전자 종합 분석
    print("=" * 80)
    print("삼성전자 (005930) 종합 기술적 분석")
    print("=" * 80)
    
    analysis = service.get_comprehensive_analysis('005930')
    
    print(f"\n현재가: {analysis['current_price']:,}원 ({analysis['change']:+.2f}%)\n")
    print(analysis['summary'])
    
    print("\n" + "=" * 80)
    print(f"추천: {analysis['recommendation']}")
    print("=" * 80)
    
    # 차트 데이터 샘플 (최근 5일)
    print("\n최근 5일 차트 데이터:")
    print(analysis['chart_data'][['date', 'close', 'ma20', 'rsi', 'volume']].tail())
