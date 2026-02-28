"""
한국거래소(KRX) Open API 래퍼
주식 시세 조회 서비스
"""

import requests
import os
import time
from typing import Optional, List, Dict
from datetime import datetime, timedelta

class KRXStockAPI:
    """한국거래소 Open API 래퍼 클래스"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('KRX_API_KEY')
        self.base_url = "http://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd"
        self.rate_limit_delay = 0.3  # 요청 간 대기 시간 (초)
    
    def get_current_price(self, ticker: str) -> dict:
        """
        주식 현재가 조회 (20분 지연)
        
        Args:
            ticker: 종목코드 (6자리, 예: '005930')
        
        Returns:
            {
                'ticker': '005930',
                'name': '삼성전자',
                'price': 75000,
                'change': 1.5,
                'volume': 12345678,
                'high': 76000,
                'low': 74500,
                'open': 75500
            }
        """
        try:
            # Rate limit 방지: 0.3초 대기
            time.sleep(0.3)
            
            # KRX API 파라미터
            params = {
                'bld': 'dbms/MDC/STAT/standard/MDCSTAT01501',
                'locale': 'ko_KR',
                'isuCd': ticker,
                'share': '1',
                'money': '1',
                'csvxls_isNo': 'false'
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0',
                'Referer': 'http://data.krx.co.kr'
            }
            
            response = requests.get(self.base_url, params=params, headers=headers, timeout=10)
            
            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}: {response.text}")
            
            data = response.json()
            
            # 데이터 확인
            if not data.get('output'):
                raise Exception("No data returned")
            
            output = data['output'][0] if isinstance(data['output'], list) else data['output']
            
            # 가격 파싱 (쉼표 제거)
            def parse_price(value):
                if isinstance(value, str):
                    return float(value.replace(',', ''))
                return float(value)
            
            current_price = parse_price(output.get('TDD_CLSPRC', 0))
            open_price = parse_price(output.get('TDD_OPNPRC', 0))
            high_price = parse_price(output.get('TDD_HGPRC', 0))
            low_price = parse_price(output.get('TDD_LWPRC', 0))
            volume = int(parse_price(output.get('ACC_TRDVOL', 0)))
            
            # 등락률 계산
            prev_price = parse_price(output.get('FLUC_RT', 0))
            if prev_price == 0 and open_price > 0:
                change = ((current_price - open_price) / open_price) * 100
            else:
                change = prev_price
            
            return {
                'ticker': ticker,
                'name': output.get('ISU_ABBRV', ''),
                'price': current_price,
                'change': change,
                'volume': volume,
                'high': high_price,
                'low': low_price,
                'open': open_price
            }
            
        except Exception as e:
            print(f"❌ {ticker} 조회 실패: {e}")
            raise
    
    def get_daily_price(self, ticker: str, target_date: str) -> Optional[Dict]:
        """
        특정 날짜의 일별 시세 조회 (KRX API 제약: 특정 일자 기준만 조회 가능)
        
        Args:
            ticker: 종목코드 (6자리, 예: '079550')
            target_date: 조회 날짜 (YYYYMMDD 또는 YYYY-MM-DD), 거래일만 가능
        
        Returns:
            {
                'ticker': '079550',
                'date': '2024-01-15',
                'name': 'LIG넥스원',
                'open': 123000,
                'high': 125000,
                'low': 122000,
                'close': 124000,
                'volume': 1234567,
                'source': 'KRX'
            } 또는 None (거래 없는 날짜)
        
        Note:
            KRX API는 특정 일자 기준으로만 데이터 제공합니다.
            기간 조회는 불가능하므로, 120일치 데이터는 
            수집: collect_historical_prices.py 참조
            자동갱신: scheduler.py의 매일 갱신 로직 참조
        """
        try:
            # 날짜 형식 변환: YYYY-MM-DD → YYYYMMDD
            if isinstance(target_date, str) and '-' in target_date:
                target_date = target_date.replace('-', '')
            
            # Rate limit 방지
            time.sleep(self.rate_limit_delay)
            
            # KRX API 파라미터
            params = {
                'bld': 'dbms/MDC/STAT/standard/MDCSTAT01501',
                'locale': 'ko_KR',
                'isuCd': ticker,
                'share': '1',
                'money': '1',
                'csvxls_isNo': 'false'
                # 참고: 기간 조회 파라미터(trdDd, strtDd 등)는 API에서 지원하지 않음
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                'Referer': 'http://data.krx.co.kr'
            }
            
            response = requests.get(self.base_url, params=params, headers=headers, timeout=10)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            if not data.get('output'):
                return None
            
            output = data['output'][0] if isinstance(data['output'], list) else data['output']
            
            # 가격 파싱
            def parse_price(value):
                if isinstance(value, str):
                    return float(value.replace(',', ''))
                return float(value) if value else 0
            
            close_price = parse_price(output.get('TDD_CLSPRC', 0))
            open_price = parse_price(output.get('TDD_OPNPRC', 0))
            high_price = parse_price(output.get('TDD_HGPRC', 0))
            low_price = parse_price(output.get('TDD_LWPRC', 0))
            volume = int(parse_price(output.get('ACC_TRDVOL', 0)))
            
            # 조회 날짜를 YYYY-MM-DD 형식으로 변환
            date_obj = output.get('TDD_CLSPRC_DATE') or output.get('BAS_DD')
            if date_obj:
                try:
                    date_formatted = datetime.strptime(str(date_obj), '%Y%m%d').strftime('%Y-%m-%d')
                except:
                    date_formatted = target_date if len(target_date) == 8 else target_date
                    date_formatted = f"{date_formatted[:4]}-{date_formatted[4:6]}-{date_formatted[6:8]}"
            else:
                date_formatted = target_date if len(target_date) == 8 else target_date
                date_formatted = f"{date_formatted[:4]}-{date_formatted[4:6]}-{date_formatted[6:8]}"
            
            return {
                'ticker': ticker,
                'date': date_formatted,
                'name': output.get('ISU_ABBRV', ''),
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price,
                'volume': volume,
                'source': 'KRX'
            }
            
        except Exception as e:
            print(f"⚠️  {ticker} {target_date} 조회 실패: {e}")
            return None
    
    def get_price_range(self, ticker: str, start_date: str, end_date: str) -> List[Dict]:
        """
        기간 내 거래일의 시세 조회 (반복 호출을 통한 구현)
        
        Args:
            ticker: 종목코드
            start_date: 시작 날짜 (YYYY-MM-DD)
            end_date: 종료 날짜 (YYYY-MM-DD)
        
        Returns:
            [{'ticker': '079550', 'date': '2024-01-15', 'close': 124000, ...}, ...]
        
        Note:
            KRX API는 특정 일자만 지원하므로, 
            실제로는 scheduler에서 매일 어제 시세를 추가하는 방식으로
            120일 데이터를 축적하는 것을 권장합니다.
            초기 데이터는 collect_historical_prices.py를 실행하세요.
        """
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        result = []
        current = start
        
        # 주말/공휴일 제외 (평일만 조회)
        skip_days = 0
        while current <= end:
            # 0=월~4=금, 5=토, 6=일
            if current.weekday() < 5:  # 평일만
                daily = self.get_daily_price(ticker, current.strftime('%Y-%m-%d'))
                if daily:
                    result.append(daily)
                    skip_days = 0
                else:
                    skip_days += 1
                    if skip_days > 5:  # 5일 연속 실패 시 중단
                        break
            
            current += timedelta(days=1)
        
        return sorted(result, key=lambda x: x['date'])


if __name__ == "__main__":
    # 테스트
    from dotenv import load_dotenv
    load_dotenv()
    
    api = KRXStockAPI()
    
    print("=" * 60)
    print("한국거래소 API 테스트")
    print("=" * 60)
    
    # 삼성전자 조회
    try:
        samsung = api.get_current_price('005930')
        print(f"\n✅ {samsung['name']}: {samsung['price']:,}원 ({samsung['change']:+.2f}%)")
        print(f"   거래량: {samsung['volume']:,}주")
        print(f"   고가: {samsung['high']:,}원")
        print(f"   저가: {samsung['low']:,}원")
    except Exception as e:
        print(f"\n❌ 에러: {e}")
