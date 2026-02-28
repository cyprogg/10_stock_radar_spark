#!/usr/bin/env python3
"""
테스트용 샘플 주가 데이터를 DB에 로드
Mock 데이터 대신 실제 DB에 저장
"""
import os
import sys
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 상위 디렉토리 모듈 import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models.stock import StockPrice

# 샘플 주가 데이터 (실제 데이터 기반)
SAMPLE_STOCKS = [
    # 한국 주식
    {
        'ticker': '005930',
        'name': '삼성전자',
        'market': 'KR',
        'prices': [74500, 75000, 74800, 74500, 74500]
    },
    {
        'ticker': '068270',
        'name': '셀트리온',
        'market': 'KR',
        'prices': [172500, 173000, 174500, 175000, 174000]
    },
    {
        'ticker': '207940',
        'name': '삼성바이오로직스',
        'market': 'KR',
        'prices': [1710000, 1720000, 1715000, 1725000, 1730000]
    },
    {
        'ticker': '012450',
        'name': '한화에어로스페이스',
        'market': 'KR',
        'prices': [1200000, 1202000, 1203000, 1204000, 1205000]
    },
    # 미국 주식
    {
        'ticker': 'JNJ',
        'name': 'Johnson & Johnson',
        'market': 'US',
        'prices': [243.50, 244.00, 244.99, 245.50, 244.75]
    },
    {
        'ticker': 'NVDA',
        'name': 'NVIDIA',
        'market': 'US',
        'prices': [185.50, 186.50, 187.98, 188.50, 187.25]
    },
    {
        'ticker': 'NEE',
        'name': 'NextEra Energy',
        'market': 'US',
        'prices': [57.50, 58.00, 58.30, 58.75, 58.25]
    }
]

def load_sample_data():
    """샘플 주가 데이터를 DB에 로드"""
    db = SessionLocal()
    
    for stock in SAMPLE_STOCKS:
        ticker = stock['ticker']
        prices = stock['prices']
        
        # 기존 데이터 삭제
        db.query(StockPrice).filter(StockPrice.ticker == ticker).delete()
        
        # 새 데이터 생성 (최근 5일)
        base_date = datetime.now().date()
        for i, close_price in enumerate(prices):
            date = base_date - timedelta(days=len(prices) - i - 1)
            
            # 가격에서 ±2% 범위로 시가/고가/저가 생성
            open_price = close_price * 0.99
            high_price = close_price * 1.015
            low_price = close_price * 0.985
            volume = (1000000 + i * 100000) if stock['market'] == 'KR' else (50000000 + i * 1000000)
            
            record = StockPrice(
                ticker=ticker,
                market=stock['market'],
                date=date,
                open=open_price,
                high=high_price,
                low=low_price,
                close=close_price,
                volume=volume,
                source='Test Data',
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            db.add(record)
        
        print(f"✅ {ticker} ({stock['name']}): {len(prices)}일 데이터 로드 완료")
    
    db.commit()
    db.close()
    
    print("\n✅ 모든 샘플 데이터 로드 완료!")

if __name__ == '__main__':
    load_sample_data()
