"""
매일 오후 6시 주가 자동 업데이트 스케줄러
"""

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import json
import os
import sys

# 상위 디렉토리의 services 모듈 import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.korea_investment_api import KoreaInvestmentAPI
from services.nh_stock_api import NHStockAPI
from services.krx_stock_api import KRXStockAPI
from services.us_stock_service import USStockService

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


def init_services():
    """API 서비스 초기화"""
    global kr_api, us_service
    
    # 한국 주식: KRX API 우선 시도
    try:
        kr_api = KRXStockAPI()
        print("✅ 한국거래소(KRX) API 초기화 완료")
    except Exception as e:
        print(f"⚠️  KRX API 초기화 실패: {e}")
        # NH투자증권 API로 fallback
        try:
            kr_api = NHStockAPI()
            print("✅ NH투자증권 API 초기화 완료 (fallback)")
        except Exception as e2:
            print(f"⚠️  NH API 초기화 실패: {e2}")
            # 한국투자증권 API로 최종 fallback
            try:
                kr_api = KoreaInvestmentAPI()
                print("✅ 한국투자증권 API 초기화 완료 (fallback)")
            except Exception as e3:
                print(f"⚠️  모든 한국 API 초기화 실패")
                kr_api = None
    
    try:
        us_service = USStockService()
        print("✅ 미국 주식 서비스 초기화 완료")
    except Exception as e:
        print(f"⚠️  미국 주식 서비스 초기화 실패: {e}")
        us_service = None


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
    
    # 매일 오후 6시 실행
    scheduler.add_job(
        update_stock_prices,
        'cron',
        hour=18,
        minute=0,
        id='daily_price_update',
        replace_existing=True
    )
    
    scheduler.start()
    
    print(f"\n{'='*60}")
    print("🕐 스케줄러 시작됨")
    print("⏰ 실행 시간: 매일 오후 6시 (18:00)")
    print("📊 대상 종목:")
    print(f"   - 미국 주식: {len(STOCK_LIST['US'])}개")
    print(f"   - 한국 주식: {len(STOCK_LIST['KR'])}개")
    print(f"   - 총 {len(STOCK_LIST['US']) + len(STOCK_LIST['KR'])}개 종목")
    print(f"{'='*60}\n")
    
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
