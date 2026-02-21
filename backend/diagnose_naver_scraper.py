#!/usr/bin/env python3
"""
Naver Stock Scraper 상태 확인
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.naver_stock_scraper import NaverStockScraper

print("=" * 70)
print("Naver Stock Scraper 상태 진단")
print("=" * 70)

scraper = NaverStockScraper()

# 1. 종목 정보
print("\n[1] 종목 정보 조회 (삼성전자 005930)")
print("  진행 중...")
try:
    stock = scraper.get_stock_overview('005930')
    if stock and stock.get('current_price'):
        print(f"  ✅ 성공")
        print(f"    • 종목명: {stock.get('name')}")
        print(f"    • 가격: {stock.get('current_price'):,}원")
        print(f"    • PER: {stock.get('per')}")
    else:
        print(f"  ⚠️  데이터 미반환")
except Exception as e:
    print(f"  ❌ 에러: {type(e).__name__}: {str(e)[:100]}")

# 2. 수급 정보
print("\n[2] 수급 정보 조회 (최근 5일)")
print("  진행 중...")
try:
    supply = scraper.get_supply_demand('005930', days=5)
    if supply and supply.get('data'):
        print(f"  ✅ 성공")
        print(f"    • 조회 기간: {supply.get('period')}일")
        print(f"    • 데이터: {len(supply.get('data', []))}개")
    else:
        print(f"  ⚠️  데이터 미반환")
except Exception as e:
    print(f"  ❌ 에러: {type(e).__name__}: {str(e)[:100]}")

# 3. 뉴스
print("\n[3] 뉴스 조회 (최근 3건)")
print("  진행 중...")
try:
    news = scraper.get_news('005930', limit=3)
    if news:
        print(f"  ✅ 성공")
        print(f"    • 총 {len(news)}건")
        for i, n in enumerate(news[:3], 1):
            print(f"      {i}. {n.get('date')} | {n.get('source')}: {n.get('title')[:40]}")
    else:
        print(f"  ⚠️  데이터 미반환")
except Exception as e:
    print(f"  ❌ 에러: {type(e).__name__}: {str(e)[:100]}")

# 4. 공시
print("\n[4] 공시 조회 (최근 7일)")
print("  진행 중...")
try:
    disclosure = scraper.get_disclosure('005930', days=7)
    if disclosure:
        print(f"  ✅ 성공")
        print(f"    • 총 {len(disclosure)}건")
        for i, d in enumerate(disclosure[:3], 1):
            print(f"      {i}. {d.get('date')}: {d.get('title')[:40]}")
    else:
        print(f"  ⚠️  데이터 미반환")
except Exception as e:
    print(f"  ❌ 에러: {type(e).__name__}: {str(e)[:100]}")

print("\n" + "=" * 70)
print("진단 요약")
print("=" * 70)
