# 🔐 개발팀 내부 가이드: Know-How 보호

**대상**: 개발팀 모든 멤버  
**기준일**: 2026년 2월 21일

---

## ⚠️ 중요

이 프로젝트는 **알고리즘 Know-How가 핵심 자산**입니다.

- ❌ **절대 하면 안 됨**: 알고리즘 상세를 API 응답이나 공개 문서에 포함
- ✅ **해야 할 일**: 기능 결과만 공개, 내부 로직은 비공개

---

## 🚫 하면 안 되는 것들

### 1. API docstring에 알고리즘 설명
```python
# ❌ 나쁜 예
@app.get("/api/analyze")
def analyze(ticker: str):
    """
    Stock Screener로 6가지 No-Go 규칙과 
    9개 필수 조건을 체크하여 LEADER/FOLLOWER/NO_GO 분류
    """
    ...

# ✅ 좋은 예
@app.get("/api/analyze")
def analyze(ticker: str):
    """
    종목을 분류합니다 (LEADER/FOLLOWER/NO_GO)
    """
    ...
```

### 2. 응답에 내부 계산 상세 포함
```python
# ❌ 나쁤 예
{
    "ticker": "005930",
    "classification": "LEADER",
    "details": {
        "no_go_rules_passed": "6/6",
        "mandatory_conditions": ["flow_score > 70", "quality > 60", ...],
        "confidence_calculation": "flow:40% + quality:30% + ..."
    }
}

# ✅ 좋은 예
{
    "ticker": "005930",
    "classification": "LEADER",
    "confidence": 0.92
}
```

### 3. 코드 주석 공개
```python
# ❌ GitHub 공개 저장소에 올리면 안 됨
def _calculate_confidence(scores):
    # No-Go 규칙: 1) 부도위험 > 30%
    #            2) 자본금 < 100억
    #            3) PER > 50
    #            4) 부채비 > 500%
    #            5) 외국인 순매도 확대
    #            6) 기술적 이격 > 30%
    ...

# ℹ️ private 저장소에서만 가능
```

### 4. 고급 설정을 기본값으로 노출
```python
# ❌ 나쁜 예: 알고리즘 파라미터 노출
app.get("/api/config")
{
    "vix_threshold": 18,
    "ma_period": [50, 200],
    "flow_ratio": 0.7,
    "no_go_rules": [...]
}

# ✅ 좋은 예: 사용자가 설정하는 것만 노출
{
    "risk_profile": "중립",
    "investment_period": "중기"
}
```

---

## ✅ 해야 할 것들

### 1. API 문서는 간결하게
```python
@router.post("/api/auth/login")
async def login(request: UserLoginRequest):
    """
    로그인하여 JWT 토큰을 받습니다.
    
    - username: 사용자명
    - password: 비밀번호
    
    Returns: access_token (24시간 유효)
    """
    ...
```

### 2. 응답은 최소 정보만
```python
return {
    "classification": "LEADER",      # 분류 결과
    "confidence": 0.92,               # 신뢰도 (0-1)
    "recommendation": "매수",         # 추천도
    "message": "종목 분석 완료"       # 사용자 메시지
}
```

### 3. 에러도 일반화
```python
# ❌ 나쁜 예: 내부 에러 노출
{
    "error": "No-Go Rule #4 failed: debt_ratio=520% > 500%"
}

# ✅ 좋은 예: 일반 메시지만
{
    "error": "분석 결과 비추천 종목입니다",
    "code": "NOT_RECOMMENDED"
}
```

### 4. Swagger UI(/docs) 기본 설정
```python
# FastAPI는 docstring 자동 생성하므로
# docstring을 항상 간결하게!

app = FastAPI(
    title="Stock Radar Spark",
    description="AI 기반 주식 분석 플랫폼",
    # version, contact 등만 포함
    # 알고리즘 상세는 NO
)
```

---

## 📋 코드 리뷰 체크리스트

PR 머지 전 반드시 확인:

```
PR 체크리스트:

API 변경사항:
- [ ] docstring에 알고리즘 상세 없음
- [ ] 응답에 내부 계산 과정 없음
- [ ] 에러 메시지가 일반화됨
- [ ] Swagger UI(/docs)에서 민감 정보 확인

코드 변경사항:
- [ ] 주석이 너무 상세하지 않음 (private 저장소 확인)
- [ ] 설정값이 환경변수에 있음 (.env)
- [ ] 로그에 민감 정보 없음

문서 변경사항:
- [ ] ALGORITHM_*.md는 .gitignore에 있음
- [ ] PUBLIC_API_GUIDE.md는 기능만 설명
- [ ] 내부 문서는 팀 공유 폴더에만 있음
```

---

## 🔄 상황별 대응

### 상황 1: 테스터가 "어떻게 LEADER인지 알고 싶어요"

```
테스터: 왜 이 종목이 LEADER인가요?
       어떤 기준인가요?

답변:
"우리의 AI 시스템은 여러 요소를 종합적으로
분석합니다. 신뢰도 92%는 높은 확율을 의미하고,
매수 추천은 신뢰할 수 있습니다.

상세 알고리즘은 회사의 지적재산이라
공개할 수 없습니다. 죄송합니다."
```

### 상황 2: 개발자가 내부 알고리즘 코드를 GitHub에 올리려 함

```
❌ 절대 금지

코드에 알고리즘 상세가 있으면:
1. repo.private 설정 필수
2. 또는 팀 공유 폴더에만 저장
3. GitHub는 최종 코드만 (주석 없는 버전)
```

### 상황 3: API 응답이 너무 상세해짐

```
응답 구조 간소화:

Before:
{
  "ticker": "005930",
  "scores": {
    "flow_score": 85,
    "quality_score": 92,
    "governance_score": 78,
    ...  // 이건 내부 계산
  }
}

After:
{
  "ticker": "005930",
  "classification": "LEADER",
  "confidence": 0.92  // 최종 결과만
}
```

---

## 📚 문서 구조

```
public (GitHub public repo):
├── PUBLIC_API_GUIDE.md          ✅ 공개 OK
├── BETA_TESTER_GUIDE.md         ✅ 공개 OK
├── README.md                    ✅ 공개 OK
├── server_v2.py                 ✅ 공개 (알고리즘 주석 제거)
└── backend/agents/*.py          ✅ 공개 (기본 로직만)

private (팀 저장소 또는 공유 폴더):
├── ALGORITHM_*.md               🔐 비공개
├── AI_AGENT_ARCHITECTURE.md     🔐 비공개
├── backend/agents/*.py (full)   🔐 비공개 (상세 주석)
├── API_KEY_MANAGEMENT.md        🔐 비공개
└── benchmark_results/           🔐 비공개
```

---

## 🛡️ 보안 점검

### 배포 전 보안 체크

```bash
# 1. 민감 정보 스캔
grep -r "no.go\|mandatory\|condition\|rule" \
  backend/ --include="*.py" | \
  grep -E "(def |return |print|response)" 
  # 알고리즘 관련 노출 확인

# 2. API 문서 점검
curl http://localhost:8000/docs | \
  grep -i "algorithm\|rule\|condition" 
  # 공개된 세부사항 없는지 확인

# 3. 로그 파일 점검
grep -i "rule\|condition\|score" logs/*.log 
# 민감한 로그 없는지 확인
```

---

## 📞 정책 위반 시

```
발견 즉시:
1. 문제 보고 (리더에게)
2. 원인 분석
3. 수정 (remove, rebase)
4. 재학습 (정책 재교육)

심각한 유출의 경우:
1. GitHub 히스토리 수정
2. 커밋 삭제 (BFG Repo-Cleaner)
3. 전체 팀 공지
```

---

## 🎓 온보딩 체크리스트

새 팀원이 합류할 때:

- [ ] INTERNAL_DOCUMENTATION_POLICY.md 읽음
- [ ] 이 가이드 숙지
- [ ] 알고리즘 상세 문서는 팀 폴더에서만 읽음
- [ ] GitHub 권한 설정 (public/private)
- [ ] .gitignore 확인
- [ ] 서명: "Know-How 보호 동의서"

---

## 📝 변경 이력

| 날짜 | 변경사항 |
|---|---|
| 2026-02-21 | 초기 작성 |

---

**이 정책을 따르면 우리의 Know-How를 보호하면서도**  
**사용자에게는 최고의 경험을 제공할 수 있습니다.**

**감사합니다! 🙏**
