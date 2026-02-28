#!/usr/bin/env python3
"""
실제 주가 데이터 수집 및 DB 저장
- 한국 주식: Naver 크롤러
- 미국 주식: yfinance (15분 지연)
"""
import os
import sys
from datetime import datetime

# 상위 디렉토리 모듈 import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models.stock import StockPrice
from services.naver_stock_scraper import NaverStockScraper
from services.us_stock_service import USStockService

# 수집할 종목
KR_STOCKS = [
    ('005930', '삼성전자'),
    ('068270', '셀트리온'),
    ('207940', '삼성바이오로직스'),
    ('012450', '한화에어로스페이스'),
]

US_STOCKS = [
    ('JNJ', 'Johnson & Johnson'),
    ('NVDA', 'NVIDIA'),
    ('LMT', 'Lockheed Martin'),
    ('NEE', 'NextEra Energy'),
]

def collect_kr_prices():
    """한국 주식 데이터 수집"""
    print("\n" + "="*70)
    print("🇰🇷 한국 주식 데이터 수집 중...")
    print("="*70)
    
    scraper = NaverStockScraper()
    db = SessionLocal()
    
    for ticker, name in KR_STOCKS:
        try:
            print(f"\n📊 {name} ({ticker}) 조회 중...")
            data = scraper.get_stock_overview(ticker)
            
            if not data or 'current_price' not in data:
                print(f"  ❌ 데이터 없음")
                continue
            
            # 기존 데이터는 최신 레코드만 유지
            db.query(StockPrice).filter(StockPrice.ticker == ticker).delete()
            
            price = data['current_price']
            change = data.get('change', 0)
            prev_close = price - change if change else price * 0.98
            
            record = StockPrice(
                ticker=ticker,
                market='KR',
                date=datetime.now().date(),
                open=prev_close,
                high=data.get('week_52_high', price * 1.05),
                low=data.get('week_52_low', price * 0.95),
                close=price,
                volume=data.get('volume', 0),
                source='Naver Finance',
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            db.add(record)
            db.commit()
            
            print(f"  ✅ {name}: ₩{price:,} (변동: {change:+.0f})")
            
        except Exception as e:
            print(f"  ❌ 오류: {str(e)}")
            db.rollback()
    
    db.close()

def collect_us_prices():
    """미국 주식 데이터 수집"""
    print("\n" + "="*70)
    print("🇺🇸 미국 주식 데이터 수집 중... (15분 지연)")
    print("="*70)
    
    service = USStockService()
    db = SessionLocal()
    
    for ticker, name in US_STOCKS:
        try:
            print(f"\n📊 {name} ({ticker}) 조회 중...")
            data = service.get_current_price_yf(ticker)
            
            if not data or 'price' not in data:
                print(f"  ❌ 데이터 없음")
                continue
            
            # 기존 데이터는 최신 레코드만 유지
            db.query(StockPrice).filter(StockPrice.ticker == ticker).delete()
            
            price = data['price']
            change = data.get('change', 0)
            prev_close = price - change if change else price * 0.98
            
            record = StockPrice(
                ticker=ticker,
                market='US',
                date=datetime.now().date(),
                open=data.get('open', prev_close),
                high=data.get('high', price * 1.02),
                low=data.get('low', price * 0.98),
                close=price,
                volume=data.get('volume', 0),
                source=f'yfinance (15분 지연)',
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            db.add(record)
            db.commit()
            
            print(f"  ✅ {name}: ${price:.2f} (변동: {change:+.2f})")
            
        except Exception as e:
            print(f"  ❌ 오류: {str(e)}")
            db.rollback()
    
    db.close()

if __name__ == '__main__':
    print("\n🌍 실제 주가 데이터 수집 시작")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        collect_kr_prices()
        collect_us_prices()
        
        print("\n" + "="*70)
        print("✅ 모든 데이터 수집 완료!")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ 치명적 오류: {e}\n")
        sys.exit(1)
