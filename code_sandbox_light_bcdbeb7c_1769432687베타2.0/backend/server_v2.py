from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import os
from datetime import date, datetime

# -----------------------
# Config
# -----------------------
ACCESS_KEY = "ds-test-2026"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(BASE_DIR, "..")  # 상위 디렉토리 (index.html 위치)

app = FastAPI(title="Decision Stream | 중기 스윙 투자 시스템")

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

    client_key = req.query_params.get("key")
    if client_key != ACCESS_KEY:
        return JSONResponse(status_code=403, content={"error": "Invalid API key"})
    return await call_next(req)

# -----------------------
# Index
# -----------------------
@app.get("/")
def root():
    index_path = os.path.join(WEB_DIR, "index.html")
    if not os.path.exists(index_path):
        return JSONResponse(status_code=404, content={"error": "index.html not found"})
    return FileResponse(index_path)

# -----------------------
# Utils / Mock Data
# -----------------------
def score(s: str) -> int:
    """간단한 점수 생성 함수 (Mock용)"""
    return sum(ord(c) for c in s) % 100

SECTORS = ["방산", "헬스케어", "AI 반도체", "전력", "에너지"]

STOCKS = {
    "방산": [
        {"ticker": "LMT", "name": "Lockheed Martin", "price": 445.50},
        {"ticker": "012450", "name": "한화에어로스페이스", "price": 185000},
        {"ticker": "079550", "name": "LIG넥스원", "price": 544000}
    ],
    "헬스케어": [
        {"ticker": "JNJ", "name": "Johnson & Johnson", "price": 158.25},
        {"ticker": "207940", "name": "삼성바이오로직스", "price": 850000},
        {"ticker": "068270", "name": "셀트리온", "price": 175000}
    ],
    "AI 반도체": [
        {"ticker": "005930", "name": "삼성전자", "price": 75000},
        {"ticker": "NVDA", "name": "NVIDIA", "price": 875.00}
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
# Health Check
# -----------------------
@app.get("/health")
def health():
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8125)
