"""
주가 데이터 모델
SQLAlchemy ORM - 일별 시세 저장
"""

from sqlalchemy import Column, String, DateTime, Float, Integer, Date, UniqueConstraint, Index
from datetime import datetime
from models.user import Base  # user.py의 Base 사용


class StockPrice(Base):
    """주가 데이터 모델 - 일별 시세"""
    
    __tablename__ = "stock_prices"
    
    # 기본 정보
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(10), index=True, nullable=False)  # 종목코드 (예: 079550)
    market = Column(String(10), nullable=False, default="KR")  # KR or US
    date = Column(Date, nullable=False, index=True)  # 거래 날짜 (YYYY-MM-DD)
    
    # 시세 정보
    open = Column(Float, nullable=True)  # 시가
    high = Column(Float, nullable=True)  # 고가
    low = Column(Float, nullable=True)   # 저가
    close = Column(Float, nullable=True) # 종가
    volume = Column(Integer, nullable=True)  # 거래량
    
    # 메타 정보
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    source = Column(String(50), nullable=True)  # 데이터 소스 (KRX, Yahoo 등)
    
    # 복합 인덱스: ticker + date (일자별 조회 성능 최적화)
    __table_args__ = (
        UniqueConstraint('ticker', 'date', 'market', name='unique_ticker_date_market'),
        Index('idx_ticker_date', 'ticker', 'date'),
        Index('idx_market_date', 'market', 'date'),
    )
    
    def __repr__(self):
        return f"<StockPrice {self.ticker} {self.date}: {self.close}>"
