"""
Decision Stream API Server
백엔드 목업 데이터 제공 서버 + 주가 자동 업데이트
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from datetime import datetime
import random

app = FastAPI(
    title="Decision Stream API",
    description="중기 스윙 투자 시스템 백엔드",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 간단한 API 키 검증
VALID_API_KEY = "ds-test-2026"

def verify_key(key: str = Query(...)):
    if key != VALID_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return key


# ========== 스케줄러 통합 ==========
try:
    from scheduler import start_scheduler, manual_update
    SCHEDULER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  스케줄러 import 실패: {e}")
    SCHEDULER_AVAILABLE = False
    start_scheduler = None
    manual_update = None

@app.on_event("startup")
async def startup_event():
    """서버 시작 시 스케줄러 시작"""
    print("\n🚀 서버 시작 중...")
    if SCHEDULER_AVAILABLE:
        try:
            start_scheduler()
            print("✅ 스케줄러 초기화 완료\n")
        except Exception as e:
            print(f"⚠️  스케줄러 시작 실패: {e}\n")
    else:
        print("⚠️  스케줄러 사용 불가 (import 실패)\n")


@app.post("/api/prices/refresh")
async def refresh_prices(key: str = Query(...)):
    """
    주가 수동 새로고침
    (매일 오후 6시 자동 업데이트 외에 수동 실행 가능)
    """
    verify_key(key)
    
    if not SCHEDULER_AVAILABLE or manual_update is None:
        raise HTTPException(status_code=503, detail="스케줄러 사용 불가")
    
    try:
        manual_update()
        return {
            "message": "주가 업데이트 완료",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"주가 업데이트 실패: {str(e)}")


# ========== Models ==========
class RegimeResponse(BaseModel):
    state: str
    risk_score: float
    playbook: str
    drivers: List[str]


class SectorItem(BaseModel):
    sector: str
    flow_score: float
    flow_signal: str
    duration: str


class StockItem(BaseModel):
    ticker: str
    name: Optional[str] = None
    scores: Optional[Dict[str, float]] = None


class FunnelResponse(BaseModel):
    leader: List[StockItem]
    follower: List[StockItem]
    no_go: List[StockItem]
    disabled: Optional[bool] = False
    reason: Optional[str] = None


class ChecklistResponse(BaseModel):
    marks: Dict[str, str]
    note: str


class NoGoReportResponse(BaseModel):
    reasons: List[str]
    conclusion: str


class TradePlanResponse(BaseModel):
    entry: Dict[str, str]
    stop_loss: str
    targets: List[str]
    position_size: str


class ElitePreCommitResponse(BaseModel):
    summary: str
    score: int
    warnings: List[str]


class TradePlanRequest(BaseModel):
    market: str  # KR or US
    sector: str
    ticker: str
    name: str
    current_price: float
    period: str  # 단기 or 중기
    risk: str  # 보수, 중립, 공격
    capital: float


class TradePlanDetailResponse(BaseModel):
    entry_price: float
    stop_loss: float
    target_1: float
    target_2: float
    quantity: int
    position_size: float
    actual_investment: float
    max_loss: float
    expected_profit: float
    risk_reward_ratio: float
    checklist: List[Dict[str, Any]]
    risk_warning: str
    total_score: int


class SimulationHistoryResponse(BaseModel):
    id: str
    date: str
    market: str
    sector: str
    ticker: str
    name: str
    entry_price: float
    stop_loss: float
    target_1: float
    risk: str
    period: str
    status: str  # 진행중, 익절, 손절
    pnl_percent: Optional[float] = None


# ========== Mock Data ==========
MOCK_REGIME = {
    "state": "RISK_ON",
    "risk_score": 7.2,
    "playbook": "공격적 진입",
    "drivers": ["금리 안정", "외국인 순매수", "VIX 하락"]
}

MOCK_SECTORS = [
    {"sector": "방산", "flow_score": 8.5, "flow_signal": "SURGE", "duration": "3주 지속"},
    {"sector": "에너지", "flow_score": 7.2, "flow_signal": "SURGE", "duration": "2주 지속"},
    {"sector": "신기술", "flow_score": 6.8, "flow_signal": "NORMAL", "duration": "1주"},
    {"sector": "헬스케어", "flow_score": 5.5, "flow_signal": "NORMAL", "duration": "2일"},
    {"sector": "금융", "flow_score": 4.2, "flow_signal": "NORMAL", "duration": "신호 없음"},
]

MOCK_FUNNEL = {
    "방산": {
        "leader": [
            {"ticker": "012450", "name": "한화에어로스페이스", "scores": {"flow": 8.5, "structure": 7.8, "risk": 6.2}},
            {"ticker": "079550", "name": "LIG넥스원", "scores": {"flow": 8.2, "structure": 7.5, "risk": 6.5}},
        ],
        "follower": [
            {"ticker": "272210", "name": "한화시스템", "scores": {"flow": 7.0, "structure": 6.8, "risk": 7.0}},
        ],
        "no_go": [
            {"ticker": "000000", "name": "샘플종목", "scores": {"flow": 3.5, "structure": 4.2, "risk": 2.8}},
        ]
    },
    "에너지": {
        "leader": [
            {"ticker": "010120", "name": "LS전선", "scores": {"flow": 7.8, "structure": 7.2, "risk": 6.8}},
        ],
        "follower": [
            {"ticker": "001770", "name": "SHD", "scores": {"flow": 6.5, "structure": 6.2, "risk": 7.2}},
        ],
        "no_go": []
    },
    "신기술": {
        "leader": [],
        "follower": [
            {"ticker": "005930", "name": "삼성전자", "scores": {"flow": 6.2, "structure": 7.8, "risk": 8.5}},
        ],
        "no_go": []
    }
}

MOCK_CHECKLIST = {
    "marks": {
        "가격 구조": "✔",
        "거래대금": "✔",
        "외국인 수급": "✔",
        "기관 수급": "✔",
        "뉴스 확정성": "✔",
        "섹터 강도": "✔",
        "변동성": "✘",
        "과열 여부": "✔"
    },
    "note": "7개 항목 통과. 매수 적기."
}

MOCK_NOGO_REPORT = {
    "reasons": [
        "최근 10일간 거래대금 급증 후 급락",
        "외국인 및 기관 순매도 전환",
        "뉴스 과열 후 실적 지연 우려",
        "기술적 지지선 하향 이탈"
    ],
    "conclusion": "단기 과열 후 조정 국면. 진입 시 손실 확률 높음."
}

MOCK_PLAN = {
    "entry": {
        "breakout": "55,000원",
        "pullback": "52,000원"
    },
    "stop_loss": "48,000원",
    "targets": ["57,000원", "60,000원", "65,000원"],
    "position_size": "총자산의 20%"
}

MOCK_ELITE_PRECOMMIT = {
    "summary": "종합 검증 점수 82점. 진입 조건 충족.",
    "score": 82,
    "warnings": [
        "시장 변동성 증가 주의",
        "손절선 엄수 필수"
    ]
}


# ========== API Endpoints ==========

@app.get("/")
def root():
    return {
        "service": "Decision Stream API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/regime", response_model=RegimeResponse)
def get_regime(key: str = Query(...)):
    verify_key(key)
    return MOCK_REGIME


@app.get("/sectors", response_model=List[SectorItem])
def get_sectors(key: str = Query(...)):
    verify_key(key)
    return MOCK_SECTORS


@app.get("/funnel", response_model=FunnelResponse)
def get_funnel(
    sector: str = Query(..., description="섹터 이름"),
    key: str = Query(...)
):
    verify_key(key)
    
    if sector not in MOCK_FUNNEL:
        return FunnelResponse(
            leader=[],
            follower=[],
            no_go=[],
            disabled=True,
            reason=f"'{sector}' 섹터 데이터가 없습니다."
        )
    
    data = MOCK_FUNNEL[sector]
    return FunnelResponse(
        leader=data["leader"],
        follower=data["follower"],
        no_go=data["no_go"]
    )


@app.get("/checklist", response_model=ChecklistResponse)
def get_checklist(
    ticker: str = Query(..., description="종목 코드"),
    sector: str = Query(..., description="섹터 이름"),
    key: str = Query(...)
):
    verify_key(key)
    return MOCK_CHECKLIST


@app.get("/nogo_report", response_model=NoGoReportResponse)
def get_nogo_report(
    ticker: str = Query(..., description="종목 코드"),
    sector: str = Query(..., description="섹터 이름"),
    key: str = Query(...)
):
    verify_key(key)
    return MOCK_NOGO_REPORT


@app.get("/plan", response_model=TradePlanResponse)
def get_trade_plan(key: str = Query(...)):
    verify_key(key)
    return MOCK_PLAN


@app.get("/elite/precommit", response_model=ElitePreCommitResponse)
def elite_precommit_check(key: str = Query(...)):
    verify_key(key)
    return MOCK_ELITE_PRECOMMIT


@app.get("/market_intelligence")
def get_market_intelligence(key: str = Query(...)):
    verify_key(key)
    return {
        "regime": "RISK_ON",
        "summary": "현재 시장은 위험자산 선호 국면입니다.",
        "sectors": "방산 및 에너지 섹터로 자금이 집중되고 있습니다.",
        "strategy": "선도주 눌림 매수 전략이 유효합니다."
    }


# ========== Trade Plan Simulation Endpoints ==========

@app.post("/trade_plan/generate", response_model=TradePlanDetailResponse)
def generate_trade_plan(request: TradePlanRequest, key: str = Query(...)):
    """
    매매 계획 생성 API
    7요소 체크리스트 기반 종합 분석 및 포지션 계산
    """
    verify_key(key)
    
    # Risk-based parameters
    risk_params = {
        '보수': {'stop_loss': 0.08, 'target1': 0.15, 'target2': 0.25, 'position_size': 0.20},
        '중립': {'stop_loss': 0.10, 'target1': 0.20, 'target2': 0.35, 'position_size': 0.25},
        '공격': {'stop_loss': 0.12, 'target1': 0.25, 'target2': 0.45, 'position_size': 0.30}
    }
    
    params = risk_params.get(request.risk, risk_params['보수'])
    
    # Calculate entry with slight buffer (2% below current for better entry)
    entry_price = round(request.current_price * 0.98)
    stop_loss = round(entry_price * (1 - params['stop_loss']))
    target_1 = round(entry_price * (1 + params['target1']))
    target_2 = round(entry_price * (1 + params['target2']))
    
    # Position sizing
    position_value = round(request.capital * params['position_size'])
    quantity = int(position_value / entry_price)
    actual_investment = quantity * entry_price
    
    # P&L calculations
    max_loss = round((entry_price - stop_loss) * quantity)
    # Assume 50% exit at target1, 30% at target2, 20% trailing
    expected_profit = round((target_1 - entry_price) * quantity * 0.5 + 
                           (target_2 - entry_price) * quantity * 0.3)
    
    risk_reward_ratio = round(expected_profit / max_loss, 2) if max_loss > 0 else 0
    
    # 7-factor checklist evaluation (mock scores)
    checklist_items = [
        {
            'name': '수급 신호',
            'pass': random.random() > 0.3,
            'score': random.randint(15, 25),
            'max_score': 25,
            'detail': '외국인/기관 누적 매수 확인'
        },
        {
            'name': '정책/테마',
            'pass': random.random() > 0.4,
            'score': random.randint(18, 30),
            'max_score': 30,
            'detail': '확정·지속·실적연결 뉴스'
        },
        {
            'name': '시장 사이클',
            'pass': random.random() > 0.2,
            'score': random.randint(6, 10),
            'max_score': 10,
            'detail': 'MA20 상향, 변동성 정상'
        },
        {
            'name': '기업 질',
            'pass': random.random() > 0.3,
            'score': random.randint(6, 10),
            'max_score': 10,
            'detail': '부채비율, 실적 안정성'
        },
        {
            'name': '서사 (Narrative)',
            'pass': random.random() > 0.5,
            'score': random.randint(4, 8),
            'max_score': 8,
            'detail': '장기 성장 스토리 존재'
        },
        {
            'name': '하방 리스크',
            'pass': random.random() > 0.6,
            'score': random.randint(5, 10),
            'max_score': 10,
            'detail': '과열 신호 없음 확인'
        },
        {
            'name': '시간 적합성',
            'pass': random.random() > 0.4,
            'score': random.randint(4, 7),
            'max_score': 7,
            'detail': '조정 후 진입 구간'
        }
    ]
    
    total_score = sum(item['score'] for item in checklist_items)
    pass_count = sum(1 for item in checklist_items if item['pass'])
    
    # Risk warning based on checklist
    if total_score >= 70 and pass_count >= 6:
        risk_warning = '✅ 체크리스트 통과! 손절가를 엄수하고 20일선 기준으로 관리하세요.'
    elif total_score >= 55 and pass_count >= 4:
        risk_warning = '⚠️ 일부 조건 미달. 포지션 크기를 줄이고 신중하게 접근하세요.'
    else:
        risk_warning = '🚫 진입 조건 미달! 관망을 권장합니다.'
    
    return TradePlanDetailResponse(
        entry_price=entry_price,
        stop_loss=stop_loss,
        target_1=target_1,
        target_2=target_2,
        quantity=quantity,
        position_size=params['position_size'],
        actual_investment=actual_investment,
        max_loss=max_loss,
        expected_profit=expected_profit,
        risk_reward_ratio=risk_reward_ratio,
        checklist=checklist_items,
        risk_warning=risk_warning,
        total_score=total_score
    )


@app.get("/trade_plan/stocks")
def get_stocks_by_sector(
    sector: str = Query(..., description="섹터 이름"),
    key: str = Query(...)
):
    """
    섹터별 종목 리스트 제공
    """
    verify_key(key)
    
    stock_database = {
        '반도체': [
            {'ticker': '005930', 'name': '삼성전자', 'price': 75000},
            {'ticker': '000660', 'name': 'SK하이닉스', 'price': 142000},
            {'ticker': '042700', 'name': '한미반도체', 'price': 85000}
        ],
        '2차전지': [
            {'ticker': '373220', 'name': 'LG에너지솔루션', 'price': 450000},
            {'ticker': '096770', 'name': 'SK이노베이션', 'price': 145000},
            {'ticker': '051910', 'name': 'LG화학', 'price': 380000}
        ],
        '바이오': [
            {'ticker': '207940', 'name': '삼성바이오로직스', 'price': 850000},
            {'ticker': '068270', 'name': '셀트리온', 'price': 175000},
            {'ticker': '326030', 'name': 'SK바이오팜', 'price': 92000}
        ],
        '자동차': [
            {'ticker': '005380', 'name': '현대자동차', 'price': 235000},
            {'ticker': '000270', 'name': '기아', 'price': 98000},
            {'ticker': '012330', 'name': '현대모비스', 'price': 265000}
        ],
        '화학': [
            {'ticker': '051910', 'name': 'LG화학', 'price': 380000},
            {'ticker': '009830', 'name': '한화솔루션', 'price': 42000},
            {'ticker': '011170', 'name': '롯데케미칼', 'price': 145000}
        ],
        '조선': [
            {'ticker': '009540', 'name': '한국조선해양', 'price': 145000},
            {'ticker': '010140', 'name': '삼성중공업', 'price': 9800},
            {'ticker': '042660', 'name': '한화오션', 'price': 31000}
        ],
        '방산': [
            {'ticker': '012450', 'name': '한화에어로스페이스', 'price': 185000},
            {'ticker': '079550', 'name': 'LIG넥스원', 'price': 528000},
            {'ticker': '272210', 'name': '한화시스템', 'price': 28000}
        ]
    }
    
    return stock_database.get(sector, [])


@app.get("/trade_plan/stats")
def get_simulation_stats(key: str = Query(...)):
    """
    시뮬레이션 통계 조회
    """
    verify_key(key)
    
    # Mock statistics
    return {
        'total_simulations': random.randint(10, 50),
        'win_rate': round(random.uniform(45, 65), 1),
        'avg_return': round(random.uniform(2, 12), 1),
        'profit_ratio': round(random.uniform(1.5, 2.8), 1),
        'best_trade': {
            'ticker': '012450',
            'name': '한화에어로스페이스',
            'return': 28.5
        },
        'worst_trade': {
            'ticker': '000000',
            'name': '샘플종목',
            'return': -8.2
        }
    }


# ========== Technical Analysis Endpoints ==========

@app.get("/api/chart/{ticker}")
async def get_chart_analysis(ticker: str, key: str = Query(...)):
    """
    종목 차트 데이터 및 기술적 분석 결과 제공
    """
    verify_key(key)
    
    try:
        # 실제로는 services/technical_analysis_service.py를 호출
        # from services.technical_analysis_service import TechnicalAnalysisService
        # service = TechnicalAnalysisService()
        # result = service.analyze_stock(ticker)
        
        # 목업 데이터 반환
        return generate_mock_chart_data(ticker)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/price/{ticker}")
async def get_current_price(ticker: str, key: str = Query(...)):
    """
    실시간 현재가 조회
    """
    verify_key(key)
    
    # 실제 구현:
    # from services.korea_investment_api import KoreaInvestmentAPI
    # api = KoreaInvestmentAPI()
    # return api.get_current_price(ticker)
    
    # 목업 데이터
    stock_prices = {
        '005930': 75000,
        '012450': 185000,
        'LMT': 445.50,
        'JNJ': 158.25
    }
    
    price = stock_prices.get(ticker, 100000)
    
    return {
        'ticker': ticker,
        'current_price': price,
        'change': round(random.uniform(-3, 5), 2),
        'change_percent': round(random.uniform(-2, 3), 2),
        'volume': random.randint(1000000, 10000000),
        'timestamp': datetime.now().isoformat()
    }


def generate_mock_chart_data(ticker: str):
    """차트 분석용 목업 데이터 생성"""
    import random
    from datetime import datetime, timedelta
    
    # 기준가
    base_prices = {
        '005930': 75000,
        '012450': 185000,
        'LMT': 445.50,
        'JNJ': 158.25
    }
    
    base_price = base_prices.get(ticker, 100000)
    
    # 120일 가격 데이터 생성
    dates = []
    prices = []
    opens = []
    highs = []
    lows = []
    closes = []
    volumes = []
    
    current_price = base_price
    
    for i in range(120):
        date = datetime.now() - timedelta(days=120-i)
        dates.append(date.strftime('%Y-%m-%d'))
        
        # OHLC 데이터 생성
        change = random.uniform(-0.03, 0.03)
        open_price = current_price
        close_price = current_price * (1 + change)
        high_price = max(open_price, close_price) * random.uniform(1.0, 1.02)
        low_price = min(open_price, close_price) * random.uniform(0.98, 1.0)
        
        opens.append(round(open_price, 2))
        closes.append(round(close_price, 2))
        highs.append(round(high_price, 2))
        lows.append(round(low_price, 2))
        prices.append(round(close_price, 2))
        volumes.append(random.randint(5000000, 15000000))
        
        current_price = close_price
    
    # 이동평균 계산
    ma5 = []
    ma20 = []
    ma60 = []
    
    for i in range(len(prices)):
        if i >= 4:
            ma5.append(round(sum(prices[i-4:i+1]) / 5, 2))
        else:
            ma5.append(None)
        
        if i >= 19:
            ma20.append(round(sum(prices[i-19:i+1]) / 20, 2))
        else:
            ma20.append(None)
        
        if i >= 59:
            ma60.append(round(sum(prices[i-59:i+1]) / 60, 2))
        else:
            ma60.append(None)
    
    # RSI 계산 (간단 버전)
    rsi = round(random.uniform(30, 70), 1)
    
    # 기술적 지표
    current = prices[-1]
    macd_signal = "매수" if random.random() > 0.5 else "중립"
    short_trend = "상승" if ma5[-1] and ma5[-1] > ma20[-1] else "하락"
    mid_trend = "상승" if ma20[-1] and ma20[-1] > ma60[-1] else "하락"
    
    support = round(min(prices[-20:]) * 0.98, 2)
    resistance = round(max(prices[-20:]) * 1.02, 2)
    
    # 캔들 패턴
    patterns = []
    if random.random() > 0.7:
        patterns.append("골든크로스")
    if random.random() > 0.8:
        patterns.append("역망치형")
    
    # 추천
    if rsi < 30 and short_trend == "상승":
        recommendation = "매수 신호 - 과매도 구간에서 반등 시작"
        signal = "BUY"
    elif rsi > 70 and short_trend == "하락":
        recommendation = "관망 신호 - 과매수 구간 조정 가능성"
        signal = "HOLD"
    else:
        recommendation = "중립 - 추세 확인 필요"
        signal = "NEUTRAL"
    
    # 요약
    summary = f"{ticker} 종목은 현재 {short_trend} 추세입니다. "
    summary += f"RSI {rsi}로 "
    if rsi < 30:
        summary += "과매도 상태이며, "
    elif rsi > 70:
        summary += "과매수 상태이며, "
    else:
        summary += "중립 구간이며, "
    
    summary += f"지지선 {support:,}, 저항선 {resistance:,}을 주시하세요."
    
    return {
        'ticker': ticker,
        'dates': dates,
        'opens': opens,
        'highs': highs,
        'lows': lows,
        'closes': closes,
        'prices': prices,
        'volumes': volumes,
        'ma5': ma5,
        'ma20': ma20,
        'ma60': ma60,
        'indicators': {
            'current_price': current,
            'rsi': rsi,
            'macd': macd_signal,
            'short_trend': short_trend,
            'mid_trend': mid_trend,
            'support': support,
            'resistance': resistance,
            'patterns': patterns
        },
        'recommendation': recommendation,
        'signal': signal,
        'summary': summary
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server:app",
        host="127.0.0.1",
        port=8125,
        reload=True,
        log_level="info"
    )
