# 실 데이터 소스 가이드

## 현재 상황
- **NH투자증권**: REST API 미제공 (DLL 방식만 지원) → 6월 이후 REST API 계획 중
- **현재 권장**: KRX Open API + Korea Data Pipeline 사용

---

## 1. 실시간 주가 데이터 (20분 지연)

### KRX Open API
- **API**: `http://data.krx.co.kr`
- **API 키**: `KRX_API_KEY` 환경변수
- **제공 데이터**:
  - 현재가 (20분 지연)
  - 시가/종가/고가/저가
  - 거래량
  - 거래대금

```python
from services.krx_stock_api import KRXStockAPI

api = KRXStockAPI()
data = api.get_current_price('005930')  # 삼성전자
print(data)
# {
#     'ticker': '005930',
#     'name': '삼성전자',
#     'price': 75000,
#     'change': 1.5,
#     'volume': 12345678
# }
```

---

## 2. 투자자별 매매동향 (수급 데이터)

### KRX 투자자별 매매동향
- **데이터**: 기관/외국인/개인 순매수
- **업데이트**: 매일 16:30 (장 마감 후)
- **지연**: 1일

```python
from services.korea_data_pipeline import KoreaDataPipeline

async def get_data():
    pipeline = KoreaDataPipeline()
    data = await pipeline.fetch_krx_supply_demand()
    return data

# {
#     '005930': {
#         'inst_net': 245000000,     # 기관 순매수 (원)
#         'foreign_net': -123000000,  # 외국인 순매수
#         'retail_net': -122000000    # 개인 순매수
#     }
# }
```

---

## 3. 공시 정보 (실적/뉴스)

### OpenDART API
- **제공**: 상장사 공시 정보
- **API 키**: `OPENDART_API_KEY`
- **데이터**: 사업보고서, 분기보고, 뉴스공시 등

---

## 4. 미국 주식 실시간 데이터

### Yahoo Finance
- **지연**: 실시간 (무료)
- **제공**: OHLCV 데이터

```python
from services.us_stock_service import USStockService

service = USStockService()
data = service.get_stock_data('AAPL')
```

---

## NH REST API 전환 로드맵

### 6월 이후 계획
1. **NH 초기 설정**
   ```python
   from services.nh_investment_api import NHInvestmentAPI
   
   api = NHInvestmentAPI(use_mock=False)
   api.get_token()
   data = api.get_current_price('005930')
   ```

2. **환경변수 수정**
   ```env
   NH_USE_MOCK=false
   ```

3. **장점**
   - 실시간 시세 (지연 없음)
   - 계좌 연동 거래 가능
   - 고급 API 기능

---

## 현재 설정

### 환경변수 상태
```env
# 모의투자 모드 (Mock)
NH_USE_MOCK=true

# KRX API (실 데이터)
KRX_API_KEY=YOUR_KEY_HERE
```

### 데이터 우선순위
1. **실시간**: KRX Open API (20분 지연)
2. **수급**: KRX 투자자별 매매동향
3. **공시**: OpenDART API
4. **뉴스**: 웹 크롤링

---

## 설정 체크리스트

- [ ] KRX_API_KEY 확인
- [ ] OPENDART_API_KEY 설정 (선택)
- [ ] MySQL/MariaDB 캐시 DB 설정 (선택)
- [ ] 프록시/방화벽 설정 확인

---

## 문제 해결

### KRX API 연결 실패
```bash
# 1. API 키 확인
echo $KRX_API_KEY

# 2. 네트워크 연결 테스트
curl http://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd

# 3. 방화벽 설정 확인
# - 아웃바운드 HTTP 80 포트 열기
# - 아웃바운드 HTTPS 443 포트 열기
```

### Rate Limiting
- KRX: 0.3초 대기 (자동)
- 동시 요청 제한 없음

---

## 참고 자료

- [KRX 데이터 포털](http://data.krx.co.kr)
- [OpenDART API](https://opendart.fss.or.kr)
- [NH투자증권 공지사항](https://securities.nhqv.com)
