# Stock Radar Spark - 베타 배포 체크리스트

**배포 날짜**: 2026년 2월 21일  
**대상**: 베타테스터 5명  
**제한 사항**: 동시 접속 10명 (안정성 우선)

---

## ✅ 배포 전 확인 사항

### 시스템 설정
- [x] Python 3.10+ 설치 확인
- [x] 필수 패키지 requirements.txt 작성
- [x] 환경변수 .env 파일 생성
- [x] SQLite 데이터베이스 초기화

### 인증 시스템
- [x] 사용자 모델 (User, UserSession)
- [x] 회원가입 엔드포인트 (/api/auth/signup)
- [x] 로그인 엔드포인트 (/api/auth/login)
- [x] JWT 토큰 생성/검증
- [x] 비밀번호 해싱 (bcrypt)
- [x] 프로필 관리 API
- [x] 비밀번호 변경 API

### AI Agent 시스템
- [x] Market Regime Analyst (시장 상태 분석)
- [x] Sector Scout (섹터 랭킹)
- [x] Stock Screener (종목 필터링)
- [x] Trade Plan Builder (매매 계획)
- [x] Devil's Advocate (반론 생성)
- [x] Agent Orchestrator (파이프라인 통합)

### 데이터 소스
- [x] Yahoo Finance API (실시간 데이터)
- [x] OpenDART API (재무 정보)
- [x] 시장 지표 계산 (VIX, KOSPI)
- [x] Market Breadth Calculator

### 모니터링 & 로깅
- [x] 헬스 체크 엔드포인트 (/api/health)
- [x] 상태 조회 엔드포인트 (/api/status)
- [x] 요청 로깅
- [x] 에러 로깅

### 보안
- [x] CORS 설정 (API 엑세스 제어)
- [x] JWT 인증 미들웨어
- [x] 비밀번호 복잡도 검증
- [x] 환경 변수에 API 키 저장
- [x] SQLite 동시성 설정 (timeout=30)

### 문서화
- [x] 베타테스터 가이드 (BETA_TESTER_GUIDE.md)
- [x] 배포 체크리스트 (이 파일)
- [x] API 문서 (Swagger UI 자동 생성)

### 시작 스크립트
- [x] Windows Batch 스크립트 (start_backend.bat)
- [x] PowerShell 스크립트 (start_backend.ps1)
- [x] 자동 패키지 설치
- [x] 자동 DB 초기화

---

## 🚀 배포 단계

### 1단계: 베타테스터 모집 (2-3일)

**체크리스트:**
- [ ] 테스터 5명 선정
- [ ] 각 테스터에게 링크 배포
- [ ] 핸드폰 번호 수집 (긴급 연락)
- [ ] 개인정보 동의서 수집

**배포 관련 정보:**
```
- GitHub 리포지토리 (또는 ZIP 파일)
- 시작 가이드 메일 발송
- Slack/Discord 채널 생성 (피드백 수집)
```

### 2단계: 로컬 환경 설정 (1일)

**윈도우 (가장 일반적):**
```bash
# 1. start_backend.bat 더블클릭
# 또는
# 2. start_backend.ps1 실행

# 또는 수동 설정:
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -c "from database import init_db; init_db()"
python -m uvicorn server_v2:app --reload --host 0.0.0.0 --port 8000
```

**Mac/Linux:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -c "from database import init_db; init_db()"
python -m uvicorn server_v2:app --reload --host 0.0.0.0 --port 8000
```

### 3단계: 초기 테스트 (1-2일)

**필수 테스트:**
```
1. 시스템 헬스 체크
   - curl http://localhost:8000/api/health
   - 각 서비스 상태 확인

2. 회원가입 & 로그인
   - 계정 생성 테스트
   - 토큰 발급 확인
   - JWT 디코딩 검증

3. AI Agent 분석
   - 각 Agent 개별 실행
   - 전체 파이프라인 테스트
   - 응답 시간 측정

4. 동시성 테스트
   - 2명 동시 로그인
   - 2명 동시 분석 요청
   - DB 락 모니터링
```

### 4단계: 피드백 수집 (1주)

**일일 체크:**
- [ ] 각 테스터 상태 확인
- [ ] 오류 로그 모니터링
- [ ] 성능 메트릭 수집
- [ ] 피드백 수집

**주간 체크:**
- [ ] 전체 피드백 분석
- [ ] 우선순위 버그 목록화
- [ ] 개선 계획 수립

---

## 📊 성능 목표

### API 응답 시간
| 작업 | 목표 | 제한 |
|---|---|---|
| 회원가입/로그인 | < 200ms | 로그 확인|
| 프로필 조회 | < 100ms | 로그 확인 |
| 시장 분석 (Market Regime) | < 500ms | 600ms |
| 전체 Agent 분석 | < 5초 | 10초 |
| 데이터 조회 | < 300ms | 500ms |

### 시스템 리소스
| 항목 | 목표 | 제한 |
|---|---|---|
| CPU 사용률 | < 30% | < 80% |
| 메모리 사용량 | < 300MB | < 600MB |
| DB 락 호출 | 0 | > 5 = 알림 |
| 디스크 용량 | < 100MB | < 500MB |

### 가용성
| 항목 | 목표 |
|---|---|
| 서비스 가용률 | 99% (월간) |
| 평균 복구 시간 | < 5분 |
| SLA (Service Level Agreement) | 최선을 다함 |

---

## 🔍 모니터링 지표

### 매일 확인할 것
```
1. /api/health 응답 상태
   - 모든 서비스 "ok"인지 확인
   - 시간: 매 시간

2. 에러 로그
   - backend/logs/app.log 확인
   - 새 에러 발생 확인

3. DB 상태
   - stock_radar.db 파일 크기
   - 테이블 row 수 확인
   ```

### 매주 확인할 것
```
1. 성능 메트릭
   - 평균 API 응답 시간
   - 피크 시간대 분석

2. 사용자 피드백
   - Slack/Discord 메시지 검토
   - 버그 우선순위 지정

3. 데이터 정합성
   - 샘플 계산 재검증
   - OpenDART 데이터 확인
```

---

## 🚨 문제 해결 가이드

### 서버 시작 오류

**오류**: "ModuleNotFoundError: No module named 'fastapi'"
```
해결: pip install -r requirements.txt 실행
```

**오류**: "database is locked"
```
해결: 다른 프로세스 선택 후 중지하고 재시작
권장: 5분 후 자동 복구됨
```

**오류**: "Port 8000 already in use"
```
해결: 다른 포트 사용
netstat -ano | findstr 8000  # Windows
lsof -i :8000               # Mac/Linux
kill -9 <PID>               # 프로세스 제거
```

### 로그인 실패

**문제**: 회원가입은 됐는데 로그인 안 됨
```
해결:
1. 비밀번호 재확인 (대소문자 구분)
2. CAPS LOCK 확인
3. 데이터베이스 삭제 후 재초기화
   rm stock_radar.db
   python -c "from database import init_db; init_db()"
```

### Agent 분석 오류

**문제**: "5 AI Agent 실행 중 오류"
```
해결:
1. /api/health 확인
2. 로그 파일 확인 (backend/logs/app.log)
3. OpenDART API 키 확인 (.env)
4. Yahoo Finance 연결 확인 (인터넷)
```

---

## 🔄 롤백 계획

**문제 발생 시 빠른 롤백:**

```bash
# 1. 데이터베이스 백업 (매일 자동)
cp stock_radar.db stock_radar.db.backup

# 2. 최근 좋은 상태로 복구
git revert <commit_hash>
# 또는
python -m uvicorn server_v2:app --workers 1  # 안정 모드
```

**데이터 보존:**
- 사용자 계정: 보존 (자주 삭제 금지)
- 분석 이력: 보존 (나중에 학습 데이터로 사용)
- 토큰: 정기적 삭제 (만료된 것만)

---

## 📋 베타 후기 수집

### 설문 항목
```
1. 기술 난이도 (1-5)
   - 설치 및 실행 난이도
   - 사용 난이도

2. 기능 완성도 (1-5)
   - Agent 분석 정확도
   - 데이터 신뢰도
   - UI/UX 만족도

3. 성능 만족도 (1-5)
   - 응답 속도
   - 안정성

4. 개선 필요 사항
   - 버그 (리스트)
   - 기능 추가 제안
   - UI/UX 개선 제안

5. 추천 가능성
   - 다른 사람에게 추천하시겠습니까? (Yes/No)
   - 이유?
```

---

## 📅 타임라인

| 날짜 | 작업 | 담당 |
|---|---|---|
| 2.21 | 베타 배포 준비 완료 | 개발팀 |
| 2.22-2.24 | 테스터 모집 & 환경 설정 | 테스터 |
| 2.25-2.28 | 초기 테스트 & 피드백 | 테스터 |
| 3.1-3.7 | 버그 수정 & 개선 | 개발팀 |
| 3.8-3.14 | 2차 테스트 | 테스터 |
| 3.15+ | 상용 출시 준비 | 개발팀 |

---

## 📞 긴급 연락처

**24/7 지원:**
- 긴급 버그: 즉시 보고
- 성능 문제: 1시간 내 확인
- 기능 개선: 주간 정리

**지원 채널:**
- Discord: #stock-radar-beta
- Email: support@stockradar.ai
- GitHub: Issues

---

## ✨ 베타 완료 조건

**5명 모두 이 항목이 "통과"되어야 베타 종료:**

- [x] 회원가입 및 로그인 정상 작동
- [x] 5개 AI Agent 모두 분석 결과 반환
- [x] 동시성 테스트 (5명) 성공
- [x] 24시간 연속 운영 성공
- [x] 오류 로그 < 1% 미만
- [x] API 응답 시간 목표 달성
- [x] 데이터 정합성 검증 완료
- [x] 보안 점검 통과

**조건 충족 후:**
1. 베타 마무리 회의 (1시간)
2. 최종 피드백 수집
3. 상용 출시 준비
4. 감사의 말씀과 사은품 발송 계획

---

**마지막 업데이트**: 2026년 2월 21일 21:00 KST

**준비 완료! 🎉**
