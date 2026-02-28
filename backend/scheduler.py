"""
매일 오후 6시 주가 자동 업데이트 스케줄러
- 현재가: NH투자증권 API / KRX API / Yahoo Finance
- 일봉 데이터: 키움 Open API (ka10081)
"""

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import json
import os
import sys
import time

# 상위 디렉토리의 services 모듈 import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.nh_investment_api import NHInvestmentAPI
from services.nh_stock_api import NHStockAPI
from services.krx_stock_api import KRXStockAPI
from services.us_stock_service import USStockService
from services.kiwoom_openapi import KiwoomOpenAPI
from database import SessionLocal
from models.stock import StockPrice

# 모든 종목 리스트
STOCK_LIST = {
    "US": [
        {"ticker": "LMT", "name": "Lockheed Martin"},
        {"ticker": "JNJ", "name": "Johnson & Johnson"}
    ],
    "KR": [
        # 한국투자증권 API 403 에러로 임시 비활성화
        # IP 제한 해결 후 주석 제거하여 활성화 가능
        # {"ticker": "012450", "name": "한화에어로스페이스"},
        # {"ticker": "079550", "name": "LIG넥스원"},
        # {"ticker": "005930", "name": "삼성전자"},
        # {"ticker": "000660", "name": "SK하이닉스"},
        # {"ticker": "207940", "name": "삼성바이오로직스"},
        # {"ticker": "068270", "name": "셀트리온"},
        # {"ticker": "373220", "name": "LG에너지솔루션"},
        # {"ticker": "096770", "name": "SK이노베이션"},
        # {"ticker": "051910", "name": "LG화학"},
        # {"ticker": "326030", "name": "SK바이오팜"},
        # {"ticker": "005380", "name": "현대자동차"},
        # {"ticker": "000270", "name": "기아"},
        # {"ticker": "012330", "name": "현대모비스"},
        # {"ticker": "009830", "name": "한화솔루션"},
        # {"ticker": "011170", "name": "롯데케미칼"},
        # {"ticker": "009540", "name": "한국조선해양"},
        # {"ticker": "010140", "name": "삼성중공업"},
        # {"ticker": "042660", "name": "한화오션"},
        # {"ticker": "042700", "name": "한미반도체"}
    ]
}

# 서비스 인스턴스 (전역)
kr_api = None
us_service = None
kiwoom_api = None  # 키움 Open API


def init_services():
    """API 서비스 초기화"""
    global kr_api, us_service, kiwoom_api
    
    # 일봉 데이터: 키움 Open API 우선
    try:
        kiwoom_api = KiwoomOpenAPI(is_mock=False)
        print("✅ 키움 Open API 초기화 완료 (일봉 데이터)")
    except Exception as e:
        print(f"⚠️  키움 API 초기화 실패: {e}")
        kiwoom_api = None
    
    # 한국 주식: NH투자증권 API 우선
    try:
        kr_api = NHInvestmentAPI()
        print("✅ NH투자증권 API 초기화 완료")
    except Exception as e:
        print(f"⚠️  NH API 초기화 실패: {e}")
        # KRX API로 fallback
        try:
            kr_api = KRXStockAPI()
            print("✅ 한국거래소(KRX) API 초기화 완료 (fallback)")
        except Exception as e2:
            print(f"⚠️  KRX API 초기화 실패: {e2}")
            # NH Stock API로 최종 fallback
            try:
                kr_api = NHStockAPI()
                print("✅ NH Stock API 초기화 완료 (최종 fallback)")
            except Exception as e3:
                print(f"⚠️  모든 한국 API 초기화 실패")
                kr_api = None
    
    try:
        us_service = USStockService()
        print("✅ 미국 주식 서비스 초기화 완료")
    except Exception as e:
        print(f"⚠️  미국 주식 서비스 초기화 실패: {e}")
        us_service = None


def update_daily_charts():
    """
    매일 일봉 데이터 갱신 (키움 Open API)
    
    어제의 종가 데이터를 조회하여 StockPrice 테이블에 저장
    - 최초 설정: collect_historical_prices.py로 120일 초기 데이터 수집
    - 매일 갱신: 이 함수로 전일 데이터 추가
    """
    print(f"\n{'='*70}")
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 일봉 데이터 갱신 시작")
    print(f"{'='*70}\n")
    
    if not kiwoom_api:
        print("⚠️  키움 API 사용 불가 (초기화 실패)")
        return
    
    # 어제 날짜 (거래일 기준)
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    
    # 주말이면 금요일 기준으로
    while yesterday.weekday() > 4:  # 5=sat, 6=sun
        yesterday -= timedelta(days=1)
    
    yesterday_str = yesterday.strftime('%Y%m%d')
    
    # 갱신할 종목 (KR 리스트에서 주석 해제된 것만)
    tickers_to_update = [
        ('012450', '한화에어로스페이스'),
        ('079550', 'LIG넥스원'),
        ('005930', '삼성전자'),
        ('000660', 'SK하이닉스'),
        ('207940', '삼성바이오로직스'),
    ]
    
    db = SessionLocal()
    success_count = 0
    fail_count = 0
    skip_count = 0
    
    try:
        print(f"📅 기준일: {yesterday.strftime('%Y-%m-%d')} (YYYYMMDD: {yesterday_str})\n")
        
        for ticker, name in tickers_to_update:
            try:
                # 이미 DB에 있는지 확인
                existing = db.query(StockPrice).filter(
                    StockPrice.ticker == ticker,
                    StockPrice.date == yesterday.strftime('%Y-%m-%d'),
                    StockPrice.market == 'KR'
                ).first()
                
                if existing:
                    print(f"  ⏭️  {name:20s} [{ticker}]: 이미 저장됨")
                    skip_count += 1
                    continue
                
                # 키움 API로 조회 (어제 기준일로)
                chart = kiwoom_api.get_daily_chart(ticker, end_date=yesterday_str)
                
                if not chart or len(chart) == 0:
                    print(f"  ⚠️  {name:20s} [{ticker}]: 데이터 없음 (휴장일?)")
                    fail_count += 1
                    continue
                
                # 가장 최근 거래일 기준 데이터 저장
                latest = chart[-1]  # 정렬되어 있으므로 마지막이 최신
                if latest['date'] <= yesterday.strftime('%Y-%m-%d'):
                    stock_price = StockPrice(
                        ticker=ticker,
                        market='KR',
                        date=latest['date'],
                        open=latest['open'],
                        high=latest['high'],
                        low=latest['low'],
                        close=latest['close'],
                        volume=latest['volume'],
                        source='Kiwoom'
                    )
                    db.add(stock_price)
                    print(f"  ✅ {name:20s} [{ticker}]: "
                          f"종가 {latest['close']:>10,.0f}원 | "
                          f"거래량 {latest['volume']:>10,}")
                    success_count += 1
                else:
                    print(f"  ⚠️  {name:20s} [{ticker}]: 날짜 오류 (조회 실패)")
                    fail_count += 1
                
                # Rate limit 방지
                time.sleep(0.5)
            
            except Exception as e:
                print(f"  ❌ {name:20s} [{ticker}]: 오류 - {str(e)[:30]}")
                fail_count += 1
        
        # 커밋
        db.commit()
        
        print(f"\n{'='*70}")
        print(f"일봉 데이터 갱신 완료")
        print(f"  ✅ 저장: {success_count}개")
        print(f"  ⏭️  스킵: {skip_count}개 (기존 데이터)")
        print(f"  ❌ 실패: {fail_count}개")
        print(f"{'='*70}\n")
    
    except Exception as e:
        db.rollback()
        print(f"❌ 일괄 오류: {e}")
    
    finally:
        db.close()


def update_stock_prices():
    """모든 종목의 종가를 조회하여 JSON 파일에 저장"""
    print(f"\n{'='*60}")
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 주가 업데이트 시작")
    print(f"{'='*60}\n")
    
    prices = {}
    stock_info = {}  # 종목 상세 정보
    success_count = 0
    fail_count = 0
    
    # 미국 주식 조회
    if us_service:
        print("📊 미국 주식 조회 중...")
        for stock in STOCK_LIST["US"]:
            ticker = stock["ticker"]
            name = stock["name"]
            try:
                data = us_service.get_current_price(ticker)
                price = round(float(data['price']), 2)
                prices[ticker] = price
                stock_info[ticker] = {
                    "name": name,
                    "market": "US",
                    "price": price
                }
                print(f"  ✅ {name:30s} ({ticker:6s}): ${price:>10.2f}")
                success_count += 1
            except Exception as e:
                print(f"  ❌ {name:30s} ({ticker:6s}): 조회 실패 - {e}")
                fail_count += 1
        print()
    else:
        print("⚠️  미국 주식 서비스 사용 불가 (API 초기화 실패)\n")
    
    # 한국 주식 조회
    if kr_api:
        print("📊 한국 주식 조회 중...")
        for stock in STOCK_LIST["KR"]:
            ticker = stock["ticker"]
            name = stock["name"]
            try:
                data = kr_api.get_current_price(ticker)
                price = int(data['price'])
                prices[ticker] = price
                stock_info[ticker] = {
                    "name": name,
                    "market": "KR",
                    "price": price
                }
                print(f"  ✅ {name:30s} ({ticker:6s}): ₩{price:>10,}")
                success_count += 1
            except Exception as e:
                print(f"  ❌ {name:30s} ({ticker:6s}): 조회 실패 - {e}")
                fail_count += 1
        print()
    else:
        print("⚠️  한국 주식 서비스 사용 불가 (API 초기화 실패)\n")
    
    # JSON 파일로 저장
    data = {
        "lastUpdate": datetime.now().isoformat(),
        "updateTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "totalStocks": len(STOCK_LIST["US"]) + len(STOCK_LIST["KR"]),
        "successCount": success_count,
        "failCount": fail_count,
        "prices": prices,
        "stocks": stock_info  # 종목 상세 정보 추가
    }
    
    # 파일 경로 (프로젝트 루트에 저장)
    output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'stock_prices.json')
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"{'='*60}")
    print(f"📁 저장 위치: {output_path}")
    print(f"✅ 성공: {success_count}개")
    if fail_count > 0:
        print(f"❌ 실패: {fail_count}개")
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 주가 업데이트 완료!")
    print(f"{'='*60}\n")


def start_scheduler():
    """스케줄러 시작"""
    init_services()
    
    scheduler = BackgroundScheduler()
    
    # 1. 매일 오후 5시: 일봉 데이터 갱신 (키움 API)
    scheduler.add_job(
        update_daily_charts,
        'cron',
        hour=17,
        minute=0,
        id='daily_chart_update',
        replace_existing=True
    )
    
    # 2. 매일 오후 6시: 현재가 조회 및 JSON 갱신
    scheduler.add_job(
        update_stock_prices,
        'cron',
        hour=18,
        minute=0,
        id='daily_price_update',
        replace_existing=True
    )
    
    scheduler.start()
    
    print(f"\n{'='*70}")
    print("🕐 스케줄러 시작됨")
    print("\n📅 실행 일정:")
    print("   ┌─ 오후 5시 (17:00): 일봉 데이터 갱신 (키움 API)")
    print("   │  - 저장 위치: StockPrice 테이블")
    print("   │  - 대상: 한국 주식 (120일 누적)")
    print("   │")
    print("   └─ 오후 6시 (18:00): 현재가 조회 (NH/KRX/Yahoo)")
    print("      - 저장 위치: stock_prices.json")
    print(f"\n📊 대상 종목:")
    print(f"   - 미국 주식: {len(STOCK_LIST['US'])}개")
    print(f"   - 한국 주식: {len(STOCK_LIST['KR'])}개 (주석 해제 시)")
    print(f"{'='*70}\n")
    
    return scheduler


# 수동 실행용 함수
def manual_update():
    """수동으로 주가 업데이트 (테스트용)"""
    init_services()
    update_stock_prices()


if __name__ == "__main__":
    import time
    
    print("=" * 60)
    print("주가 자동 업데이트 스케줄러 테스트")
    print("=" * 60)
    print()
    
    # 즉시 실행 테스트
    print("1. 즉시 업데이트 테스트...")
    manual_update()
    
    print("\n2. 스케줄러 시작...")
    scheduler = start_scheduler()
    
    print("3. 스케줄러 대기 중... (Ctrl+C로 종료)")
    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        print("\n스케줄러 종료 중...")
        scheduler.shutdown()
        print("✅ 스케줄러 종료 완료")
