"""
HTS CSV 변환 도구 - 키움증권/미래에셋 일봉 데이터
"""
import pandas as pd
import glob
import os
from pathlib import Path

# 경로 설정
SCRIPT_DIR = Path(__file__).parent
HTS_DIR = SCRIPT_DIR / ".." / "screener" / "data" / "hts_raw" / "prices"
OUT_FILE = SCRIPT_DIR / ".." / "screener" / "data" / "raw" / "prices_daily.csv"

# HTS 컬럼명 → 표준 컬럼명 매핑
COLUMN_MAP = {
    # 날짜
    "일자": "date",
    "날짜": "date",
    # 종목
    "종목코드": "ticker",
    "단축코드": "ticker",
    # 가격
    "시가": "open",
    "고가": "high",
    "저가": "low",
    "종가": "close",
    # 거래
    "거래량": "volume",
}


def normalize_ticker(x):
    """종목코드 6자리로 정규화"""
    return str(x).zfill(6)


def convert():
    """HTS CSV → 표준 포맷 변환"""
    files = glob.glob(str(HTS_DIR / "*.csv"))
    
    if not files:
        print("⚠️  HTS 가격 CSV 파일이 없습니다.")
        print(f"   파일 위치: {HTS_DIR}")
        return
    
    dfs = []
    for f in files:
        print(f"📄 처리중: {os.path.basename(f)}")
        try:
            df = pd.read_csv(f, encoding="cp949")
            
            # 필요한 컬럼만 선택
            available_cols = [c for c in COLUMN_MAP.keys() if c in df.columns]
            if not available_cols:
                print(f"   ⚠️ 매핑 가능한 컬럼이 없습니다: {list(df.columns)}")
                continue
            
            df = df[available_cols].rename(columns=COLUMN_MAP)
            df["ticker"] = df["ticker"].apply(normalize_ticker)
            df["date"] = pd.to_datetime(df["date"])
            dfs.append(df)
            
        except Exception as e:
            print(f"   ❌ 오류: {e}")
            continue
    
    if not dfs:
        print("❌ 변환 가능한 데이터가 없습니다.")
        return
    
    # 통합 및 중복 제거
    out = (
        pd.concat(dfs, ignore_index=True)
        .sort_values(["ticker", "date"])
        .drop_duplicates(["ticker", "date"], keep="last")
    )
    
    # 저장
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_FILE, index=False, encoding="utf-8-sig")
    
    print(f"\n✅ 변환 완료!")
    print(f"   출력: {OUT_FILE}")
    print(f"   행 수: {len(out):,}")
    print(f"   종목 수: {out['ticker'].nunique()}")
    print(f"   기간: {out['date'].min()} ~ {out['date'].max()}")


if __name__ == "__main__":
    convert()
