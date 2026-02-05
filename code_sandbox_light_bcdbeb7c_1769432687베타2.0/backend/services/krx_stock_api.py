"""
한국거래소(KRX) Open API 래퍼
주식 시세 조회 서비스
"""

import requests
import os
import time
from typing import Optional

class KRXStockAPI:
    """한국거래소 Open API 래퍼 클래스"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('KRX_API_KEY')
        self.base_url = "http://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd"
    
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
