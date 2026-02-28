"""
120일 일별 시세 데이터 수집 스크립트
KRX Open API를 통한 초기 데이터 로딩 및 갱신

사용법:
    python collect_historical_prices.py --ticker 079550 --days 120
    python collect_historical_prices.py --ticker 005930 --from 2026-01-01 --to 2026-02-28
"""

import sys
import os
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import argparse
import time

# 상위 디렉토리의 모듈 import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.krx_stock_api import KRXStockAPI
from database import SessionLocal
from models.stock import StockPrice


class HistoricalPriceCollector:
    """역사적 시세 데이터 수집기"""
    
    def __init__(self):
        self.krx_api = KRXStockAPI()
        self.db = SessionLocal()
    
    def get_trading_days(self, start_date: datetime, end_date: datetime) -> List[str]:
        """
        거래일만 추출 (평일 기준, 실제 공휴일은 KRX API 응답으로 필터링)
        
        Args:
            start_date: 시작 날짜
            end_date: 종료 날짜
        
        Returns:
            ['2026-02-26', '2026-02-25', ...] (역순)
        """
        trading_days = []
        current = start_date
        
        while current <= end_date:
            # 평일만 (월~금)
            if current.weekday() < 5:
                trading_days.append(current.strftime('%Y-%m-%d'))
            current += timedelta(days=1)
        
        # 최신 날짜부터 조회하도록 역순 정렬
        return sorted(trading_days, reverse=True)
    
    def collect_for_ticker(self, ticker: str, start_date: str, end_date: str,
                          batch_size: int = 5, delay: float = 0.5) -> Tuple[int, int]:
        """
        특정 종목의 기간별 시세 수집
        
        Args:
            ticker: 종목코드 (예: '079550')
            start_date: 시작 날짜 (YYYY-MM-DD)
            end_date: 종료 날짜 (YYYY-MM-DD)
            batch_size: 배치당 요청 수
            delay: 요청 간 대기 시간 (초)
        
        Returns:
            (수집된 레코드 수, 실패한 레코드 수)
        """
        print(f"\n{'='*70}")
        print(f"종목 {ticker} 데이터 수집 시작")
        print(f"기간: {start_date} ~ {end_date}")
        print(f"{'='*70}\n")
        
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        trading_days = self.get_trading_days(start, end)
        total_days = len(trading_days)
        
        print(f"📅 거래일 수: {total_days}일")
        print(f"🔄 배치 요청: {batch_size}일마다 {delay}초 대기\n")
        
        collected = 0
        failed = 0
        skipped = 0  # 이미 DB에 있는 데이터
        
        for idx, date_str in enumerate(trading_days, 1):
            try:
                # 진행 상황 표시
                if idx % batch_size == 0 or idx == 1:
                    print(f"[{idx:3d}/{total_days}] {date_str} 조회 중...", end=' ')
                
                # 이미 DB에 있는 데이터 확인
                existing = self.db.query(StockPrice).filter(
                    StockPrice.ticker == ticker,
                    StockPrice.date == date_str,
                    StockPrice.market == 'KR'
                ).first()
                
                if existing:
                    print(f"[스킵] 이미 저장됨")
                    skipped += 1
                    continue
                
                # KRX API 호출
                price_data = self.krx_api.get_daily_price(ticker, date_str)
                
                if price_data:
                    # DB 저장
                    stock_price = StockPrice(
                        ticker=price_data['ticker'],
                        market='KR',
                        date=price_data['date'],
                        open=price_data['open'],
                        high=price_data['high'],
                        low=price_data['low'],
                        close=price_data['close'],
                        volume=price_data['volume'],
                        source=price_data['source']
                    )
                    self.db.add(stock_price)
                    collected += 1
                    
                    if idx % batch_size == 0 or idx == total_days:
                        self.db.commit()
                        print(f"[✅ 저장] {price_data['close']:,}원")
                    else:
                        print("[임시]", end=' ')
                else:
                    print(f"[❌ 실패] 응답 없음")
                    failed += 1
                
                # Rate limit 방지
                if idx % batch_size == 0 and idx < total_days:
                    print(f"⏰ {delay}초 대기 중...")
                    time.sleep(delay)
                
            except Exception as e:
                print(f"[❌ 에러] {str(e)[:40]}")
                failed += 1
            
            # 50번 요청마다 프로그레스 리포트
            if idx % 50 == 0:
                print(f"\n💾 진행 상황: {collected}개 저장, {failed}개 실패, {skipped}개 스킵\n")
        
        # 최종 커밋
        try:
            self.db.commit()
        except:
            self.db.rollback()
        
        print(f"\n{'='*70}")
        print(f"[완료] {ticker}")
        print(f"  ✅ 저장: {collected}개 레코드")
        print(f"  ❌ 실패: {failed}개")
        print(f"  ⏭️  스킵: {skipped}개 (기존 데이터)")
        print(f"{'='*70}\n")
        
        return collected, failed
    
    def collect_last_120_days(self, ticker: str) -> Tuple[int, int]:
        """
        최근 120일 시세 수집 (편의 함수)
        
        Args:
            ticker: 종목코드
        
        Returns:
            (수집된 레코드 수, 실패한 레코드 수)
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=120)
        
        return self.collect_for_ticker(
            ticker,
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )
    
    def batch_collect(self, tickers: List[str], days: int = 120) -> Dict[str, Tuple[int, int]]:
        """
        여러 종목의 120일 데이터 일괄 수집
        
        Args:
            tickers: 종목코드 리스트 (예: ['079550', '005930'])
            days: 수집 일 수 (기본 120일)
        
        Returns:
            {
                '079550': (52 저장, 3 실패),
                '005930': (48 저장, 2 실패),
                ...
            }
        """
        print(f"\n{'='*70}")
        print(f"🚀 배치 수집 시작 ({len(tickers)}개 종목)")
        print(f"{'='*70}\n")
        
        results = {}
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        for ticker in tickers:
            try:
                collected, failed = self.collect_for_ticker(
                    ticker,
                    start_date.strftime('%Y-%m-%d'),
                    end_date.strftime('%Y-%m-%d')
                )
                results[ticker] = (collected, failed)
            except Exception as e:
                print(f"⚠️  {ticker} 수집 실패: {e}\n")
                results[ticker] = (0, -1)  # -1은 심각한 에러 표시
        
        return results
    
    def __del__(self):
        """정리"""
        if self.db:
            self.db.close()


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description='KRX API를 통한 120일 일별 시세 수집',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예제:
  # 최근 120일 수집
  python collect_historical_prices.py --ticker 079550 --days 120
  
  # 특정 기간 수집
  python collect_historical_prices.py --ticker 079550 --from 2025-11-01 --to 2026-02-28
  
  # 여러 종목 일괄 수집
  python collect_historical_prices.py --batch 079550,005930,000660
        """
    )
    
    parser.add_argument('--ticker', type=str, help='종목코드 (예: 079550)')
    parser.add_argument('--days', type=int, default=120, help='수집 일 수 (기본: 120일)')
    parser.add_argument('--from', dest='start_date', type=str, help='시작 날짜 (YYYY-MM-DD)')
    parser.add_argument('--to', dest='end_date', type=str, help='종료 날짜 (YYYY-MM-DD)')
    parser.add_argument('--batch', type=str, help='여러 종목 일괄 수집 (쉼표 구분: 079550,005930)')
    
    args = parser.parse_args()
    
    collector = HistoricalPriceCollector()
    
    if args.batch:
        # 배치 수집
        tickers = [t.strip() for t in args.batch.split(',')]
        results = collector.batch_collect(tickers, args.days)
        
        # 최종 리포트
        print(f"\n{'='*70}")
        print("📊 최종 수집 결과")
        print(f"{'='*70}\n")
        
        total_collected = 0
        total_failed = 0
        
        for ticker, (collected, failed) in results.items():
            if failed == -1:
                print(f"{ticker}: ❌ 심각한 에러 발생")
            else:
                print(f"{ticker}: ✅ {collected}개 저장, ❌ {failed}개 실패")
                total_collected += collected
                total_failed += failed
        
        print(f"\n총계: ✅ {total_collected}개, ❌ {total_failed}개 실패\n")
    
    elif args.ticker:
        # 단일 종목 수집
        if args.start_date and args.end_date:
            # 기간 지정
            collector.collect_for_ticker(args.ticker, args.start_date, args.end_date)
        else:
            # 최근 N일 수집
            collector.collect_last_120_days(args.ticker)
    
    else:
        parser.print_help()
        print("\n❌ 종목코드(--ticker) 또는 배치(--batch) 옵션을 지정하세요.")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  사용자 중단")
    except Exception as e:
        print(f"\n❌ 오류: {e}")
        import traceback
        traceback.print_exc()
