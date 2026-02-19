# AI Agent 시스템 시작 가이드

## 🚀 빠른 시작

### 1. 서버 시작
```bash
cd backend
python server_v2.py
```

또는 자동 재시작 모드:
```bash
uvicorn server_v2:app --host 0.0.0.0 --port 8125 --reload
```

### 2. 웹 브라우저에서 테스트
```
http://localhost:8125/agent_test.html
```

## 📋 테스트 시나리오

### A. 전체 파이프라인 (Full Analysis)
모든 종목을 분석하고 상위 3개 추천

**테스트 방법:**
1. "Full Analysis 실행" 버튼 클릭
2. RISK_ON/RISK_OFF 상태 확인
3. 섹터 순위 확인
4. 추천 종목 3개 확인 (LEADER/FOLLOWER)
5. 매매 계획 (진입가, 손절가, 목표가) 확인
6. 반론 사항 검토

### B. 단일 종목 분석 (Quick Analysis)
특정 종목만 빠르게 분석

**테스트 방법:**
1. 종목 코드 입력 (예: 005930, NVDA)
2. "Quick Analysis 실행" 버튼 클릭
3. 종목 분류 확인 (LEADER/FOLLOWER/NO_GO)
4. 신뢰도 및 액션 확인

### C. 시장 상태만 확인 (Market Regime)
현재 시장이 RISK_ON인지 RISK_OFF인지만 확인

**테스트 방법:**
1. "Market Regime 조회" 버튼 클릭
2. 시장 점수와 Playbook 확인

## 🧪 CLI 테스트 (터미널)
```bash
cd backend
python test_agents.py
```

## 📊 현재 데이터

### 한국 주식 (KRW)
- 삼성전자 (005930): 75,000원
- SK하이닉스 (000660): 135,000원
- 한화에어로스페이스 (012450): 225,000원

### 미국 주식 (USD)
- NVDA (엔비디아): $875.00
- LMT (록히드마틴): $445.50
- AAPL (애플): $185.25

## 🔧 API 엔드포인트

### 1. 전체 분석
```bash
POST http://localhost:8125/api/agent/analyze
Content-Type: application/json

{
  "period": "단기",
  "risk_profile": "중립"
}
```

### 2. 단일 종목 분석
```bash
POST http://localhost:8125/api/agent/quick-analyze
Content-Type: application/json

{
  "ticker": "NVDA"
}
```

### 3. 시장 상태
```bash
GET http://localhost:8125/api/agent/market-regime
```

## 📁 출력 파일 위치
```
backend/output/agent_results/agent_analysis_YYYYMMDD_HHMMSS.json
```

## ✅ 체크리스트

- [ ] 서버 실행 확인 (http://localhost:8125)
- [ ] 전체 파이프라인 테스트
- [ ] 한국 주식 Quick Analysis (005930)
- [ ] 미국 주식 Quick Analysis (NVDA)
- [ ] 통화 표시 확인 (원 vs $)
- [ ] 매매 계획 생성 확인
- [ ] 반론 사항 확인
- [ ] JSON 출력 파일 확인

## 🐛 문제 해결

### 서버가 안 켜지는 경우
```bash
# 포트 충돌 확인
netstat -ano | findstr :8125

# 해당 프로세스 종료
taskkill /PID <프로세스ID> /F

# 서버 재시작
python server_v2.py
```

### 모듈 없음 오류
```bash
pip install -r requirements.txt
```

## 🎯 다음 단계

1. **실제 데이터 연결**
   - KRX API (한국 주식)
   - Yahoo Finance API (미국 주식)
   - OpenDART API (재무제표)

2. **스케줄러 설정**
   - 장 마감 후 자동 분석
   - 아침 9시 리포트 생성

3. **알림 추가**
   - LEADER 등장 시 알림
   - RISK_OFF 전환 시 경고
