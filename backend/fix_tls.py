#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TLS 1.2+ 강제 적용 스크립트
한국투자증권 API 연결을 위한 TLS 설정 강제
"""

import ssl
import requests
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager
from urllib3.util.ssl_ import create_urllib3_context

class TLSAdapter(HTTPAdapter):
    """TLS 1.2 이상을 강제하는 HTTP Adapter"""
    
    def init_poolmanager(self, *args, **kwargs):
        # TLS 1.2 이상을 강제
        context = create_urllib3_context()
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.maximum_version = ssl.TLSVersion.MAXIMUM_SUPPORTED
        
        kwargs['ssl_context'] = context
        return super(TLSAdapter, self).init_poolmanager(*args, **kwargs)

def create_tls_session():
    """TLS 1.2+ 를 강제하는 requests.Session 생성"""
    session = requests.Session()
    session.mount('https://', TLSAdapter())
    return session

# 테스트
if __name__ == "__main__":
    print("=" * 60)
    print("🔧 TLS 1.2+ 강제 적용 테스트")
    print("=" * 60)
    
    # TLS 1.2+ 세션 생성
    session = create_tls_session()
    
    # 한국투자증권 API 서버 연결 테스트
    test_url = "https://openapi.koreainvestment.com:9443"
    
    try:
        print(f"\n연결 시도: {test_url}")
        response = session.get(test_url, timeout=10)
        print(f"✅ 연결 성공! 상태 코드: {response.status_code}")
        print("\n💡 TLS 1.2+ 강제 적용 성공!")
        print("   → 이 방식을 korea_investment_api.py에 적용하면 됩니다.")
    except Exception as e:
        print(f"❌ 에러: {e}")
        print("\n💡 해결 방법:")
        print("   1) Python 3.7 이상으로 업그레이드")
        print("   2) pip install --upgrade requests urllib3")
        print("   3) OpenSSL 1.1.1 이상 설치")
    
    print("\n" + "=" * 60)
