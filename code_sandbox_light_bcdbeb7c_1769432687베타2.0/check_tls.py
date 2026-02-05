#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TLS 버전 확인 스크립트
한국투자증권 API 연결을 위한 TLS 1.2+ 지원 여부 확인
"""

import ssl
import sys
import requests
from urllib3.util.ssl_ import create_urllib3_context

print("=" * 60)
print("🔐 TLS 버전 확인")
print("=" * 60)

# 1. OpenSSL 버전 확인
print(f"\n1️⃣ OpenSSL 버전: {ssl.OPENSSL_VERSION}")
print(f"   OpenSSL 버전 정보: {ssl.OPENSSL_VERSION_INFO}")

# 2. TLS 지원 확인
print("\n2️⃣ TLS 프로토콜 지원 여부:")
print(f"   - TLS 1.0: {hasattr(ssl, 'PROTOCOL_TLSv1')}")
print(f"   - TLS 1.1: {hasattr(ssl, 'PROTOCOL_TLSv1_1')}")
print(f"   - TLS 1.2: {hasattr(ssl, 'PROTOCOL_TLSv1_2')}")
print(f"   - TLS 1.3: {hasattr(ssl, 'TLSVersion') and hasattr(ssl.TLSVersion, 'TLSv1_3')}")

# 3. 기본 SSL 컨텍스트 확인
print("\n3️⃣ 기본 SSL 컨텍스트:")
try:
    context = ssl.create_default_context()
    print(f"   - 최소 TLS 버전: {context.minimum_version}")
    print(f"   - 최대 TLS 버전: {context.maximum_version}")
    print(f"   - 설정된 프로토콜: {context.protocol}")
except Exception as e:
    print(f"   ❌ 에러: {e}")

# 4. Requests 라이브러리의 TLS 설정
print("\n4️⃣ Requests 라이브러리:")
print(f"   - 버전: {requests.__version__}")
try:
    urllib3_ctx = create_urllib3_context()
    print(f"   - urllib3 컨텍스트 생성: ✅")
except Exception as e:
    print(f"   - urllib3 컨텍스트 생성: ❌ {e}")

# 5. 한국투자증권 API 서버 연결 테스트
print("\n5️⃣ 한국투자증권 API 서버 연결 테스트:")
test_url = "https://openapi.koreainvestment.com:9443"
try:
    print(f"   연결 시도: {test_url}")
    response = requests.get(test_url, timeout=10)
    print(f"   ✅ 연결 성공! 상태 코드: {response.status_code}")
except requests.exceptions.SSLError as e:
    print(f"   ❌ SSL 에러: {e}")
    print("\n   💡 해결 방법:")
    print("      1) Python 3.7 이상으로 업그레이드")
    print("      2) OpenSSL 1.1.1 이상 설치")
    print("      3) pip install --upgrade requests urllib3")
except requests.exceptions.RequestException as e:
    print(f"   ⚠️  기타 에러: {e}")

# 6. 권장 사항
print("\n" + "=" * 60)
print("📋 권장 사항")
print("=" * 60)

python_version = sys.version_info
if python_version >= (3, 7):
    print("✅ Python 버전: OK (TLS 1.2+ 지원)")
else:
    print(f"❌ Python 버전: {sys.version}")
    print("   → Python 3.7 이상으로 업그레이드 필요")

if ssl.OPENSSL_VERSION_INFO >= (1, 1, 1):
    print("✅ OpenSSL 버전: OK (TLS 1.2+ 지원)")
else:
    print(f"❌ OpenSSL 버전: {ssl.OPENSSL_VERSION}")
    print("   → OpenSSL 1.1.1 이상으로 업그레이드 필요")

print("\n" + "=" * 60)
print("🎯 테스트 완료!")
print("=" * 60)
