"""
NH투자증권 Open API 래퍼
실시간 주가 조회 서비스
"""

import requests
import os
import time
from datetime import datetime, timedelta
from typing import Optional

class NHStockAPI:
    """NH투자증권 Open API 래퍼 클래스"""
    
    def __init__(self, app_key: Optional[str] = None, app_secret: Optional[str] = None):
        self.app_key = app_key or os.getenv('NH_APP_KEY')
        self.app_secret = app_secret or os.getenv('NH_APP_SECRET')
        self.base_url = "https://openapi.nhqv.com"
        self.token = None
        self.token_expires = None
        
        # 세션 생성
        self.session = requests.Session()
    
    def get_token(self) -> str:
        """Access Token 발급"""
        if self.token and self.token_expires and datetime.now() < self.token_expires:
            return self.token
        
        url = f"{self.base_url}/oauth2/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "client_credentials",
            "appkey": self.app_key,
            "appsecretkey": self.app_secret
        }
        
        response = self.session.post(url, headers=headers, data=data)
        response.raise_for_status()
        
        result = response.json()
        self.token = result['access_token']
        self.token_expires = datetime.now() + timedelta(hours=23)
        
        return self.token
    
    def get_current_price(self, ticker: str) -> dict:
        """
        주식 현재가 조회
        
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
            # Rate limit 방지: 0.2초 대기
            time.sleep(0.2)
            
            token = self.get_token()
            
            url = f"{self.base_url}/v1/quotations/inquire-price"
            headers = {
                "Content-Type": "application/json",
                "authorization": f"Bearer {token}",
                "appkey": self.app_key,
                "appsecret": self.app_secret
            }
            params = {
                "PRDT_TYPE_CD": "300",  # 주식
                "PDNO": ticker
            }
            
            response = self.session.get(url, headers=headers, params=params)
            
            # 에러 체크
            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}: {response.text}")
            
            data = response.json()
            
            # API 에러 체크
            if data.get('rt_cd') != '0':
                error_msg = data.get('msg1', 'Unknown error')
                raise Exception(f"API Error: {error_msg}")
            
            output = data['output']
            
            return {
                'ticker': ticker,
                'name': output.get('hts_kor_isnm', ''),
                'price': float(output.get('stck_prpr', 0)),
                'change': float(output.get('prdy_ctrt', 0)),
                'volume': int(output.get('acml_vol', 0)),
                'high': float(output.get('stck_hgpr', 0)),
                'low': float(output.get('stck_lwpr', 0)),
                'open': float(output.get('stck_oprc', 0))
            }
            
        except Exception as e:
            print(f"❌ {ticker} 조회 실패: {e}")
            raise


if __name__ == "__main__":
    # 테스트
    from dotenv import load_dotenv
    load_dotenv()
    
    api = NHStockAPI()
    
    print("=" * 60)
    print("NH투자증권 API 테스트")
    print("=" * 60)
    
    # 삼성전자 조회
    try:
        samsung = api.get_current_price('005930')
        print(f"\n✅ {samsung['name']}: {samsung['price']:,}원 ({samsung['change']:+.2f}%)")
    except Exception as e:
        print(f"\n❌ 에러: {e}")
