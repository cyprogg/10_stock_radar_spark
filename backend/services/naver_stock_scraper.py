"""
네이버 금융 웹 크롤러
공식 API 없는 데이터를 크롤링으로 수집
- 종목 정보, 기관/외국인 수급, 뉴스, PER/PBR 등
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import re
import time


class NaverStockScraper:
    """네이버 금융 웹 크롤러"""
    
    def __init__(self):
        self.base_url = "https://finance.naver.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    def get_stock_overview(self, ticker: str) -> Dict[str, Any]:
        """
        종목 개요 조회
        
        Args:
            ticker: 종목 코드 (6자리, 예: 005930)
        
        Returns:
            {
                'ticker': '005930',
                'name': '삼성전자',
                'current_price': 75000,
                'change': 1500,
                'change_rate': 2.0,
                'per': 8.5,
                'pbr': 1.2,
                'dividend_yield': 2.5,
                'market_cap': 450000000000000,  # 450조
                'volume': 12345678,
                'week_52_high': 85000,
                'week_52_low': 65000
            }
        """
        url = f"{self.base_url}/item/main.nhn?code={ticker}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 종목명
            name_elem = soup.select_one('.h_company span.txt')
            name = name_elem.text if name_elem else "Unknown"
            
            # 현재가
            price_elem = soup.select_one('.h_item .blind')
            current_price = 0
            if price_elem:
                current_price = int(price_elem.text.replace(',', ''))
            
            # 변동률 및 변동가
            rate_elems = soup.select('.h_item .blind')
            change = 0
            change_rate = 0.0
            if len(rate_elems) > 1:
                change_str = rate_elems[1].text
                if change_str:
                    change = int(float(change_str.split('(')[0].replace(',', '')))
                    change_rate = float(change_str.split('(')[1].split('%')[0])
            
            # PER/PBR (시세 탭)
            per = self._get_per_pbr(soup, 'per')
            pbr = self._get_per_pbr(soup, 'pbr')
            
            # 거래량
            volume = self._get_volume(soup)
            
            return {
                'ticker': ticker,
                'name': name,
                'current_price': current_price,
                'change': change,
                'change_rate': change_rate,
                'per': per,
                'pbr': pbr,
                'volume': volume,
                'market_cap': 0,  # 별도 계산 필요
                'dividend_yield': 0.0
            }
        
        except Exception as e:
            print(f"❌ 네이버 개요 조회 실패 ({ticker}): {e}")
            return {}
    
    def get_supply_demand(self, ticker: str, days: int = 5) -> Dict[str, Any]:
        """
        기관/외국인/개인 수급 조회 (최근 N일)
        
        Args:
            ticker: 종목 코드
            days: 조회 기간 (기본값: 5일)
        
        Returns:
            {
                'ticker': '005930',
                'period': 5,
                'data': [
                    {
                        'date': '2026-02-21',
                        'inst_net': 50000000,      # 기관 순매수 (원)
                        'foreign_net': -30000000,  # 외국인 순매수 (원)
                        'retail_net': -20000000    # 개인 순매수 (원)
                    },
                    ...
                ]
            }
        """
        url = f"{self.base_url}/item/frgn.nhn?code={ticker}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.content, 'html.parser')
            
            supply_data = []
            
            # 최근 days일의 수급 데이터 추출
            table = soup.select_one('table.type2')
            if table:
                rows = table.select('tbody tr')
                for row in rows[:days]:
                    cells = row.select('td')
                    if len(cells) >= 4:
                        try:
                            date_str = cells[0].text.strip()
                            inst_str = cells[1].text.strip().replace(',', '')
                            foreign_str = cells[2].text.strip().replace(',', '')
                            retail_str = cells[3].text.strip().replace(',', '')
                            
                            supply_data.append({
                                'date': date_str,
                                'inst_net': int(float(inst_str)) if inst_str else 0,
                                'foreign_net': int(float(foreign_str)) if foreign_str else 0,
                                'retail_net': int(float(retail_str)) if retail_str else 0
                            })
                        except:
                            continue
            
            return {
                'ticker': ticker,
                'period': days,
                'data': supply_data
            }
        
        except Exception as e:
            print(f"❌ 네이버 수급 조회 실패 ({ticker}): {e}")
            return {'ticker': ticker, 'period': days, 'data': []}
    
    def get_news(self, ticker: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        종목 관련 뉴스 조회
        
        Args:
            ticker: 종목 코드
            limit: 조회 건수 (기본값: 10)
        
        Returns:
            [
                {
                    'title': '삼성전자, 반도체 사업 호황',
                    'source': '조선일보',
                    'date': '2026-02-21',
                    'url': '...'
                },
                ...
            ]
        """
        url = f"{self.base_url}/item/news.nhn?code={ticker}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.content, 'html.parser')
            
            news_list = []
            
            # 뉴스 목록 추출
            news_items = soup.select('table tbody tr')
            for item in news_items[:limit]:
                cells = item.select('td')
                if len(cells) >= 3:
                    try:
                        title_elem = cells[0].select_one('a')
                        title = title_elem.text.strip() if title_elem else ""
                        
                        source_elem = cells[2].select_one('a')
                        source = source_elem.text.strip() if source_elem else ""
                        
                        date_elem = cells[1]
                        date = date_elem.text.strip() if date_elem else ""
                        
                        if title:
                            news_list.append({
                                'title': title,
                                'source': source,
                                'date': date,
                                'url': self.base_url + title_elem['href'] if title_elem else ""
                            })
                    except:
                        continue
            
            return news_list
        
        except Exception as e:
            print(f"❌ 네이버 뉴스 조회 실패 ({ticker}): {e}")
            return []
    
    def get_disclosure(self, ticker: str, days: int = 7) -> List[Dict[str, Any]]:
        """
        종목 공시 정보 조회 (최근 N일)
        
        Args:
            ticker: 종목 코드
            days: 조회 기간 (기본값: 7일)
        
        Returns:
            [
                {
                    'date': '2026-02-20',
                    'title': '분기보고서',
                    'type': '정기보고',
                    'url': '...'
                },
                ...
            ]
        """
        url = f"{self.base_url}/item/news_notice.nhn?code={ticker}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.content, 'html.parser')
            
            disclosure_list = []
            
            # 공시 목록 추출
            notice_items = soup.select('table tbody tr')
            for item in notice_items[:20]:
                cells = item.select('td')
                if len(cells) >= 2:
                    try:
                        date_elem = cells[0]
                        date = date_elem.text.strip() if date_elem else ""
                        
                        title_elem = cells[1].select_one('a')
                        title = title_elem.text.strip() if title_elem else ""
                        
                        if title and date:
                            # 날짜 필터링
                            date_obj = datetime.strptime(date, '%Y-%m-%d')
                            if (datetime.now() - date_obj).days <= days:
                                disclosure_list.append({
                                    'date': date,
                                    'title': title,
                                    'type': '공시',
                                    'url': title_elem['href'] if title_elem.get('href') else ""
                                })
                    except:
                        continue
            
            return disclosure_list
        
        except Exception as e:
            print(f"❌ 네이버 공시 조회 실패 ({ticker}): {e}")
            return []
    
    def _get_per_pbr(self, soup: BeautifulSoup, metric: str) -> float:
        """PER/PBR 추출"""
        try:
            # 시세 정보 탭에서 추출
            info_elem = soup.select_one('.lside')
            if not info_elem:
                return 0.0
            
            # metric: 'per' 또는 'pbr'
            pattern = f'{metric.upper()}\\s*([\\d.]+)'
            text = info_elem.text
            match = re.search(pattern, text, re.IGNORECASE)
            
            return float(match.group(1)) if match else 0.0
        except:
            return 0.0
    
    def _get_volume(self, soup: BeautifulSoup) -> int:
        """거래량 추출"""
        try:
            # 거래량 정보 추출
            volume_elem = soup.select_one('.h_item span.blind')
            if volume_elem:
                volume_text = volume_elem.text.split('(')[0].replace(',', '')
                return int(float(volume_text))
            return 0
        except:
            return 0


# 테스트
if __name__ == '__main__':
    scraper = NaverStockScraper()
    
    # 삼성전자 종목 정보
    info = scraper.get_stock_overview('005930')
    print("=== 종목 정보 ===")
    print(info)
    
    # 수급 정보
    supply = scraper.get_supply_demand('005930')
    print("\n=== 수급 정보 ===")
    print(supply)
    
    # 뉴스
    news = scraper.get_news('005930', limit=5)
    print("\n=== 뉴스 ===")
    for n in news:
        print(f"  {n['date']} | {n['source']}: {n['title']}")
    
    # 공시
    disclosure = scraper.get_disclosure('005930')
    print("\n=== 최근 공시 ===")
    for d in disclosure:
        print(f"  {d['date']}: {d['title']}")
