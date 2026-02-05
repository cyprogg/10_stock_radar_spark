"""
한국투자증권 Open API 통합 예제
실시간 주가 조회 서비스
"""

import requests
import ssl
import os
import time
from datetime import datetime, timedelta
from typing import Optional
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager
from urllib3.util.ssl_ import create_urllib3_context
import urllib3


class TLSAdapter(HTTPAdapter):
    """
    TLS 1.2 이상을 강제하는 HTTP Adapter
    한국투자증권 API는 TLS 1.2+ 만 허용
    """
    
    def init_poolmanager(self, *args, **kwargs):
        context = create_urllib3_context()
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.maximum_version = ssl.TLSVersion.MAXIMUM_SUPPORTED
        kwargs['ssl_context'] = context
        return super(TLSAdapter, self).init_poolmanager(*args, **kwargs)


class KoreaInvestmentAPI:
    """
    한국투자증권 Open API 래퍼 클래스
    
    사용 전 준비:
    1. https://apiportal.koreainvestment.com/ 회원가입
    2. API 신청 → 앱 키 발급
    3. 환경변수 설정:
       - KIS_APP_KEY
       - KIS_APP_SECRET
    """
    
    def __init__(self, app_key: Optional[str] = None, app_secret: Optional[str] = None, use_mock: bool = False):
        self.app_key = app_key or os.getenv('KIS_APP_KEY')
        self.app_secret = app_secret or os.getenv('KIS_APP_SECRET')
        
        # 모의투자 모드 (IP 제한 없음)
        if use_mock or os.getenv('KIS_USE_MOCK', 'false').lower() == 'true':
            self.base_url = "https://openapivts.koreainvestment.com:9443"
            print("⚠️  모의투자 서버 사용 중")
        else:
            self.base_url = "https://openapi.koreainvestment.com:9943"
        
        self.token = None
        self.token_expires = None
        
        # TLS 1.2+ 세션 생성
        self.session = requests.Session()
        self.session.mount('https://', TLSAdapter())
        
        # SSL 검증 비활성화 (회사 방화벽/프록시 대응)
        self.session.verify = False
        
        # SSL 경고 메시지 숨기기
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    def get_token(self) -> str:
        """
        Access Token 발급
        (24시간 유효)
        """
        if self.token and self.token_expires and datetime.now() < self.token_expires:
            return self.token
        
        url = f"{self.base_url}/oauth2/tokenP"
        headers = {"content-type": "application/json"}
        data = {
            "grant_type": "client_credentials",
            "appkey": self.app_key,
            "appsecret": self.app_secret
        }
        
        # TLS 1.2+ 세션 사용
        response = self.session.post(url, headers=headers, json=data)
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
            # Rate limit 방지: 0.2초 대기 (초당 5건, 안전)
            time.sleep(0.2)
            
            token = self.get_token()
            
            url = f"{self.base_url}/uapi/domestic-stock/v1/quotations/inquire-price"
            headers = {
                "content-type": "application/json",
                "authorization": f"Bearer {token}",
                "appkey": self.app_key,
                "appsecret": self.app_secret,
                "tr_id": "FHKST01010100"
            }
            params = {
                "FID_COND_MRKT_DIV_CODE": "J",
                "FID_INPUT_ISCD": ticker
            }
            
            # TLS 1.2+ 세션 사용
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
                'name': output.get('prdt_name', ''),
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
    
    def get_daily_price(self, ticker: str, start_date: str, end_date: str) -> list:
        """
        일봉 데이터 조회
        
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
        
        url = f"{self.base_url}/uapi/domestic-stock/v1/quotations/inquire-daily-price"
        headers = {
            "content-type": "application/json",
            "authorization": f"Bearer {token}",
            "appkey": self.app_key,
            "appsecret": self.app_secret,
            "tr_id": "FHKST01010400"
        }
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": ticker,
            "FID_PERIOD_DIV_CODE": "D",
            "FID_ORG_ADJ_PRC": "0"
        }
        
        # TLS 1.2+ 세션 사용
        response = self.session.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        result = []
        
        for item in data['output']:
            date = item['stck_bsop_date']
            if start_date <= date <= end_date:
                result.append({
                    'date': date,
                    'open': float(item['stck_oprc']),
                    'high': float(item['stck_hgpr']),
                    'low': float(item['stck_lwpr']),
                    'close': float(item['stck_clpr']),
                    'volume': int(item['acml_vol'])
                })
        
        return result


# ========== 사용 예제 ==========

if __name__ == "__main__":
    # API 인스턴스 생성
    api = KoreaInvestmentAPI()
    
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
