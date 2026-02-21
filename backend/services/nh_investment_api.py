"""
NH투자증권 Open API 통합
실시간 주가 조회 서비스
"""

import requests
import ssl
import os
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager
from urllib3.util.ssl_ import create_urllib3_context
import urllib3


class TLSAdapter(HTTPAdapter):
    """
    TLS 1.2 이상을 강제하는 HTTP Adapter
    """
    
    def init_poolmanager(self, *args, **kwargs):
        context = create_urllib3_context()
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.maximum_version = ssl.TLSVersion.MAXIMUM_SUPPORTED
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        kwargs['ssl_context'] = context
        return super(TLSAdapter, self).init_poolmanager(*args, **kwargs)


class NHInvestmentAPI:
    """
    NH투자증권 Open API 래퍼 클래스
    
    사용 전 준비:
    1. https://securities.nhqv.com 회원가입
    2. API 신청 → 앱 키 발급
    3. 환경변수 설정:
       - NH_APP_KEY
       - NH_APP_SECRET
       - NH_ACCOUNT_NO (선택)
    """
    
    def __init__(self, app_key: Optional[str] = None, app_secret: Optional[str] = None, use_mock: bool = False):
        self.app_key = app_key or os.getenv('NH_APP_KEY')
        self.app_secret = app_secret or os.getenv('NH_APP_SECRET')
        self.account_no = os.getenv('NH_ACCOUNT_NO', '')
        
        # 모의투자 모드
        if use_mock or os.getenv('NH_USE_MOCK', 'false').lower() == 'true':
            self.base_url = "https://openapi-mock.nhqv.com"
            print("⚠️  NH투자증권 모의투자 서버 사용 중")
        else:
            self.base_url = "https://openapi.nhqv.com"
        
        self.token = None
        self.token_expires = None
        
        # TLS 1.2+ 세션 생성
        self.session = requests.Session()
        self.session.mount('https://', TLSAdapter())
        
        # SSL 검증 비활성화 (회사 방화벽/프록시 대응)
        self.session.verify = False
        
        # SSL 경고 메시지 숨기기
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    def get_token(self) -> str:
        """
        Access Token 발급
        (NH투자증권 API 토큰은 24시간 유효)
        """
        if self.token and self.token_expires and datetime.now() < self.token_expires:
            return self.token
        
        url = f"{self.base_url}/oauth2/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "client_credentials",
            "appkey": self.app_key,
            "secretkey": self.app_secret
        }
        
        try:
            response = self.session.post(url, headers=headers, data=data)
            response.raise_for_status()
            
            result = response.json()
            self.token = result.get('access_token', result.get('token'))
            self.token_expires = datetime.now() + timedelta(hours=23)
            
            return self.token
        except Exception as e:
            print(f"⚠️  토큰 발급 실패: {e}")
            # 토큰 없이도 일부 API 사용 가능
            return ""
    
    def get_current_price(self, ticker: str) -> dict:
        """
        주식 현재가 조회 (NH투자증권 API)
        
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
            # Rate limit 방지
            time.sleep(0.2)
            
            token = self.get_token()
            
            url = f"{self.base_url}/api/stock/current-price"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}" if token else "",
                "X-API-KEY": self.app_key
            }
            params = {
                "code": ticker,
                "market": "KRX"
            }
            
            response = self.session.get(url, headers=headers, params=params)
            
            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}: {response.text}")
            
            data = response.json()
            
            # NH API 응답 형식에 맞게 파싱
            if 'data' in data:
                output = data['data']
            else:
                output = data
            
            return {
                'ticker': ticker,
                'name': output.get('name', output.get('itemname', '')),
                'price': float(output.get('price', output.get('curprice', 0))),
                'change': float(output.get('change_rate', output.get('rate', 0))),
                'volume': int(output.get('volume', output.get('volume', 0))),
                'high': float(output.get('high', output.get('high', 0))),
                'low': float(output.get('low', output.get('low', 0))),
                'open': float(output.get('open', output.get('open', 0)))
            }
            
        except Exception as e:
            print(f"❌ {ticker} 조회 실패: {e}")
            raise
    
    def get_daily_price(self, ticker: str, start_date: str, end_date: str) -> list:
        """
        일봉 데이터 조회 (NH투자증권 API)
        
        Args:
            ticker: 종목코드
            start_date: 시작일 (YYYYMMDD)
            end_date: 종료일 (YYYYMMDD)
        
        Returns:
            [
                {
                    'date': '20240121',
                    'open': 75000,
                    'high': 76000,
                    'low': 74500,
                    'close': 75500,
                    'volume': 12345678
                },
                ...
            ]
        """
        token = self.get_token()
        
        url = f"{self.base_url}/api/stock/daily-price"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}" if token else "",
            "X-API-KEY": self.app_key
        }
        params = {
            "code": ticker,
            "start_date": start_date,
            "end_date": end_date,
            "period": "D"
        }
        
        response = self.session.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        result = []
        
        # NH API 응답 형식에 맞게 파싱
        items = data.get('data', data.get('output', []))
        
        for item in items:
            date = item.get('date', item.get('stck_bsop_date', ''))
            if start_date <= date <= end_date:
                result.append({
                    'date': date,
                    'open': float(item.get('open', item.get('stck_oprc', 0))),
                    'high': float(item.get('high', item.get('stck_hgpr', 0))),
                    'low': float(item.get('low', item.get('stck_lwpr', 0))),
                    'close': float(item.get('close', item.get('stck_clpr', 0))),
                    'volume': int(item.get('volume', item.get('acml_vol', 0)))
                })
        
        return result


# ========== 사용 예제 ==========

if __name__ == "__main__":
    # NH투자증권 API 인스턴스 생성
    api = NHInvestmentAPI()
    
    # 예제 1: 삼성전자 현재가 조회
    print("=" * 50)
    print("예제 1: 삼성전자 현재가 조회")
    print("=" * 50)
    
    samsung = api.get_current_price('005930')
    print(f"종목명: {samsung['name']}")
    print(f"현재가: {samsung['price']:,}원")
    print(f"등락률: {samsung['change']:+.2f}%")
    print(f"거래량: {samsung['volume']:,}주")
    print(f"고가: {samsung['high']:,}원")
    print(f"저가: {samsung['low']:,}원")
    print()
    
    # 예제 2: SK하이닉스 현재가 조회
    print("=" * 50)
    print("예제 2: SK하이닉스 현재가 조회")
    print("=" * 50)
    
    hynix = api.get_current_price('000660')
    print(f"종목명: {hynix['name']}")
    print(f"현재가: {hynix['price']:,}원")
    print(f"등락률: {hynix['change']:+.2f}%")
    print()
    
    # 예제 3: 삼성전자 일봉 데이터 (최근 5일)
    print("=" * 50)
    print("예제 3: 삼성전자 일봉 데이터 (최근 5일)")
    print("=" * 50)
    
    daily = api.get_daily_price('005930', '20240101', '20240121')
    for item in daily[:5]:
        print(f"{item['date']}: 시가 {item['open']:,}, 종가 {item['close']:,}, 거래량 {item['volume']:,}")
    print()
    
    # 예제 4: 여러 종목 한번에 조회
    print("=" * 50)
    print("예제 4: 방산 섹터 주요 종목")
    print("=" * 50)
    
    defense_stocks = [
        ('012450', '한화에어로스페이스'),
        ('079550', 'LIG넥스원'),
        ('272210', '한화시스템')
    ]
    
    for ticker, name in defense_stocks:
        try:
            data = api.get_current_price(ticker)
            print(f"{data['name']}: {data['price']:,}원 ({data['change']:+.2f}%)")
        except Exception as e:
            print(f"{name}: 조회 실패 - {e}")
    
    print()
    print("✅ 모든 예제 완료!")
    print("=" * 50)
