# 🔧 종목 선택 및 차트 분석 문제 해결 가이드

## 📋 현재 상황
- ✅ 초기화: 작동함
- ❌ 주가 자동 입력: 작동 안함
- ❌ 차트 분석 버튼: 작동 안함

---

## 🛠️ 적용된 수정 사항

### 1. 이벤트 리스너 충돌 제거
**문제**: addEventListener와 HTML onchange가 동시에 등록되어 충돌
**해결**: addEventListener 제거, HTML onchange만 사용

### 2. 차트 분석 함수 개선
**문제**: 에러 처리 부족
**해결**: 
- 팝업 차단 감지
- 에러 메시지 추가
- 상세한 로깅

### 3. 디버깅 기능 추가
- `debugStockInfo()` 함수
- 콘솔 로그 추가
- 테스트 페이지 생성

---

## 🧪 테스트 방법

### 방법 1: 테스트 페이지 사용 (권장)
1. **`test_stock_selection.html` 열기**
2. 섹터 선택: 방산
3. 종목 선택: 한화에어로스페이스
4. 화면의 로그 영역 확인:
   ```
   섹터 선택: 방산
   3개 종목 로드됨
   handleStockChange 호출됨
   선택된 종목: 012450
   Dataset price: 185000
   ✅ 주가 자동 입력: 185000
   ```
5. "📊 차트 분석 열기" 버튼 클릭
6. 새 탭에서 chart_analysis.html 열림 확인

### 방법 2: 실제 페이지 테스트
1. **`trade_plan_simulation.html` 열기**
2. **F12** 눌러서 개발자 도구 열기
3. **Console 탭** 선택
4. 섹터 선택: 방산
5. 종목 선택: 한화에어로스페이스
6. 콘솔에서 확인:
   ```
   🔵 handleStockChange called
   Selected option: <option>...</option>
   Selected value: 012450
   Dataset price: 185000
   ✅ Setting price to: 185000
   ```

---

## 🔍 문제 진단 체크리스트

### 주가 자동 입력이 안 될 때:

#### 1. 콘솔 로그 확인
브라우저 콘솔(F12)에서 다음을 확인:
```
🔵 handleStockChange called  ← 이 메시지가 보이나요?
```

**보이지 않으면**:
- HTML의 `onchange="handleStockChange()"` 속성이 제대로 있는지 확인
- 브라우저 캐시 문제: **Ctrl+Shift+R** (하드 리프레시)

**보이면**:
```
Dataset price: 185000  ← 이 값이 보이나요?
```

#### 2. 수동 테스트
콘솔에서 직접 실행:
```javascript
debugStockInfo()
```

결과 확인:
```
=== 종목 디버깅 정보 ===
Selected value: 012450
Dataset price: 185000
Current price input: 185000
```

#### 3. DOM 확인
콘솔에서:
```javascript
document.getElementById('stock').options[document.getElementById('stock').selectedIndex].dataset.price
```

값이 나와야 합니다: `"185000"`

---

### 차트 분석이 안 열릴 때:

#### 1. 팝업 차단 확인
브라우저 주소창 옆에 팝업 차단 아이콘이 있는지 확인
- Chrome: 주소창 오른쪽 끝에 🚫 아이콘
- 해결: 아이콘 클릭 → "항상 허용"

#### 2. 콘솔 로그 확인
```
📊 openChartAnalysis called
Current ticker: 012450
Opening chart URL: chart_analysis.html?ticker=012450
✅ Chart window opened successfully
```

**"❌ Popup blocked"** 메시지가 보이면:
- 브라우저 팝업 설정에서 허용

#### 3. 파일 경로 확인
콘솔에서:
```javascript
console.log(window.location.href)
```

`chart_analysis.html`이 같은 폴더에 있는지 확인

---

## 💡 빠른 해결 방법

### 문제가 계속되면:

1. **브라우저 캐시 완전 삭제**
   ```
   Ctrl + Shift + Delete
   → "캐시된 이미지 및 파일" 선택
   → 삭제
   ```

2. **시크릿 모드로 테스트**
   ```
   Ctrl + Shift + N (Chrome)
   Ctrl + Shift + P (Firefox)
   ```

3. **다른 브라우저로 테스트**
   - Chrome → Firefox
   - Firefox → Edge

4. **로컬 서버 사용**
   ```bash
   # Python 3
   python -m http.server 8000
   
   # 브라우저에서
   http://localhost:8000/trade_plan_simulation.html
   ```

---

## 🎯 예상 원인

### 주가 자동 입력 문제:
1. ❌ 브라우저 캐시 (가장 흔함)
2. ❌ JavaScript 에러로 인한 실행 중단
3. ❌ dataset 속성이 제대로 설정되지 않음

### 차트 분석 문제:
1. ❌ 팝업 차단 (가장 흔함)
2. ❌ 파일 경로 문제 (file:// 프로토콜)
3. ❌ JavaScript 에러

---

## 📊 테스트 결과 리포트

### test_stock_selection.html 사용 시:
이 테스트 페이지에서 작동하면 → 실제 페이지의 **다른 코드와 충돌**
이 테스트 페이지에서도 안 되면 → **브라우저 설정 또는 환경 문제**

---

## 🆘 여전히 안 되면:

1. **`test_stock_selection.html` 테스트 결과 알려주세요**
   - 작동하나요? Yes/No
   - 로그에 어떤 메시지가 보이나요?

2. **브라우저 콘솔 로그 전체를 복사해주세요**
   - F12 → Console 탭
   - 우클릭 → "모두 저장"

3. **브라우저 정보**
   - Chrome/Firefox/Edge?
   - 버전?
   - 운영체제?

4. **파일 열기 방법**
   - 더블클릭? (file://)
   - 로컬 서버? (http://localhost)

---

## ✅ 다음 단계

1. **먼저**: `test_stock_selection.html` 열어서 테스트
2. **성공하면**: trade_plan_simulation.html에서 캐시 삭제 후 재시도
3. **실패하면**: 위의 정보를 알려주세요

---

© 2026 Decision Stream
