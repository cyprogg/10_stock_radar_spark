"""
Decision Stream - 중기 스윙 투자 스크리너
월 1회 실행 기준 MVP 버전
"""
from __future__ import annotations
import os
import pandas as pd
import numpy as np
from datetime import date
from pathlib import Path

# 데이터 디렉토리
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)
(DATA_DIR / "raw").mkdir(exist_ok=True)
(DATA_DIR / "hts_raw" / "prices").mkdir(parents=True, exist_ok=True)
(DATA_DIR / "hts_raw" / "flows").mkdir(parents=True, exist_ok=True)
(DATA_DIR / "output").mkdir(exist_ok=True)


# ========== Helpers ==========
def _to_dt(x) -> pd.Timestamp:
    return pd.to_datetime(x).tz_localize(None)


def ma(series: pd.Series, n: int) -> pd.Series:
    """이동평균"""
    return series.rolling(n, min_periods=n).mean()


def pct_change(series: pd.Series, n: int) -> pd.Series:
    """n일 수익률"""
    return series.pct_change(n)


def realized_vol(series: pd.Series, n: int) -> pd.Series:
    """실현 변동성 (rolling std)"""
    r = series.pct_change()
    return r.rolling(n, min_periods=n).std()


def slope(series: pd.Series, n: int) -> float:
    """선형 기울기"""
    y = series.dropna().tail(n).values
    if len(y) < n:
        return np.nan
    x = np.arange(n)
    coef = np.polyfit(x, y, 1)[0]
    return float(coef)


# ========== Loaders ==========
def load_universe(path: str) -> pd.DataFrame:
    """종목 유니버스 로드"""
    if not os.path.exists(path):
        # 샘플 데이터 생성
        sample = pd.DataFrame({
            'ticker': ['012450', '079550', '010120'],
            'name': ['한화에어로스페이스', 'LIG넥스원', 'LS전선'],
            'theme': ['defense', 'defense', 'energy'],
            'chain': ['prime', 'midstream', 'midstream']
        })
        sample.to_csv(path, index=False, encoding='utf-8-sig')
    
    u = pd.read_csv(path, dtype={"ticker": str})
    required = {"ticker", "name", "theme", "chain"}
    missing = required - set(u.columns)
    if missing:
        raise ValueError(f"universe.csv missing columns: {missing}")
    return u


def load_news(path: str) -> pd.DataFrame:
    """뉴스 이벤트 로드"""
    if not os.path.exists(path):
        # 샘플 데이터 생성
        sample = pd.DataFrame({
            'date': ['2026-01-15', '2026-01-18'],
            'theme': ['defense', 'energy'],
            'confirmed': [1, 1],
            'duration_months': [3, 6],
            'affects_earnings': [1, 1],
            'industry_wide': [1, 1],
            'rumor': [0, 0],
            'one_off': [0, 0],
            'notes': ['수출 계약 확정', '전력망 투자 확정']
        })
        sample.to_csv(path, index=False, encoding='utf-8-sig')
    
    n = pd.read_csv(path)
    n["date"] = _to_dt(n["date"])
    for c in ["confirmed", "affects_earnings", "industry_wide", "rumor", "one_off"]:
        n[c] = n[c].astype(int)
    n["duration_months"] = n["duration_months"].astype(int)
    return n


def load_prices_csv(path: str) -> pd.DataFrame:
    """일봉 가격 데이터 로드"""
    if not os.path.exists(path):
        return pd.DataFrame(columns=['date', 'ticker', 'open', 'high', 'low', 'close', 'volume'])
    
    df = pd.read_csv(path, dtype={"ticker": str})
    df["date"] = _to_dt(df["date"])
    return df


def load_index_csv(path: str) -> pd.DataFrame:
    """지수 데이터 로드"""
    if not os.path.exists(path):
        # 샘플 지수 데이터 생성
        dates = pd.date_range(end=date.today(), periods=200)
        sample = pd.DataFrame({
            'date': dates,
            'close': 2500 + np.cumsum(np.random.randn(200) * 10)
        })
        sample.to_csv(path, index=False, encoding='utf-8-sig')
    
    idx = pd.read_csv(path)
    idx["date"] = _to_dt(idx["date"])
    return idx.sort_values("date")


def load_flows_csv(path: str) -> pd.DataFrame | None:
    """수급 데이터 로드"""
    if not os.path.exists(path):
        return None
    
    f = pd.read_csv(path, dtype={"ticker": str})
    f["date"] = _to_dt(f["date"])
    return f


# ========== Gates & Scores ==========
def market_gate(index_df: pd.DataFrame) -> tuple[bool, dict]:
    """시장 레짐 필터 (RISK_ON/OFF)"""
    idx = index_df.sort_values("date").copy()
    idx["ma20"] = ma(idx["close"], 20)
    idx["vol10"] = realized_vol(idx["close"], 10)
    idx["vol20"] = realized_vol(idx["close"], 20)
    
    last = idx.dropna().tail(1)
    if last.empty:
        return False, {"reason": "index insufficient data"}
    
    close = float(last["close"].iloc[0])
    ma20v = float(last["ma20"].iloc[0])
    ma20_s = slope(idx["ma20"], 10)
    vol10 = float(last["vol10"].iloc[0])
    vol20 = float(last["vol20"].iloc[0])
    
    # Gate logic
    if close < ma20v and ma20_s < 0:
        return False, {"reason": "risk_off_ma20_down"}
    if vol20 > 0 and vol10 > vol20 * 1.5:
        return False, {"reason": "risk_off_vol_spike"}
    
    return True, {"reason": "risk_on"}


def score_news(news_df: pd.DataFrame, theme: str, asof: pd.Timestamp) -> int:
    """뉴스 점수 (0~30)"""
    recent = news_df[(news_df["theme"] == theme) & (news_df["date"] <= asof)].tail(20)
    score = 0
    
    for _, n in recent.iterrows():
        if n["confirmed"] == 1:
            score += 2
        if int(n["duration_months"]) >= 1:
            score += 1
        if n["affects_earnings"] == 1:
            score += 1
        if n["industry_wide"] == 1:
            score += 1
        if n["rumor"] == 1:
            score -= 2
        if n["one_off"] == 1:
            score -= 1
    
    return int(min(max(score, 0), 30))


def heat_gate(price_df: pd.DataFrame) -> bool:
    """과열 회피 필터"""
    d = price_df.sort_values("date").copy()
    if len(d) < 30:
        return False
    
    d["gain10"] = pct_change(d["close"], 10)
    last = d.tail(1)
    gain10 = float(last["gain10"].iloc[0]) if not np.isnan(last["gain10"].iloc[0]) else 0.0
    
    if gain10 > 0.25:  # 10일간 25% 이상 급등
        return False
    
    vol_avg = float(d["volume"].tail(20).mean())
    vol_last = float(last["volume"].iloc[0])
    bearish = float(last["close"].iloc[0]) < float(last["open"].iloc[0])
    
    if vol_avg > 0 and vol_last > vol_avg * 3.0 and bearish:
        return False
    
    return True


def score_flow(flow_df: pd.DataFrame | None, ticker: str, asof: pd.Timestamp) -> int:
    """수급 점수 (0~25)"""
    if flow_df is None:
        return 0
    
    f = flow_df[(flow_df["ticker"] == ticker) & (flow_df["date"] <= asof)].sort_values("date").tail(10)
    if f.empty:
        return 0
    
    foreign_days = int((f["foreign_net"] > 0).sum())
    inst_days = int((f["institution_net"] > 0).sum())
    
    score = 0
    if foreign_days >= 5:
        score += 10
    if inst_days >= 5:
        score += 10
    
    # Net ratio 계산
    net_abs = float((f["foreign_net"].abs() + f["institution_net"].abs()).mean())
    if net_abs > 0:
        net_ratio = float((f["foreign_net"] + f["institution_net"]).sum() / (net_abs * len(f)))
        if net_ratio > 0.02:
            score += 5
    
    return int(min(score, 25))


def score_price(price_df: pd.DataFrame) -> int:
    """가격 구조 점수 (0~25)"""
    d = price_df.sort_values("date").copy()
    if len(d) < 80:
        return 0
    
    d["ma20"] = ma(d["close"], 20)
    last = d.dropna().tail(1)
    if last.empty:
        return 0
    
    close = float(last["close"].iloc[0])
    ma20v = float(last["ma20"].iloc[0])
    
    score = 0
    if close > ma20v:
        score += 10
    
    # Higher highs & higher lows
    recent = d.tail(40)
    hh = recent["high"].rolling(5).max()
    ll = recent["low"].rolling(5).min()
    
    higher_highs = hh.dropna().iloc[-1] > hh.dropna().iloc[-6] if len(hh.dropna()) >= 6 else False
    higher_lows = ll.dropna().iloc[-1] > ll.dropna().iloc[-6] if len(ll.dropna()) >= 6 else False
    
    if higher_highs and higher_lows:
        score += 10
    
    # Pullback volume < rally volume
    v_pull = float(d["volume"].tail(10).mean())
    v_rally = float(d["volume"].tail(20).head(10).mean())
    
    if v_rally > 0 and v_pull < v_rally:
        score += 5
    
    return int(min(score, 25))


def score_risk(price_df: pd.DataFrame) -> int:
    """리스크 점수 (0~20)"""
    d = price_df.sort_values("date").copy()
    if len(d) < 40:
        return 0
    
    vol = float(realized_vol(d["close"], 20).dropna().iloc[-1])
    score = 20
    
    if vol > 0.08:  # 일간 변동성 8% 초과
        score -= 5
    if vol > 0.10:
        score -= 5
    
    return int(max(score, 0))


def entry_signal(price_df: pd.DataFrame) -> bool:
    """진입 신호 (조정 후 진입)"""
    d = price_df.sort_values("date").copy()
    if len(d) < 80:
        return False
    
    d["ma20"] = ma(d["close"], 20)
    d = d.dropna()
    if len(d) < 30:
        return False
    
    close = float(d["close"].iloc[-1])
    ma20v = float(d["ma20"].iloc[-1])
    
    if close < ma20v:
        return False
    
    # Pullback from 20-day high
    high20 = float(d["high"].tail(20).max())
    if high20 <= 0:
        return False
    
    drawdown = (close / high20) - 1.0
    if not (-0.08 <= drawdown <= -0.03):
        return False
    
    # Support confirmed
    support = float(d["low"].tail(10).min())
    last2 = d.tail(2)
    
    if (last2["close"] >= support).all() and (last2["close"] >= last2["ma20"]).all():
        return True
    
    return False


def risk_plan(entry_price: float, stop_pct: float = 0.08) -> dict:
    """손절/목표가 계산"""
    stop = entry_price * (1 - stop_pct)
    t1 = entry_price * 1.15
    t2 = entry_price * 1.25
    return {"stop": stop, "t1": t1, "t2": t2}


# ========== Main ==========
def run_monthly(asof: str | None = None):
    """월 1회 스크리너 실행"""
    asof_dt = _to_dt(asof) if asof else pd.Timestamp(date.today())
    out_dir = DATA_DIR / "output"
    out_dir.mkdir(exist_ok=True)
    
    # Load data
    uni = load_universe(str(DATA_DIR / "raw" / "universe.csv"))
    news = load_news(str(DATA_DIR / "raw" / "news_events.csv"))
    prices = load_prices_csv(str(DATA_DIR / "raw" / "prices_daily.csv"))
    index_df = load_index_csv(str(DATA_DIR / "raw" / "index_kospi.csv"))
    flows = load_flows_csv(str(DATA_DIR / "raw" / "flows_daily.csv"))
    
    # Market gate
    ok, gate_info = market_gate(index_df[index_df["date"] <= asof_dt])
    if not ok:
        out_path = out_dir / f"candidates_{asof_dt:%Y%m}.csv"
        pd.DataFrame([{"status": "NO_TRADE", **gate_info}]).to_csv(
            out_path, index=False, encoding="utf-8-sig"
        )
        print(f"[MarketGate OFF] wrote {out_path} reason={gate_info}")
        return
    
    # Score all candidates
    rows = []
    for _, r in uni.iterrows():
        ticker = r["ticker"]
        theme = r["theme"]
        
        p = prices[(prices["ticker"] == ticker) & (prices["date"] <= asof_dt)].sort_values("date").tail(200)
        if len(p) < 80:
            continue
        
        # Heat gate
        if not heat_gate(p):
            continue
        
        # Scores
        s_news = score_news(news, theme, asof_dt)
        if s_news < 15:
            continue
        
        s_flow = score_flow(flows, ticker, asof_dt)
        s_price = score_price(p)
        s_risk = score_risk(p)
        total = s_news + s_flow + s_price + s_risk
        
        # Entry signal
        entry_ok = entry_signal(p)
        if total >= 70 and entry_ok:
            entry_price = float(p["close"].iloc[-1])
            plan = risk_plan(entry_price, 0.08)
            
            rows.append({
                "ticker": ticker,
                "name": r["name"],
                "theme": theme,
                "chain": r["chain"],
                "score_total": total,
                "score_news": s_news,
                "score_flow": s_flow,
                "score_price": s_price,
                "score_risk": s_risk,
                "entry_price": entry_price,
                "stop": plan["stop"],
                "t1": plan["t1"],
                "t2": plan["t2"],
            })
    
    # Write output
    out_path = out_dir / f"candidates_{asof_dt:%Y%m}.csv"
    out = pd.DataFrame(rows).sort_values(
        ["score_total", "score_news", "score_flow"], ascending=False
    )
    out.to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"✅ Wrote candidates: {out_path} (n={len(out)})")
    
    return out


if __name__ == "__main__":
    result = run_monthly()
    if result is not None:
        print("\n=== Top Candidates ===")
        print(result[['ticker', 'name', 'score_total', 'entry_price']].head())
