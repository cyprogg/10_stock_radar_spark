from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import os
from datetime import date, datetime
import traceback
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# AI Agent imports
from agents.orchestrator import AgentOrchestrator
from services.agent_data_provider import AgentDataProvider
from services.krx_stock_api import KRXStockAPI

# Database imports
from database import init_db, get_db

# Router imports
from routers.auth import router as auth_router
from dependencies.auth import get_current_user

# -----------------------
# Config
# -----------------------
ACCESS_KEY = "ds-test-2026"

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("stock_radar")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(BASE_DIR, "..")  # 상위 디렉토리 (index.html 위치)

app = FastAPI(
    title="Stock Radar Spark | AI 투자 분석 시스템",
    description="5개 AI Agent 기반 주식 분석 플랫폼",
    version="1.0.0-beta"
)

# -----------------------
# Database 초기화
# -----------------------
try:
    init_db()
    logger.info("✅ 데이터베이스 초기화 완료")
except Exception as e:
    logger.error(f"⚠️ 데이터베이스 초기화 실패: {e}")

# -----------------------
# 인증 라우터 마운트
# -----------------------
app.include_router(auth_router)

# -----------------------
# AI Agent 초기화
# -----------------------
try:
    agent_orchestrator = AgentOrchestrator()
    agent_data_provider = AgentDataProvider(use_real_us_data=True)  # 실시간 미국 주식 데이터 사용
    krx_api = KRXStockAPI()  # 한국거래소 API (20분 지연)
    logger.info("✅ AI Agent 시스템 초기화 완료")
    logger.info("✅ KRX API 초기화 완료 (한국 주식 20분 지연 시세)")
except Exception as e:
    logger.error(f"⚠️ AI Agent 초기화 실패: {e}")
    agent_orchestrator = None
    agent_data_provider = None
    krx_api = None

# -----------------------
# CORS
# -----------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------
# Access Key Middleware
# -----------------------
@app.middleware("http")
async def keycheck(req: Request, call_next):
    # Allow HTML files without key
    if req.url.path == "/" or req.url.path.endswith(".html") or req.url.path.endswith(".css") or req.url.path.endswith(".js"):
        return await call_next(req)
    
    # Allow public APIs without key
    if req.url.path.startswith("/api/chart/") or req.url.path.startswith("/api/health") or req.url.path.startswith("/api/status"):
        return await call_next(req)
    
    # Allow auth endpoints without key
    if req.url.path.startswith("/api/auth/"):
        return await call_next(req)

    client_key = req.query_params.get("key")
    if client_key != ACCESS_KEY:
        return JSONResponse(status_code=403, content={"error": "Invalid API key"})
    return await call_next(req)

# -----------------------
# Index & Static HTML
# -----------------------
@app.get("/")
def root():
    index_path = os.path.join(WEB_DIR, "index.html")
    if not os.path.exists(index_path):
        return JSONResponse(status_code=404, content={"error": "index.html not found"})
    return FileResponse(index_path)

@app.get("/agent_test.html")
def agent_test():
    """AI Agent 테스트 페이지"""
    agent_test_path = os.path.join(WEB_DIR, "agent_test.html")
    if not os.path.exists(agent_test_path):
        return JSONResponse(status_code=404, content={"error": "agent_test.html not found"})
    return FileResponse(agent_test_path)

# -----------------------
# Utils / Mock Data
# -----------------------
def score(s: str) -> int:
    """간단한 점수 생성 함수 (Mock용)"""
    return sum(ord(c) for c in s) % 100

SECTORS = ["방산", "헬스케어", "AI 반도체", "전력", "에너지"]

STOCKS = {
    "방산": [
        {"ticker": "LMT", "name": "Lockheed Martin", "price": 649.81},
        {"ticker": "012450", "name": "한화에어로스페이스", "price": 1149000},
        {"ticker": "079550", "name": "LIG넥스원", "price": 463000}
    ],
    "헬스케어": [
        {"ticker": "JNJ", "name": "Johnson & Johnson", "price": 244.99},
        {"ticker": "207940", "name": "삼성바이오로직스", "price": 1720000},
        {"ticker": "068270", "name": "셀트리온", "price": 244500}
    ],
    "AI 반도체": [
        {"ticker": "005930", "name": "삼성전자", "price": 190000},
        {"ticker": "NVDA", "name": "NVIDIA", "price": 187.98}
    ],
    "전력": [
        {"ticker": "NEE", "name": "NextEra Energy", "price": 58.30},
        {"ticker": "015760", "name": "한국전력", "price": 23500}
    ],
    "에너지": [
        {"ticker": "XOM", "name": "Exxon Mobil", "price": 112.50}
    ]
}

CHECKLIST_ITEMS = [
    "가격 구조 (과열/이격 없음)",
    "거래량 정상",
    "변동성 안정",
    "이벤트 리스크 없음",
    "구조적 눌림 구간"
]

# -----------------------
# 모니터링 API (인증 불필요)
# -----------------------

@app.get("/api/health")
async def health_check():
    """
    시스템 헬스 체크
    - 데이터베이스 상태
    - Agent 시스템 상태
    - API 서비스 상태
    """
    db_ok = False
    agent_ok = agent_orchestrator is not None
    
    try:
        db = next(get_db())
        db.execute("SELECT 1")
        db_ok = True
        db.close()
    except:
        db_ok = False
    
    all_ok = db_ok and agent_ok
    status_code = "healthy" if all_ok else "degraded"
    
    return {
        "status": status_code,
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "database": "ok" if db_ok else "error",
            "ai_agents": "ok" if agent_ok else "error",
            "api_server": "ok"
        }
    }


@app.get("/api/status")
async def status():
    """
    시스템 상태 상세 정보
    베타테스터 모니터링용
    """
    return {
        "app_name": "Stock Radar Spark",
        "version": "1.0.0-beta",
        "environment": "development" if os.getenv("DEBUG") == "true" else "production",
        "timestamp": datetime.utcnow().isoformat(),
        "active_users": "베타테스터 5명 제한",
        "database": {
            "type": "SQLite (development)" if "sqlite" in os.getenv("DATABASE_URL", "") else "PostgreSQL",
            "status": "running"
        },
        "ai_agents": {
            "market_regime": agent_orchestrator is not None,
            "sector_scout": agent_orchestrator is not None,
            "stock_screener": agent_orchestrator is not None,
            "trade_plan_builder": agent_orchestrator is not None,
            "devils_advocate": agent_orchestrator is not None
        },
        "data_sources": {
            "yahoo_finance": "active",
            "opendart_api": bool(os.getenv("OPENDART_API_KEY")),
            "krx_api": "20분 지연"
        }
    }

# -----------------------
# Core APIs
# -----------------------

@app.get("/regime")
def regime():
    """Market Regime API"""
    return {
        "date": str(date.today()),
        "state": "RISK_ON",
        "score": 2,
        "max_score": 3,
        "playbook": "눌림 매수 허가",
        "factors": {
            "breadth": True,
            "volatility": True,
            "theme": False
        },
        "note": "Risk_ON = 사도 죽지 않을 확률이 높다",
        "detail": {
            "breadth_ratio": "1.3:1 (상승 650, 하락 500)",
            "vkospi": 18,
            "lasting_themes": ["방산"]
        }
    }


@app.get("/sectors")
def sectors():
    """Sector Heatmap API"""
    out = []
    for s in SECTORS:
        sc = score(s)
        # 방산과 헬스케어를 SURGE로 고정
        if s in ["방산", "헬스케어"]:
            flow_score = 97 if s == "방산" else 96
            signal = "SURGE"
            duration = "2주 지속" if s == "방산" else "1주 지속"
        else:
            flow_score = 40 + (sc % 20)
            signal = "NORMAL"
            duration = "-"
        
        out.append({
            "sector": s,
            "flow_score": flow_score,
            "flow_signal": signal,
            "duration": duration
        })
    
    return sorted(out, key=lambda x: x["flow_score"], reverse=True)


@app.get("/funnel")
def funnel(sector: str):
    """Stock Funnel API"""
    stocks = STOCKS.get(sector, [])
    
    leader = []
    follower = []
    no_go = []
    
    for stock in stocks:
        s = score(stock["ticker"])
        
        # 섹터별 특정 분류 (데모용)
        if sector == "방산":
            # 방산: Follower만 (LMT, 한화에어로)
            follower.append(stock)
        elif sector == "헬스케어":
            # 헬스케어: JNJ는 Leader, 나머지 Follower
            if stock["ticker"] == "JNJ":
                leader.append(stock)
            else:
                follower.append(stock)
        else:
            # 다른 섹터: 점수로 분류
            if s >= 70:
                leader.append(stock)
            elif s >= 40:
                follower.append(stock)
            else:
                no_go.append(stock)
    
    return {
        "leader": leader,
        "follower": follower,
        "no_go": no_go
    }


@app.get("/checklist")
def checklist(ticker: str, sector: str):
    """Watch & Checklist API"""
    base = score(ticker + sector)
    
    checks = {}
    for i, item in enumerate(CHECKLIST_ITEMS):
        v = (base + i * 13) % 100
        checks[item] = v >= 60  # 60% 이상이면 통과
    
    pass_count = sum(checks.values())
    
    # Checklist Level 결정
    if pass_count == 5:
        level = "Strong"
    elif pass_count == 4:
        level = "Medium"
    else:
        level = "Weak"
    
    return {
        "ticker": ticker,
        "sector": sector,
        "checks": checks,
        "pass_count": pass_count,
        "level": level,
        "note": "사면 안 되는 이유를 체크합니다."
    }


@app.get("/nogo_report")
def nogo_report(ticker: str, sector: str):
    """No-Go 탈락 사유 API"""
    base = score(ticker + sector)
    reasons = []

    if base % 5 < 2:
        reasons.append("자금 흐름: 최근 수급 약화")
    if base % 7 < 3:
        reasons.append("모멘텀: 중기 추세 하락")
    if base % 9 < 4:
        reasons.append("섹터 내 상대강도 하위")
    if base % 11 < 5:
        reasons.append("변동성 증가로 리스크 확대")
    if base % 13 < 6:
        reasons.append("기술적 구조 불안정")

    # 최소 2개는 표시
    if len(reasons) < 2:
        reasons.append("구조: 현재 국면과 시간 부적합")

    return {
        "ticker": ticker,
        "sector": sector,
        "reasons": reasons,
        "conclusion": "현재 Market Regime에서는 매수 확률이 통계적으로 불리합니다."
    }


@app.get("/market_intelligence")
def market_intelligence():
    """Market Intelligence (시장 해설) API"""
    r = regime()
    s = sectors()
    
    surge_sectors = [x for x in s if x["flow_signal"] == "SURGE"]
    
    script = f"현재 시장은 {r['state']} 국면이며, 자금이 {', '.join([x['sector'] for x in surge_sectors])} 섹터로 집중되고 있습니다.\n\n"
    script += f"방산 섹터는 2주째 SURGE 신호를 유지하고 있으며, Lockheed Martin과 한화에어로스페이스가 Follower로 분류됩니다.\n\n"
    script += f"전략: 눌림 매수 대기. 20일선 지지 확인 후 진입을 권장합니다."
    
    return {
        "script": script
    }


# -----------------------
# DS-Anchor Script Generator
# -----------------------
@app.get("/generate_ds_anchor_script")
def generate_ds_anchor_script():
    """DS-Anchor 대본 생성 (10분 뉴스+교육 톤)"""
    r = regime()
    s = sectors()

    surge_sectors = [x for x in s if x["flow_signal"] == "SURGE"]
    top_sectors = surge_sectors[:2] if surge_sectors else s[:2]

    leaders_all = []
    followers_all = []
    nogo_all = []

    for sec in top_sectors:
        f = funnel(sec["sector"])
        leaders_all += [(sec["sector"], x["ticker"], x["name"]) for x in f["leader"]]
        followers_all += [(sec["sector"], x["ticker"], x["name"]) for x in f["follower"]]
        nogo_all += [(sec["sector"], x["ticker"], x["name"]) for x in f["no_go"]]

    # 대표 종목 선정
    focus = leaders_all[:2] if leaders_all else followers_all[:2]
    focus_txt = ", ".join([f"{sec} {name}" for sec, tic, name in focus]) if focus else "선도/관찰 종목이 뚜렷하지 않습니다."

    # No-Go 대표
    nogo_pick = nogo_all[:2]
    nogo_txt = ", ".join([f"{sec} {name}" for sec, tic, name in nogo_pick]) if nogo_pick else "금일 No-Go로 분류된 대표 종목은 제한적입니다."

    top_sector_names = ", ".join([x["sector"] for x in top_sectors])
    title = f"DS-Anchor | {r['date']} 오늘의 투자시장 브리핑"

    script = f"""
안녕하세요. DS-Anchor입니다. {r['date']} 오늘의 투자시장을 브리핑합니다.

1) 오늘의 시장 상태입니다.
오늘 시장은 {r['state']} 국면으로 요약됩니다.
Risk Score는 {r['score']}/{r['max_score']}이며, 운영 원칙은 '{r['playbook']}'입니다.

여기서 중요한 점은, {r['state']}라고 해서 모든 종목을 사도 된다는 뜻은 아니라는 점입니다.
Risk-On은 "사도 죽지 않을 확률이 높다"는 의미이지, 무조건 수익을 보장하는 신호가 아닙니다.

2) 섹터 흐름입니다.
오늘 시스템이 포착한 상위 섹터는 {top_sector_names}입니다.
SURGE는 단순한 상승이 아니라, 짧은 기간에 자금이 집중되고 있음을 의미합니다.

이 조합은 우연이 아닙니다.
• 공격 자금 → 방산 (지정학 리스크를 수익으로 전환)
• 방어 자금 → 헬스케어 (경기 둔화 대비 현금흐름)

지금 시장은 "전쟁·금리 피크·경기 둔화"를 동시에 반영하고 있습니다.

3) 종목 Funnel 요약입니다.
오늘의 포커스 후보는 {focus_txt}입니다.

방산 섹터의 구조가 특히 중요합니다.
섹터는 이미 달리고 있는데, 종목은 아직 본격 돌파 전입니다.
이게 가장 수익률이 높은 단계입니다.

일반적인 순서:
1) 섹터 자금 유입 ✅
2) Follower 급등 ← 지금 여기
3) Leader 확정
4) 개인들 몰림 → 끝

전략: 돌파 추격이 아니라, 눌림에서 조용히 매집하세요.

반대로 No-Go는 {nogo_txt}입니다.
No-Go는 '나쁜 기업'이 아니라, '현재 국면에서 시간과 구조가 맞지 않는' 경우입니다.

4) Watch & Checklist 중요성
종목을 선택했다고 바로 매수하는 것이 아닙니다.
Watch & Checklist에서 "사면 안 되는 이유"를 체크합니다.

5가지 체크:
• 가격 구조 (과열/이격 없음)
• 거래량 정상
• 변동성 안정
• 이벤트 리스크 없음
• 구조적 눌림 구간

5개 통과 → Strong (선제 매집 가능)
4개 통과 → Medium (관찰 대기)
3개 이하 → Weak (보류)

5) 결론입니다.
오늘 시장은 {r['state']}이지만, 운영 원칙은 명확합니다.

핵심을 기억하세요:
"자금이 몰리는 섹터 안에서, 눌림을 기다리는 장"입니다.

이상 DS-Anchor였습니다.
""".strip()

    return {"title": title, "script": script}


# -----------------------
# AI Agent APIs
# -----------------------

@app.post("/api/agent/analyze")
async def agent_full_analysis(request: Request):
    """
    전체 AI Agent 분석 파이프라인 실행
    
    Request Body:
    {
        "tickers": ["005930", "000660", "012450"],  // 선택
        "sectors": ["반도체", "방산"],              // 선택
        "period": "단기",                           // 단기 | 중기
        "risk_profile": "중립",                    // 보수 | 중립 | 공격
        "account_size": 10000000                   // 선택 (원)
    }
    """
    if not agent_orchestrator or not agent_data_provider:
        return JSONResponse(
            status_code=503,
            content={"error": "AI Agent system not initialized"}
        )
    
    try:
        body = await request.json()
        
        # 1. 데이터 수집
        market_data = agent_data_provider.get_market_data()
        
        # 섹터 데이터
        sectors_param = body.get("sectors", ["반도체", "방산", "2차전지"])
        sectors_data = agent_data_provider.get_sectors_data(sectors_param)
        
        # 종목 데이터
        tickers = body.get("tickers", ["005930", "000660", "012450"])
        stocks_data = agent_data_provider.get_stocks_data(tickers)
        
        # 2. 사용자 프로필
        user_profile = {
            "period": body.get("period", "단기"),
            "risk_profile": body.get("risk_profile", "중립"),
            "account_size": body.get("account_size", 0)
        }
        
        # 3. Agent 실행
        result = agent_orchestrator.run_full_analysis(
            market_data,
            sectors_data,
            stocks_data,
            user_profile
        )
        
        # 4. 결과 저장 (선택)
        if body.get("save_result", False):
            agent_data_provider.save_analysis_result(result)
        
        return result
        
    except Exception as e:
        print(f"❌ Agent 분석 오류: {e}")
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "detail": traceback.format_exc()}
        )


@app.post("/api/agent/quick-analyze")
async def agent_quick_analysis(request: Request):
    """
    단일 종목 빠른 분석 (Agent 1, 3, 4, 5만 실행)
    
    Request Body:
    {
        "ticker": "005930",
        "period": "단기",
        "risk_profile": "중립",
        "account_size": 10000000
    }
    """
    if not agent_orchestrator or not agent_data_provider:
        return JSONResponse(
            status_code=503,
            content={"error": "AI Agent system not initialized"}
        )
    
    try:
        body = await request.json()
        ticker = body.get("ticker")
        
        if not ticker:
            return JSONResponse(
                status_code=400,
                content={"error": "ticker is required"}
            )
        
        # 데이터 수집
        market_data = agent_data_provider.get_market_data()
        stocks_data = agent_data_provider.get_stocks_data([ticker])
        
        if not stocks_data:
            return JSONResponse(
                status_code=404,
                content={"error": f"Stock data not found for {ticker}"}
            )
        
        stock_data = stocks_data[0]
        
        # 사용자 프로필
        user_profile = {
            "period": body.get("period", "단기"),
            "risk_profile": body.get("risk_profile", "중립"),
            "account_size": body.get("account_size", 0)
        }
        
        # 빠른 분석 실행
        result = agent_orchestrator.run_quick_analysis(
            market_data,
            stock_data,
            user_profile
        )
        
        return result
        
    except Exception as e:
        print(f"❌ 빠른 분석 오류: {e}")
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "detail": traceback.format_exc()}
        )


@app.get("/api/agent/market-regime")
def agent_market_regime():
    """
    시장 상태만 빠르게 조회
    """
    if not agent_orchestrator or not agent_data_provider:
        return JSONResponse(
            status_code=503,
            content={"error": "AI Agent system not initialized"}
        )
    
    try:
        market_data = agent_data_provider.get_market_data()
        result = agent_orchestrator.market_analyst.analyze(market_data)
        return result
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.get("/api/agent/sectors")
def agent_sectors():
    """
    AI Agent가 실시간 섹터 분석 (Sector Scout)
    """
    if not agent_orchestrator or not agent_data_provider:
        return JSONResponse(
            status_code=503,
            content={"error": "AI Agent system not initialized"}
        )
    
    try:
        # 한국 주요 섹터
        sectors = ["방산", "헬스케어", "AI 반도체", "전력", "에너지"]
        sectors_data = agent_data_provider.get_sectors_data(sectors)
        
        # Sector Scout Agent 실행
        result = agent_orchestrator.sector_scout.rank_sectors(sectors_data)
        
        # 기존 /sectors 형식으로 변환
        sectors_list = []
        for sector_result in result:
            sectors_list.append({
                "sector": sector_result.get("sector", ""),
                "flow_score": sector_result.get("flow_score", 0),
                "flow_signal": sector_result.get("signal", "NORMAL"),
                "duration": sector_result.get("duration", "-")
            })
        
        return sorted(sectors_list, key=lambda x: x["flow_score"], reverse=True)
        
    except Exception as e:
        print(f"❌ Sector 분석 오류: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.get("/api/agent/funnel")
def agent_funnel(sector: str):
    """
    AI Agent가 섹터별 종목 분류 (Stock Screener)
    Leader, Follower, No-Go 실시간 분류
    """
    if not agent_orchestrator or not agent_data_provider:
        return JSONResponse(
            status_code=503,
            content={"error": "AI Agent system not initialized"}
        )
    
    try:
        # 섹터별 종목 리스트
        stocks_by_sector = {
            "방산": ["LMT", "012450", "079550"],
            "헬스케어": ["JNJ", "207940", "068270"],
            "AI 반도체": ["005930", "NVDA", "000660"],
            "전력": ["NEE", "015760"],
            "에너지": ["XOM"]
        }
        
        tickers = stocks_by_sector.get(sector, [])
        if not tickers:
            return {"leader": [], "follower": [], "no_go": []}
        
        # 종목 데이터 수집
        stocks_data = agent_data_provider.get_stocks_data(tickers)
        
        # Stock Screener Agent 실행
        result = agent_orchestrator.stock_screener.screen_stocks(stocks_data)
        
        # 기존 /funnel 형식으로 변환
        leaders = []
        followers = []
        no_gos = []
        
        for stock in result.get("leaders", []):
            leaders.append({
                "ticker": stock.get("ticker", ""),
                "name": stock.get("name", ""),
                "price": stock.get("price", 0),
                "currency": stock.get("currency", "KRW")
            })
        
        for stock in result.get("followers", []):
            followers.append({
                "ticker": stock.get("ticker", ""),
                "name": stock.get("name", ""),
                "price": stock.get("price", 0),
                "currency": stock.get("currency", "KRW")
            })
        
        for stock in result.get("no_go", []):
            no_gos.append({
                "ticker": stock.get("ticker", ""),
                "name": stock.get("name", ""),
                "price": stock.get("price", 0),
                "currency": stock.get("currency", "KRW"),
                "reason": stock.get("reason", "Not recommended")
            })
        
        return {
            "leader": leaders,
            "follower": followers,
            "no_go": no_gos
        }
        
    except Exception as e:
        print(f"❌ Funnel 분석 오류: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.get("/api/agent/market-intelligence")
def agent_market_intelligence():
    """
    AI Agent가 생성하는 시장 해설 (Market Analyst)
    """
    if not agent_orchestrator or not agent_data_provider:
        return JSONResponse(
            status_code=503,
            content={"error": "AI Agent system not initialized"}
        )
    
    try:
        # 시장 데이터 수집
        market_data = agent_data_provider.get_market_data()
        sectors = ["방산", "헬스케어", "AI 반도체", "전력", "에너지"]
        sectors_data = agent_data_provider.get_sectors_data(sectors)
        
        # Market Analyst에서 상세 해설 생성
        regime_result = agent_orchestrator.market_analyst.analyze(market_data)
        sectors_result = agent_orchestrator.sector_scout.rank_sectors(sectors_data)
        
        # 종합 해설 생성
        script = f"현재 시장은 {regime_result.get('state', 'UNKNOWN')} 국면입니다.\n\n"
        
        # SURGE 섹터 찾기
        surge_sectors = [s for s in sectors_result if s.get("signal") == "SURGE"]
        if surge_sectors:
            sector_names = [s.get("sector", "") for s in surge_sectors]
            script += f"자금이 {', '.join(sector_names)} 섹터로 집중되고 있습니다.\n\n"
        
        # Playbook 추가
        script += f"전략: {regime_result.get('playbook', '관망')}\n"
        
        return {"script": script}
        
    except Exception as e:
        print(f"❌ Market Intelligence 생성 오류: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


# -----------------------
# Chart Analysis (Real Data)
# -----------------------
def _format_summary(name, price, currency, short_trend, mid_trend, ma20, ma60):
    """Summary 텍스트 생성"""
    if currency == 'USD':
        price_str = f"${price:.2f}"
        ma20_str = f"${ma20:.2f}"
        ma60_str = f"${ma60:.2f}"
    else:
        price_str = f"{int(price):,}원"
        ma20_str = f"{int(ma20):,}원"
        ma60_str = f"{int(ma60):,}원"
    
    return f"""{name} 실시간 분석

현재가: {price_str}
단기 추세: {short_trend}
중기 추세: {mid_trend}
MA20: {ma20_str}
MA60: {ma60_str}"""

@app.get("/api/chart/{ticker}")
async def get_chart_data(ticker: str):
    """
    차트 분석용 실시간 데이터 제공
    - 한국 주식 (6자리 숫자): Yahoo Finance (.KS) 사용 (15분 지연)
    - 미국 주식 (알파벳): Yahoo Finance 사용 (15분 지연)
    """
    if not agent_data_provider:
        return JSONResponse(
            status_code=503,
            content={"error": "Agent system not initialized"}
        )
    
    try:
        # 한국 주식 vs 미국 주식 자동 감지
        is_korean_stock = ticker.isdigit() and len(ticker) == 6
        
        if is_korean_stock:
            # 한국 주식: Yahoo Finance 사용 (종목코드.KS)
            yahoo_ticker = f"{ticker}.KS"
            
            if agent_data_provider.us_stock_service:
                try:
                    # Yahoo Finance로 한국 주식 조회
                    kr_price_data = agent_data_provider.us_stock_service.get_current_price(yahoo_ticker)
                    
                    stock_data = {
                        'ticker': ticker,
                        'name': kr_price_data.get('name', ticker),
                        'current_price': kr_price_data.get('price', 0),
                        'change_rate': kr_price_data.get('change_percent', 0),
                        'volume': kr_price_data.get('volume', 0),
                        'currency': 'KRW',
                        'ma20': kr_price_data.get('ma20', 0),
                        'ma60': kr_price_data.get('ma60', 0)
                    }
                    currency = 'KRW'
                    real_ticker = yahoo_ticker  # Historical 데이터용
                except Exception as e:
                    return JSONResponse(
                        status_code=500,
                        content={"error": f"Yahoo Finance (KR) error: {str(e)}"}
                    )
            else:
                return JSONResponse(
                    status_code=503,
                    content={"error": "US stock service not available"}
                )
        else:
            # 미국 주식: 기존 로직 사용
            stocks_data = agent_data_provider.get_stocks_data([ticker])
            
            if not stocks_data:
                return JSONResponse(
                    status_code=404,
                    content={"error": f"Stock data not found for {ticker}"}
                )
            
            stock_data = stocks_data[0]
            currency = stock_data.get('currency', 'USD')
            real_ticker = ticker
        
        # Historical 데이터 가져오기
        dates = []
        prices = []
        ma5 = []
        ma20_arr = []
        ma60_arr = []
        
        # Yahoo Finance로 historical 데이터 가져오기 (한국/미국 모두)
        if agent_data_provider.us_stock_service:
            try:
                # 120일 historical 데이터
                daily_data = agent_data_provider.us_stock_service.get_daily_data(real_ticker, period="6mo")
                
                for i, day in enumerate(daily_data[-120:]):
                    dates.append(day['date'])
                    prices.append(day['close'])
                    
                    # MA 계산
                    if i >= 4:
                        ma5.append(sum(prices[i-4:i+1]) / 5)
                    else:
                        ma5.append(None)
                    
                    if i >= 19:
                        ma20_arr.append(sum(prices[i-19:i+1]) / 20)
                    else:
                        ma20_arr.append(None)
                    
                    if i >= 59:
                        ma60_arr.append(sum(prices[i-59:i+1]) / 60)
                    else:
                        ma60_arr.append(None)
            except Exception as e:
                print(f"Failed to get historical data: {e}")
                # Fallback to simple data
                pass
        
        # Historical 데이터가 없으면 간단한 데이터 생성
        if not prices:
            current_price = stock_data.get('current_price', 0)
            for i in range(120):
                dates.append(f"2026-{1 + i//31:02d}-{1 + i%31:02d}")
                # 간단한 랜덤 가격 (현재가 기준)
                price_variance = (i - 60) * current_price * 0.001
                prices.append(current_price + price_variance)
                ma5.append(None if i < 4 else current_price)
                ma20_arr.append(None if i < 19 else stock_data.get('ma20', current_price))
                ma60_arr.append(None if i < 59 else stock_data.get('ma60', current_price))
        
        # 차트용 데이터 변환
        current_price = stock_data.get('current_price', 0)
        ma20 = stock_data.get('ma20', 0)
        ma60 = stock_data.get('ma60', 0)
        currency = stock_data.get('currency', 'KRW')
        
        # 간단한 기술적 지표 계산
        # RSI는 간소화 (실제로는 14일 필요)
        rsi = 55.0  # Mock
        
        # 추세 판단
        short_trend = '상승' if current_price > ma20 else '하락'
        mid_trend = '상승' if ma20 > ma60 else '하락'
        
        # MACD는 간소화
        macd = '매수' if current_price > ma20 else '중립'
        
        # 지지선/저항선
        support = stock_data.get('support_levels', [current_price * 0.95])[0]
        resistance = stock_data.get('resistance_levels', [current_price * 1.05])[0]
        
        # 매수/매도 신호
        signal = 'BUY' if short_trend == '상승' and mid_trend == '상승' else 'HOLD'
        
        return {
            "ticker": ticker,
            "name": stock_data.get('name', ticker),
            "currency": currency,
            "dates": dates,
            "prices": prices,
            "ma5": ma5,
            "ma20": ma20_arr,
            "ma60": ma60_arr,
            "indicators": {
                "current_price": current_price,
                "ma20": ma20,
                "ma60": ma60,
                "rsi": rsi,
                "macd": macd,
                "short_trend": short_trend,
                "mid_trend": mid_trend,
                "support": support,
                "resistance": resistance,
                "patterns": []
            },
            "signal": signal,
            "summary": _format_summary(stock_data.get('name', ticker), current_price, currency, short_trend, mid_trend, ma20, ma60)
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

# -----------------------
# Health Check
# -----------------------
@app.get("/health")
def health():
    agent_status = "ok" if agent_orchestrator and agent_data_provider else "unavailable"
    
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "ai_agent": agent_status
    }


# -----------------------
# Catch-all HTML Route (MUST BE LAST)
# -----------------------
@app.get("/{filename}")
def serve_html(filename: str):
    """HTML 파일 제공 (맨 마지막 라우트)"""
    if not filename.endswith(".html"):
        return JSONResponse(status_code=404, content={"error": "Not found"})
    
    filepath = os.path.join(WEB_DIR, filename)
    if not os.path.exists(filepath):
        return JSONResponse(status_code=404, content={"error": f"{filename} not found"})
    return FileResponse(filepath)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8125)
