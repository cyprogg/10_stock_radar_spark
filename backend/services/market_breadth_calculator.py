"""
시장 폭(Market Breadth) 계산기
상승/하락 종목 비율로 시장의 강도를 판정
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, Any
from datetime import datetime


class MarketBreadthCalculator:
    """시장 폭 계산기"""
    
    def __init__(self):
        self.kospi_url = "https://finance.naver.com/sise/siseIndex.naver?code=KOSPI"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    def calculate_kospi_breadth(self) -> Dict[str, Any]:
        """
        코스피 상승/하락 종목 수 및 시장 폭(Breadth) 계산
        
        Returns:
            {
                'date': '2026-02-21',
                'advancers': 650,           # 상승 종목
                'decliners': 500,           # 하락 종목
                'unchanged': 50,            # 보합 종목
                'breadth_ratio': 1.3,       # 상승/하락 비율
                'advance_decline_ratio': 56.5,  # 상승율 (%)
                'market_strength': 'STRONG'  # STRONG | NEUTRAL | WEAK
            }
        """
        try:
            response = requests.get(self.kospi_url, headers=self.headers, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 상승/하락 정보 추출
            info_elements = soup.select('.data')
            
            advancers = 0
            decliners = 0
            unchanged = 0
            
            # 테이블에서 상승/하락/보합 종목 수 추출
            table = soup.select_one('table.tbl_data')
            if table:
                rows = table.select('tbody tr')
                for row in rows:
                    cells = row.select('td')
                    if len(cells) >= 2:
                        label = cells[0].text.strip()
                        value_str = cells[1].text.strip().replace(',', '')
                        
                        try:
                            value = int(value_str)
                            if '상승' in label or '상' in label:
                                advancers = value
                            elif '하락' in label or '하' in label:
                                decliners = value
                            elif '보합' in label or '변화없음' in label:
                                unchanged = value
                        except:
                            continue
            
            # 계산
            total = advancers + decliners + unchanged
            breadth_ratio = advancers / decliners if decliners > 0 else 0
            advance_ratio = (advancers / total * 100) if total > 0 else 0
            
            # 시장 강도 판정
            if breadth_ratio > 1.2 and advance_ratio > 55:
                strength = "STRONG"
            elif breadth_ratio > 0.8 and advance_ratio > 45:
                strength = "NEUTRAL"
            else:
                strength = "WEAK"
            
            return {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'advancers': advancers,
                'decliners': decliners,
                'unchanged': unchanged,
                'total': total,
                'breadth_ratio': round(breadth_ratio, 2),
                'advance_ratio': round(advance_ratio, 1),
                'market_strength': strength
            }
        
        except Exception as e:
            print(f"❌ 시장 폭 계산 실패: {e}")
            return {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'advancers': 0,
                'decliners': 0,
                'unchanged': 0,
                'total': 0,
                'breadth_ratio': 0,
                'advance_ratio': 0,
                'market_strength': 'UNKNOWN'
            }
    
    def calculate_sector_breadth(self, sector_tickers: list) -> Dict[str, Any]:
        """
        특정 섹터의 시장 폭 계산
        
        Args:
            sector_tickers: 섹터 종목 코드 리스트 (예: ['005930', '000660', ...])
        
        Returns:
            {
                'sector': '반도체',
                'total_stocks': 10,
                'positive': 7,
                'negative': 3,
                'breadth_ratio': 2.33,
                'strength': 'STRONG'
            }
        """
        positive = 0
        negative = 0
        
        for ticker in sector_tickers:
            try:
                url = f"https://finance.naver.com/item/main.nhn?code={ticker}"
                response = requests.get(url, headers=self.headers, timeout=5)
                response.encoding = 'utf-8'
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # 현재가 변동 확인
                change_elem = soup.select_one('.h_item .blind')
                if change_elem:
                    change_text = change_elem.text
                    if '(' in change_text:
                        change_rate = float(change_text.split('(')[1].split('%')[0])
                        if change_rate > 0:
                            positive += 1
                        else:
                            negative += 1
            except:
                continue
        
        total = positive + negative
        breadth_ratio = positive / negative if negative > 0 else 0
        
        if breadth_ratio > 1.5:
            strength = "STRONG"
        elif breadth_ratio > 0.67:
            strength = "NEUTRAL"
        else:
            strength = "WEAK"
        
        return {
            'total_stocks': total,
            'positive': positive,
            'negative': negative,
            'breadth_ratio': round(breadth_ratio, 2),
            'strength': strength,
            'positive_ratio': round(positive / total * 100, 1) if total > 0 else 0
        }


# 테스트
if __name__ == '__main__':
    calc = MarketBreadthCalculator()
    
    # 코스피 시장 폭
    breadth = calc.calculate_kospi_breadth()
    print("=== 코스피 시장 폭 ===")
    print(f"상승: {breadth['advancers']:,} | 하락: {breadth['decliners']:,} | 보합: {breadth['unchanged']:,}")
    print(f"상승/하락 비율: {breadth['breadth_ratio']}")
    print(f"상승률: {breadth['advance_ratio']}%")
    print(f"시장 강도: {breadth['market_strength']}")
    
    # 섹터 시장 폭 (반도체)
    semiconductor = ['005930', '000660', '006400', '035720', '121600']
    sector_breadth = calc.calculate_sector_breadth(semiconductor)
    print("\n=== 반도체 섹터 시장 폭 ===")
    print(f"상승: {sector_breadth['positive']} | 하락: {sector_breadth['negative']}")
    print(f"상승/하락 비율: {sector_breadth['breadth_ratio']}")
    print(f"시장 강도: {sector_breadth['strength']}")
