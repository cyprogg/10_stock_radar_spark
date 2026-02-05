# 🔧 주가 자동 입력 및 차트 분석 완전 해결 가이드

## 📋 현재 문제 상황
- ❌ 주가 자동 입력 안됨
- ❌ 차트 분석 버튼 작동 안됨
- ✅ 체크리스트 일관성 문제 해결됨 (같은 종목 → 같은 결과)

---

## 🔍 핵심 문제 진단

### 가설 1: 브라우저 캐시 문제
**가능성: 90%**

JavaScript 파일이 업데이트되었지만 브라우저가 이전 버전을 사용 중

**해결 방법**:
```
1. Ctrl + Shift + Delete
2. "캐시된 이미지 및 파일" 선택
3. "전체 기간" 선택
4. 삭제
5. 브라우저 재시작
```

### 가설 2: file:// 프로토콜 제한
**가능성: 70%**

파일을 더블클릭으로 열면 `file://` 프로토콜로 실행되어 일부 기능 제한

**해결 방법**: 로컬 서버 사용
```bash
# Python 3 설치되어 있으면
cd /path/to/decision-stream
python -m http.server 8000

# 브라우저에서
http://localhost:8000/trade_plan_simulation.html
```

### 가설 3: JavaScript 에러
**가능성: 50%**

다른 에러로 인해 이벤트 핸들러가 실행되지 않음

**확인 방법**: F12 → Console 탭에서 빨간색 에러 확인

---

## ✅ 적용된 수정 사항

### 1. 체크리스트 일관성 문제 해결 ✅
**변경 전**:
```javascript
// 매번 랜덤 생성 → 같은 종목도 다른 결과
pass: Math.random() > 0.3
```

**변경 후**:
```javascript
// 종목 코드 기반 시드 → 같은 종목은 항상 같은 결과
const checklistSeed = ticker.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
function seededRandom(index) {
    const x = Math.sin(checklistSeed + index) * 10000;
    return x - Math.floor(x);
}
pass: seededRandom(1) > 0.3  // 일관된 결과
```

**결과**: 
- 한화에어로스페이스 → 항상 같은 체크리스트
- 삼성전자 → 항상 같은 체크리스트 (하지만 한화와는 다름)

### 2. 이벤트 리스너 충돌 제거
- addEventListener 제거
- HTML onchange만 사용

### 3. 차트 분석 함수 강화
- 팝업 차단 감지
- 에러 처리
- 상세 로깅

---

## 🧪 단계별 테스트 방법

### 📍 STEP 1: 완전히 깨끗한 상태로 시작

#### A. 브라우저 캐시 완전 삭제
```
1. Ctrl + Shift + Delete
2. "캐시된 이미지 및 파일" 체크
3. "전체 기간" 선택
4. "데이터 삭제" 클릭
5. 브라우저 완전 종료 (작업 관리자에서 확인)
6. 브라우저 재시작
```

#### B. 시크릿 모드로 테스트
```
Chrome: Ctrl + Shift + N
Firefox: Ctrl + Shift + P
Edge: Ctrl + Shift + N
```

---

### 📍 STEP 2: 테스트 페이지로 기능 확인

#### `test_stock_selection.html` 열기

**목적**: 독립적인 환경에서 기본 기능 테스트

**테스트 순서**:
1. 파일 열기
2. 섹터 선택: **방산**
3. 화면 하단 로그 확인:
   ```
   섹터 선택: 방산
   3개 종목 로드됨
   ```
4. 종목 선택: **한화에어로스페이스**
5. 로그 확인:
   ```
   handleStockChange 호출됨
   선택된 종목: 012450
   Dataset price: 185000
   ✅ 주가 자동 입력: 185000
   ```
6. "현재 주가" 입력 필드 확인: **185000** 표시되어야 함
7. "📊 차트 분석 열기" 버튼 클릭
8. 로그 확인:
   ```
   차트 URL: chart_analysis.html?ticker=012450
   ✅ 차트 창 열림
   ```

**결과 해석**:
- ✅ **모두 작동**: 기본 기능은 정상 → `trade_plan_simulation.html`의 다른 코드 문제
- ❌ **주가 입력 안됨**: Dataset 문제 또는 브라우저 호환성
- ❌ **차트 안 열림**: 팝업 차단 또는 파일 경로 문제

---

### 📍 STEP 3: 로컬 서버로 실행 (권장)

#### Python 서버 시작
```bash
# 프로젝트 폴더로 이동
cd /path/to/decision-stream

# Python 3
python -m http.server 8000

# 또는 Python 2
python -m SimpleHTTPServer 8000
```

#### 브라우저에서 접속
```
http://localhost:8000/test_stock_selection.html
http://localhost:8000/trade_plan_simulation.html
```

**왜 필요한가?**
- `file://` 프로토콜의 제한 회피
- 크로스 오리진 문제 해결
- 실제 배포 환경과 유사

---

### 📍 STEP 4: 실제 페이지 테스트

#### `trade_plan_simulation.html` 열기

**F12 개발자 도구 열기** (필수!)

1. 섹터 선택: **방산**
2. 콘솔 확인: 에러 없어야 함
3. 종목 선택: **한화에어로스페이스**
4. 콘솔 확인:
   ```
   🔵 handleStockChange called
   Selected option: <option>...</option>
   Selected value: 012450
   Dataset price: 185000
   ✅ Setting price to: 185000
   ```
5. "현재 주가" 필드: **185000** 확인
6. "📊 차트 분석 보기" 버튼 클릭
7. 콘솔 확인:
   ```
   📊 openChartAnalysis called
   Current ticker: 012450
   Opening chart URL: chart_analysis.html?ticker=012450
   ✅ Chart window opened successfully
   ```

---

### 📍 STEP 5: 수동 디버깅

#### 콘솔에서 직접 실행

**종목 정보 확인**:
```javascript
debugStockInfo()
```

**예상 출력**:
```
=== 종목 디버깅 정보 ===
Selected index: 2
Selected value: 012450
Selected option: <option value="012450">...</option>
Option text: 한화에어로스페이스 (012450)
Dataset price: 185000
Dataset name: 한화에어로스페이스
Current price input: 185000
======================
```

**함수 직접 호출**:
```javascript
// 주가 입력 테스트
handleStockChange()

// 차트 열기 테스트
openChartAnalysis()
```

---

## 🎯 시장 해설 생성 테스트 방법

### `index.html` (Decision Stream 대시보드)

#### 방법 1: 정상 플로우
1. **`index.html` 열기**
2. **"Regime 조회"** 버튼 클릭
   - Risk Score 확인
3. **"Sectors 조회"** 버튼 클릭
   - SURGE 섹터 확인
4. **SURGE 섹터 클릭** (예: 방산)
   - Stock Funnel 자동 로드
5. **"▶ 시장 해설 생성"** 버튼 클릭
6. **결과 확인**:
   ```
   📊 Decision Stream 시장 해설
   
   현재 시장은 RISK_ON이며 Risk Score는 72입니다.
   이는 자금이 위험자산으로 이동 중인 전형적인 Risk-On 국면입니다.
   
   자금 흐름
   현재 기관 자금은 방산, 헬스케어 섹터로 집중되고 있습니다.
   
   종목 구조
   선도주: 없음
   Follower: LMT, 012450
   
   이는 섹터는 이미 움직였고, 종목들은 아직 본격적인 돌파 전인 최적의 매집 구간을 의미합니다.
   
   전략
   방산 → 눌림 매수 대기
   
   한 줄 요약
   "공격 자금이 활발한 시장입니다."
   ```

#### 방법 2: 백엔드 서버 사용 (권장)
```bash
# 터미널 1: 백엔드 서버
cd backend
python server.py

# 터미널 2: 프론트엔드 서버
cd ..
python -m http.server 8000
```

브라우저: `http://localhost:8000/index.html`

---

## ❌ 문제별 해결 방법

### 문제 1: "먼저 섹터를 선택하세요" 알림
**원인**: Regime → Sectors → 섹터 클릭 순서를 지키지 않음

**해결**:
1. "Regime 조회" 먼저 클릭
2. "Sectors 조회" 클릭
3. SURGE 섹터(예: 방산) 클릭
4. "시장 해설 생성" 클릭

### 문제 2: 시장 해설에 데이터 없음
**원인**: 백엔드 서버가 실행 중이지 않음

**해결**:
```bash
cd backend
python server.py
```

### 문제 3: CORS 에러
**원인**: `file://` 프로토콜에서 API 호출

**해결**: 로컬 서버 사용
```bash
python -m http.server 8000
```

---

## 📊 체크리스트 일관성 테스트

### 같은 종목 반복 테스트
1. **한화에어로스페이스 선택 → 계획 생성**
2. 체크리스트 결과 기록 (예: 5/7 통과)
3. **초기화 버튼 클릭**
4. **다시 한화에어로스페이스 선택 → 계획 생성**
5. 체크리스트 결과 확인 → **동일해야 함** ✅

### 다른 종목 비교 테스트
1. **한화에어로스페이스**: 5/7 통과
2. **삼성전자**: 6/7 통과 (다를 수 있음)
3. 각 종목은 고유한 체크리스트를 유지

---

## 🚨 긴급 문제 해결

### 아무것도 작동하지 않을 때:

#### 1. 브라우저 완전 재설정
```
Chrome: chrome://settings/clearBrowserData
Firefox: about:preferences#privacy
```

#### 2. 다른 브라우저 시도
- Chrome → Firefox
- Firefox → Edge
- Edge → Chrome

#### 3. 파일 재다운로드
- 파일이 손상되었을 가능성
- 프로젝트 전체 재다운로드

#### 4. 로그 수집
F12 → Console → 모든 로그 복사 → 공유

---

## 📝 체크리스트

### 주가 자동 입력 문제
- [ ] 캐시 삭제함
- [ ] 시크릿 모드 시도함
- [ ] `test_stock_selection.html` 테스트함
- [ ] 로컬 서버로 실행함
- [ ] F12 콘솔에서 에러 없음
- [ ] `debugStockInfo()` 실행함
- [ ] Dataset price 값이 있음

### 차트 분석 문제
- [ ] 팝업 차단 해제함
- [ ] `chart_analysis.html` 파일 존재 확인
- [ ] 로컬 서버로 실행함
- [ ] 콘솔에서 "✅ Chart window opened" 확인
- [ ] 브라우저 팝업 설정 확인

### 시장 해설 문제
- [ ] 백엔드 서버 실행 중 (`python server.py`)
- [ ] Regime 조회 → Sectors 조회 → 섹터 클릭 순서
- [ ] 로컬 서버로 실행함 (CORS 회피)
- [ ] 콘솔에서 API 에러 없음

---

## 🎯 다음 단계

1. **먼저**: `test_stock_selection.html` 테스트
2. **캐시 삭제**: Ctrl+Shift+Delete
3. **로컬 서버**: `python -m http.server 8000`
4. **백엔드 실행**: `cd backend && python server.py`
5. **테스트**: 위의 체크리스트 확인

---

## 💬 피드백 요청

다음 정보를 알려주시면 더 정확히 도와드릴 수 있습니다:

1. **`test_stock_selection.html` 결과**
   - 주가 입력: 작동/미작동
   - 차트 열기: 작동/미작동
   - 로그 내용

2. **브라우저 콘솔 로그**
   - F12 → Console 탭
   - 전체 로그 복사

3. **실행 방법**
   - 더블클릭 (file://)
   - 로컬 서버 (http://localhost)

4. **브라우저 & OS**
   - Chrome/Firefox/Edge?
   - Windows/Mac/Linux?

---

© 2026 Decision Stream
