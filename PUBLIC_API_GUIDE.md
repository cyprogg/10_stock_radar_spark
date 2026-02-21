# Stock Radar Spark - Public API Guide

**버전**: 1.0.0-beta  
**기준일**: 2026년 2월 21일

---

## 📡 API 개요

Stock Radar Spark는 AI 기반 주식 분석 플랫폼입니다. 

**핵심 기능:**
- 시장 상태 분석 (Risk-On/Risk-Off)
- 섹터별 강도 분석
- 종목 분류 (Leader/Follower/NoGo)
- 매매 계획 수립
- 투자 위험 평가

---

## 🔐 인증

### 회원가입
```http
POST /api/auth/signup
Content-Type: application/json

{
  "username": "user123",
  "email": "user@example.com",
  "password": "SecurePass123!",
  "password_confirm": "SecurePass123!",
  "full_name": "홍길동"
}
```

**응답:**
```json
{
  "success": true,
  "message": "회원가입 성공",
  "data": {
    "user_id": 1,
    "username": "user123"
  }
}
```

### 로그인
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "user123",
  "password": "SecurePass123!"
}
```

**응답:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "id": 1,
    "username": "user123",
    "email": "user@example.com"
  }
}
```

---

## 📊 분석 API

### 시장 상태 분석
```http
GET /api/analysis/market-regime
Authorization: Bearer {토큰}
```

**응답:**
```json
{
  "state": "RISK_ON",
  "confidence": 0.85,
  "recommendation": "공격적 매수",
  "timestamp": "2026-02-21T10:30:00"
}
```

**상태 값:**
- `RISK_ON`: 공격적 매수 가능 (시장이 건강한 상태)
- `RISK_OFF`: 방어 모드 (리스크 관리 필수)

---

### 섹터 분석
```http
GET /api/analysis/sectors
Authorization: Bearer {토큰}
```

**응답:**
```json
{
  "sectors": [
    {
      "name": "반도체",
      "strength": 95,
      "trend": "상승 중",
      "duration": "2주"
    },
    {
      "name": "방위산업",
      "strength": 88,
      "trend": "상승",
      "duration": "1주"
    }
  ]
}
```

**strength 의미:**
- 90-100: 강한 상승
- 70-89: 중등도 상승
- 50-69: 중립
- 30-49: 약한 하락
- 0-29: 강한 하락

---

### 종목 분류
```http
POST /api/analysis/classify
Authorization: Bearer {토큰}
Content-Type: application/json

{
  "ticker": "005930",  // 삼성전자
  "sector": "반도체"
}
```

**응답:**
```json
{
  "ticker": "005930",
  "name": "삼성전자",
  "classification": "LEADER",
  "confidence": 0.92,
  "recommendation": "매수",
  "priority": "high",
  "analysis_date": "2026-02-21"
}
```

**분류 의미:**
- `LEADER`: 강하게 추천 (매우 높은 확률)
- `FOLLOWER`: 조건부 추천 (중간 확률)
- `NO_GO`: 비추천 (위험도 높음)

---

### 매매 계획
```http
POST /api/analysis/trade-plan
Authorization: Bearer {토큰}
Content-Type: application/json

{
  "ticker": "005930",
  "sector": "반도체",
  "classification": "LEADER"
}
```

**응답:**
```json
{
  "ticker": "005930",
  "entry_price": 71400,
  "entry_type": "market",
  "stop_loss": 67000,
  "target_price": 75000,
  "position_size": 100,
  "risk_reward_ratio": 2.0,
  "validity": "2주"
}
```

**필드 의미:**
- `entry_price`: 추천 진입가
- `stop_loss`: 손절가 (이 아래로 떨어지면 매도)
- `target_price`: 목표가
- `risk_reward_ratio`: 위험/수익 비율 (클수록 good)

---

### 투자 위험 평가
```http
POST /api/analysis/risk-assessment
Authorization: Bearer {토큰}
Content-Type: application/json

{
  "ticker": "005930",
  "classification": "LEADER"
}
```

**응답:**
```json
{
  "ticker": "005930",
  "risk_level": "MEDIUM",
  "concerns": [
    "대형 기관 물량 증가",
    "기술적 저항선 근처"
  ],
  "mitigation": [
    "분할 진입 권장",
    "ATR 기반 손절선 엄격히 준수"
  ],
  "overall_confidence": 0.82
}
```

**위험도:**
- `LOW`: 진입 가능
- `MEDIUM`: 주의 필요
- `HIGH`: 비추천

---

## 👤 사용자 관리

### 프로필 조회
```http
GET /api/auth/me
Authorization: Bearer {토큰}
```

### 프로필 업데이트
```http
PUT /api/auth/profile
Authorization: Bearer {토큰}
Content-Type: application/json

{
  "risk_profile": "중립",
  "account_size": 10000000,
  "investment_period": "중기"
}
```

### 비밀번호 변경
```http
POST /api/auth/change-password
Authorization: Bearer {토큰}
Content-Type: application/json

{
  "old_password": "OldPass123!",
  "new_password": "NewPass456!",
  "new_password_confirm": "NewPass456!"
}
```

---

## 🔍 시스템 상태

### 헬스 체크
```http
GET /api/health
```

**응답:**
```json
{
  "status": "healthy",
  "timestamp": "2026-02-21T10:30:00",
  "services": {
    "database": "ok",
    "ai_agents": "ok",
    "api_server": "ok"
  }
}
```

### 상태 상세
```http
GET /api/status
```

---

## ⚙️ 환경설정

### 투자 성향 설정
```json
{
  "risk_profile": "보수" | "중립" | "공격",
  "account_size": 1000000,
  "investment_period": "단기" | "중기" | "장기"
}
```

### 필터링 옵션 (향후 추가)
```json
{
  "min_price": 5000,
  "max_price": 100000,
  "exclude_sectors": ["에너지"],
  "min_confidence": 0.8
}
```

---

## 📋 응답 코드

| 코드 | 의미 |
|---|---|
| 200 | 성공 |
| 400 | 잘못된 요청 |
| 401 | 인증 실패 |
| 403 | 권한 없음 |
| 500 | 서버 오류 |

---

## 💡 사용 팁

### 1. API 접근 순서
```
1. /api/auth/login (토큰 획득)
2. /api/analysis/market-regime (전체 시장 상태 파악)
3. /api/analysis/sectors (주력 섹터 파악)
4. /api/analysis/classify (종목별 분류)
5. /api/analysis/trade-plan (구체적 매매 계획)
6. /api/analysis/risk-assessment (리스크 확인)
```

### 2. 재액세스 방지
```
- 시장 지표는 5분마다 갱신
- 종목 분석은 10분마다 갱신
- 동일 종목 재조회 시 캐시된 데이터 반환
```

### 3. 에러 처리
```json
{
  "detail": "입력하신 데이터가 유효하지 않습니다",
  "code": "INVALID_INPUT"
}
```

---

## 🔒 보안 주의사항

1. **토큰 관리**
   - 토큰은 24시간 유효
   - 로그아웃 후 새 토큰 발급 필수
   - 토큰 공유 금지

2. **API 키**
   - 환경에 따라 제한됨
   - 만료되면 새 키 발급 필요

3. **로그**
   - 모든 요청 기록됨
   - 비정상 패턴 자동 감지

---

## 📞 지원

- **API 문서**: http://localhost:8000/docs
- **문제 해결**: BETA_TESTER_GUIDE.md 참조
- **피드백**: support@stockradar.ai

---

**Version**: 1.0.0-beta  
**Last Updated**: 2026-02-21
