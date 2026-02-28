import yfinance as yf

stock = yf.Ticker('012450.KS')
hist = stock.history(start='2026-02-01', end='2026-02-21')

print('=== 012450 한화에어로스페이스 (2/1~2/20) Yahoo Finance ===')
if not hist.empty:
    print(hist[['Close']])
    print(f'\n범위: {hist.index[0].date()} ~ {hist.index[-1].date()}')
    print(f'포인트: {len(hist)}개')
    print('\n✅ Yahoo에 실제 데이터 있음')
else:
    print('⚠️ Yahoo 데이터 없음 - 캐시되지 않은 데이터로 복구 불가')
