# Stock Radar Spark - 스케일링 분석

## 📊 현재 구조 용량 분석

### 1. **데이터베이스 (SQLite)**
```
✅ 장점:
- 설치 불필요, 파일 기반
- 소규모 앱에 충분
- 비용 0원

⚠️ 병목 지점:
- 동시 쓰기 작업 제한 (Lock 발생)
- SQLite는 1개의 쓰기 연결만 허용
- 동시성 낮음 (concurrent users ↓)
```

**SQLite 용량:**
- **가능한 동시 사용자**: 5-10명
- **활성 사용자 (월간)**: 50명
- **DB 크기**: 32MB (사용자 1000명, 분석 이력 100만 건)

---

### 2. **FastAPI 서버**

**하드웨어 기준** (단일 Linux/Windows 머신):
- CPU: 4-core
- Memory: 8GB
- 디스크: 50GB

**FastAPI + Uvicorn 성능:**
```
워커 설정: 4개 (4-core CPU 기준)
uvicorn main:app --workers 4 --host 0.0.0.0 --port 8000

동시 요청: ~100-200 req/sec
```

**각 요청 처리 시간:**
| 작업 | 시간 | 리소스 |
|---|---|---|
| 로그인/회원가입 | 50ms | 낮음 |
| 시장 분석 (Market Regime) | 200ms | 중간 |
| 종목 스크리너 (5 Agent) | 2-3초 | 높음 ⚠️ |
| 차트 데이터 | 300ms | 중간 |

---

### 3. **외부 API 제약**

#### **Yahoo Finance**
```
제한: Rate Limit 없음 (yfinance 라이브러리 사용)
동시 요청: 10-20개 안전
비용: 무료
```

#### **OpenDART API**
```
제한: 1초당 10회 요청 (Rate Limit)
일 한도: 10,000건
비용: 무료
```

---

### 4. **메모리 사용량**

**프로세스당 (Uvicorn Worker)**
```
기본: ~100MB
Agent 실행 중: +200MB
DataFrame 캐싱: +50MB

총 메모리 (4 workers): 
  = (100 + 200 + 50) MB × 4 = 1.4GB
```

---

## 🎯 **현재 시스템 수용 능력**

### **시나리오 1: API Key 보호 사용 (현재)**
```
ACCESS_KEY = "ds-test-2026" 으로 보호된 상태
- 신뢰할 수 있는 사용자만 접근
- 동시 활성 사용자: 10-20명
- 월간 활성 사용자: 100-200명
```

### **시나리오 2: 인증 시스템 추가 (방금 구현)**
```
회원가입/로그인 추가됨
- 동시 활성 사용자: 5-10명
- 월간 활성 사용자: 50-100명
- 병목: SQLite 쓰기 Lock (로그인, 분석 저장)
```

### **시나리오 3: 캐싱 최적화 (권장)**
```
Redis 추가 시:
- 동시 활성 사용자: 20-50명
- 월간 활성 사용자: 500-1000명
- API 호출 감소: 60-70%
```

---

## ⚠️ **병목 지점**

### **1. SQLite 동시성** (가장 큰 문제)
```python
# 문제: 동시 2개 이상의 쓰기 요청 시 Lock 발생
User.query.add(new_user)  # Lock 획득
db.commit()               # Lock 해제

# 해결: PostgreSQL 또는 MySQL로 마이그레이션
```

**현재 Lock 위험 시나리오:**
- 2명 이상이 동시에 로그인 → 1명 Timeout
- 분석 결과 동시 저장 → 일부 실패

### **2. Agent 계산 성능**
```
5개 Agent 실행 시간: 2-3초
동시 3개 요청 시: 총 6-9초 대기
```

**해결:**
- 백그라운드 작업: Celery/RQ
- 캐싱: 동일 종목은 10분 캐시
- 비동기: async/await 최적화

### **3. API Rate Limit**
```
OpenDART: 1초당 10회
- 사용자 10명이 동시 조회 → 대기열 필요
- 해결: Redis Queue, 1초 단위 배치 처리
```

---

## 📈 **확장 로드맵**

### **Phase 1: 현재 (SQLite)** ✅
```
- 동시 사용자: 5-10명
- 월간 사용자: 50-100명
- 비용: $0/월
- 구성: FastAPI + SQLite + yfinance

권장 용도:
  ✅ 팀 내부용 (10명 이하)
  ✅ MVP/데모
  ✅ 개인 투자 도구
```

### **Phase 2: 권장 (PostgreSQL + Redis)** ⭐
```
비용: $20-50/월 (클라우드 DB)
확장성:
  - 동시 사용자: 50-100명
  - 월간 사용자: 5,000명+

구성:
  - DB: PostgreSQL (RDS)
  - 캐시: Redis (ElastiCache)
  - Worker: Celery + RabbitMQ
  - 서버: EC2 t3.medium (2-4 cores)

성능:
  - API 응답: 100-500ms
  - 동시 요청: 1000+ req/min
```

### **Phase 3: 상용 수준 (마이크로서비스)**
```
비용: $200-500/월
확장성:
  - 동시 사용자: 1000+명
  - 월간 사용자: 100,000+명

구성:
  - 로드 밸런서: ALB
  - 앱 서버: 3-5개 EC2 인스턴스
  - DB: RDS Aurora (자동 스케일)
  - 캐시: ElastiCache Cluster
  - 메시지Q: SQS/RabbitMQ
  - CDN: CloudFront
  - 모니터링: CloudWatch + Datadog
```

---

## 🔧 **Phase 2로 업그레이드 하려면**

### **필요한 변경:**
```
1. DB 마이그레이션 (SQLite → PostgreSQL)
   - models/user.py: 변경 없음 (SQLAlchemy ORM)
   - .env: DATABASE_URL 변경
   - 시간: 1-2시간

2. 캐싱 추가
   - requirements.txt: redis 이미 있음
   - services/cache_service.py: 신규 작성
   - 주요 캐시 대상:
     * 시장 지표 (5분 단위)
     * 종목 분석 (10분 단위)
     * OpenDART 재무 (1일 단위)

3. 백그라운드 작업 (선택)
   - Celery + RabbitMQ
   - 장시간 Agent 분석 비동기화
   - 시간: 4-6시간

4. 성능 최적화
   - API 연결 풀링
   - DB 인덱싱
   - Agent 병렬 실행
```

---

## 💰 **비용 비교**

| 항목 | 현재 (SQLite) | Phase 2 (PostgreSQL) | Phase 3 (클라우드) |
|---|---|---|---|
| **서버** | 0 (로컬) | $10 (EC2) | $50 (3x EC2) |
| **DB** | 0 | $20 (RDS) | $100 (Aurora) |
| **캐시** | 0 | $5 (ElastiCache) | $30 |
| **기타** | 0 | $10 | $50 |
| **합계/월** | **$0** | **$45** | **$230** |
| **사용자** | 50-100 | 5,000 | 100,000 |
| **비용/사용자** | - | $0.009 | $0.0023 |

---

## ✅ **권장 사항**

### **개발 단계에서 (현재)**
```
현재 SQLite 구조 계속 사용
- 단일 서버에서 테스트 진행
- 유저 5-10명까지 safe
```

### **베타 출시 준비 (2주 후)**
```
PostgreSQL + Redis로 마이그레이션
- 월간 사용자 50-100명 예상
```

### **상용 출시 (1-2개월 후)**
```
AWS 또는 GCP로 전환
- 동시 사용자 증가 대비
- 가용성 99% 이상 필요
```

---

## 🚀 **지금 할 수 있는 최적화**

**즉시 적용 (5분):**
```python
# 1. SQLite 동시성 개선
DATABASE_URL = "sqlite:///./stock_radar.db?timeout=30&check_same_thread=False"

# 2. Connection Pool (PostgreSQL 마이그레이션 시)
pool_size = 10
max_overflow = 20
```

**본주일 안에 (2-3시간):**
```python
# 1. API 응답 캐싱
@cached(ttl=300)  # 5분 캐시
def get_market_regime():
    ...

# 2. DB 쿼리 최적화
- User 조회: username 인덱스 ✅ (이미 있음)
- 분석 이력: user_id + created_at 복합 인덱스
```

**이번 주 (4-6시간):**
```python
# 1. Agent 병렬 실행
async def run_agents_parallel():
    # 기존: 순차 실행 (2-3초)
    # 변경: 병렬 실행 (1-1.5초)
    tasks = [
        asyncio.create_task(market_regime()),
        asyncio.create_task(sector_scout()),
        ...
    ]
    return await asyncio.gather(*tasks)
```

---

## 📝 **체크리스트**

**Phase 1 (현재):**
- [x] SQLite DB
- [x] FastAPI + Uvicorn
- [x] 사용자 인증
- [x] 5 AI Agent
- [ ] 캐싱
- [ ] 백그라운드 작업
- [ ] 성능 모니터링

**Phase 2 (추천):**
- [ ] PostgreSQL 마이그레이션
- [ ] Redis 캐싱
- [ ] Celery 백그라운드 작업
- [ ] 로드 밸런싱
- [ ] 헬스 체크 엔드포인트

**Phase 3:**
- [ ] AWS/GCP 인프라
- [ ] 오토스케일링
- [ ] 마이크로서비스
- [ ] 모니터링/알림

---

## 결론

**현재 시스템:**
- ✅ **최대 5-10명 동시 사용자**
- ✅ **월간 50-100명 사용 가능**
- ❌ **SQLite가 주 병목**
- ⭐ **Phase 2 (PostgreSQL)로 업그레이드 강력 권장**
