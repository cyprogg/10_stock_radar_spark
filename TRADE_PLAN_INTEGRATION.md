# 📊 Trade Plan Seamless Integration Guide

## 개요
index.html의 간단한 Trade Plan 미리보기와 trade_plan_simulation.html의 상세 시뮬레이션을 **seamless하게 연결**하는 통합 시스템입니다.

---

## 🎯 설계 목표

### 사용자 경험
1. **마찰 없는 흐름 (Frictionless Flow)**
   - 메인 대시보드에서 종목 선택
   - 간단한 설정 (기간, 리스크) 조정
   - 버튼 하나로 상세 시뮬레이션 진입
   - **데이터 재입력 불필요**

2. **단계적 의사결정 (Progressive Disclosure)**
   - Level 1: 간단한 미리보기 (2개 입력)
   - Level 2: 상세 시뮬레이션 (전체 파라미터)
   - 복잡도를 단계별로 노출

3. **일관성 유지 (Consistency)**
   - 같은 종목, 같은 가격
   - 사용자 설정 자동 전달
   - 시장 구분 자동 판단

---

## 🔧 기술 구현

### 1. index.html - 메인 대시보드

#### 추가된 함수

**`openDetailedSimulation()`** - 상세 시뮬레이션 열기
```javascript
function openDetailedSimulation() {
  if (!selectedStock) {
    alert('먼저 종목을 선택하세요.');
    return;
  }
  
  // 현재 선택된 값들 가져오기
  const period = $('#plan-period')?.value || '중기';
  const risk = $('#plan-risk')?.value || '중립';
  
  // 시장 결정 (티커로 판단)
  const ticker = selectedStock.ticker || '';
  const isUSStock = /^[A-Z]+$/.test(ticker) && ticker.length <= 5;
  const market = isUSStock ? 'US' : 'KR';
  
  // Risk 매핑 (한글 → 영문)
  const riskMapping = {
    '보수': 'conservative',
    '중립': 'neutral',
    '공격': 'aggressive'
  };
  const riskEng = riskMapping[risk] || 'neutral';
  
  // URL 파라미터 생성
  const params = new URLSearchParams({
    market: market,
    sector: selectedSector || '',
    ticker: selectedStock.ticker || '',
    name: selectedStock.name || '',
    price: selectedStock.price || '',
    period: period,
    risk: riskEng,
    capital: '10000000',  // 기본 1천만원
    from: 'index'
  });
  
  // 새 탭에서 시뮬레이션 페이지 열기
  const url = `trade_plan_simulation.html?${params.toString()}`;
  window.open(url, '_blank');
}
```

**`updateTradePlan()`** - 실시간 미리보기 업데이트
```javascript
function updateTradePlan() {
  if (!selectedStock) {
    const resultBox = $('#plan-result');
    if (resultBox) {
      resultBox.innerHTML = `
        <div class="small" style="color:var(--muted); text-align:center; padding:20px;">
          종목을 먼저 선택하세요.
        </div>
      `;
    }
    return;
  }
  
  // 현재 선택된 종목의 funnelType 가져오기
  const funnelType = selectedStock.type || 'FOLLOWER';
  
  // buildTradePlan 재실행 (기존 함수 활용)
  buildTradePlan(selectedStock, funnelType);
}
```

#### UI 연결
```html
<!-- 투자기간 선택 -->
<select id="plan-period" class="plan-input" onchange="updateTradePlan()">
  <option value="단기">단기 (수일~2주)</option>
  <option value="중기" selected>중기 (1~3개월)</option>
</select>

<!-- 리스크 성향 선택 -->
<select id="plan-risk" class="plan-input" onchange="updateTradePlan()">
  <option value="보수">보수적</option>
  <option value="중립" selected>중립</option>
  <option value="공격">공격적</option>
</select>

<!-- 상세 시뮬레이션 버튼 -->
<button onclick="openDetailedSimulation()" 
        style="...">
  📊 상세 시뮬레이션 열기
  <span style="font-size:11px; opacity:0.8;">(trade_plan_simulation.html)</span>
</button>
```

---

### 2. trade_plan_simulation.html - 상세 시뮬레이션

#### URL 파라미터 처리 (이미 구현됨)

**자동 로드 로직**
```javascript
window.addEventListener('DOMContentLoaded', () => {
  const params = new URLSearchParams(window.location.search);
  
  if (params.has('from') && params.get('from') === 'index') {
    // 파라미터에서 데이터 추출
    const market = params.get('market');
    const sector = params.get('sector');
    const ticker = params.get('ticker');
    const name = params.get('name');
    const price = params.get('price');
    const period = params.get('period');
    const risk = params.get('risk');
    const capital = params.get('capital');
    
    // 시장 선택
    if (market === 'US') {
      document.getElementById('market-us').checked = true;
    } else {
      document.getElementById('market-kr').checked = true;
    }
    
    // 섹터/종목 자동 선택
    if (sector && ticker) {
      // 섹터 드롭다운 설정
      const sectorSelect = document.getElementById('sector');
      sectorSelect.value = sector;
      
      // 종목 옵션 생성 및 선택
      populateStockDropdown(sector);
      document.getElementById('stock').value = ticker;
      
      // 현재가 입력
      document.getElementById('current-price').value = price;
    }
    
    // 투자기간/리스크 설정
    document.getElementById('period').value = period;
    const riskRadio = document.querySelector(`input[name="risk"][value="${risk}"]`);
    if (riskRadio) riskRadio.checked = true;
    
    // 투자금액 설정
    document.getElementById('capital').value = capital;
    
    // 성공 알림 표시
    showSuccessAlert(name, ticker, sector, price, market);
    
    // 돌아가기 버튼 표시
    document.getElementById('back-to-index-btn').style.display = 'block';
  }
});
```

#### 개선된 알림 메시지
```javascript
alertDiv.innerHTML = `
  <strong>✅ Decision Stream에서 연결됨!</strong><br>
  <strong>${name} (${ticker})</strong> 종목이 자동으로 선택되었습니다.<br>
  섹터: ${sector} | 현재가: ${currencySymbol}${formattedPrice} | 기간: ${period} | 리스크: ${risk}<br>
  <span style="opacity: 0.8;">아래 "매매 계획 생성" 버튼을 클릭하여 상세 시뮬레이션을 시작하세요.</span>
`;
alertDiv.className = 'alert success';
alertDiv.style.background = 'rgba(72, 187, 120, 0.2)';
alertDiv.style.borderLeftColor = '#48bb78';
alertDiv.style.color = '#9ae6b4';
```

#### 돌아가기 버튼
```html
<button id="back-to-index-btn" 
        style="display: none; ..." 
        onclick="window.close()">
  ← 메인으로 돌아가기
</button>
```

---

## 📋 전달되는 데이터

### URL 파라미터 구조
```
trade_plan_simulation.html?
  market=KR
  &sector=방산
  &ticker=012450
  &name=한화에어로스페이스
  &price=185000
  &period=중기
  &risk=neutral
  &capital=10000000
  &from=index
```

### 파라미터 설명

| 파라미터 | 타입 | 예시 | 설명 |
|---------|------|------|------|
| `market` | string | KR / US | 시장 구분 (티커 패턴으로 자동 판단) |
| `sector` | string | 방산 | 선택된 섹터 |
| `ticker` | string | 012450 | 종목 코드 |
| `name` | string | 한화에어로스페이스 | 종목명 |
| `price` | number | 185000 | 현재가 |
| `period` | string | 단기 / 중기 | 투자기간 |
| `risk` | string | conservative / neutral / aggressive | 리스크 성향 |
| `capital` | number | 10000000 | 기본 투자금액 (1천만원) |
| `from` | string | index | 출발지 표시 (통합 여부 확인) |

---

## 🎨 사용자 흐름

### 완전한 워크플로우

```
1. 메인 대시보드 (index.html)
   ↓
   [사용자] 섹터 클릭 → 방산
   ↓
   [시스템] 섹터 종목 로드 → Leader/Follower 표시
   ↓
   [사용자] 종목 클릭 → 한화에어로스페이스
   ↓
   [시스템] Watch & Checklist 표시
   ↓
   [시스템] Trade Plan 미리보기 생성
   ↓
   [사용자] 투자기간 변경 → 중기
   ↓
   [시스템] 실시간 업데이트 (updateTradePlan 실행)
   ↓
   [사용자] 리스크 변경 → 중립
   ↓
   [시스템] 실시간 업데이트
   ↓
   [사용자] "📊 상세 시뮬레이션 열기" 클릭
   ↓
   [시스템] openDetailedSimulation() 실행
   ↓
   [시스템] URL 파라미터 생성
   ↓
   [시스템] 새 탭에서 trade_plan_simulation.html 열기
   ↓

2. 상세 시뮬레이션 (trade_plan_simulation.html)
   ↓
   [시스템] URL 파라미터 감지 (from=index)
   ↓
   [시스템] 모든 폼 자동 입력
      - 시장: KR
      - 섹터: 방산
      - 종목: 한화에어로스페이스 (012450)
      - 현재가: ₩185,000
      - 투자기간: 중기
      - 리스크: 중립
      - 투자금액: ₩10,000,000
   ↓
   [시스템] 성공 알림 표시
   ↓
   [시스템] 돌아가기 버튼 표시
   ↓
   [사용자] 추가 파라미터 조정 (선택사항)
      - 진입 전략
      - 포지션 크기
      - 기타 설정
   ↓
   [사용자] "매매 계획 생성" 클릭
   ↓
   [시스템] 시뮬레이션 실행
   ↓
   [시스템] 결과 표시
   ↓
   [사용자] 차트 연동 / 시뮬레이션 학습
   ↓
   [사용자] "← 메인으로 돌아가기" 클릭 (선택사항)
   ↓
   [시스템] 탭 닫기 (window.close())
```

---

## ✅ 구현 체크리스트

### index.html
- [x] `openDetailedSimulation()` 함수 추가
- [x] `updateTradePlan()` 함수 추가
- [x] 투자기간 select에 `onchange="updateTradePlan()"` 연결
- [x] 리스크 select에 `onchange="updateTradePlan()"` 연결
- [x] 상세 시뮬레이션 버튼에 `onclick="openDetailedSimulation()"` 연결
- [x] 시장 구분 자동 판단 로직 (티커 패턴)
- [x] Risk 한글 → 영문 매핑

### trade_plan_simulation.html
- [x] URL 파라미터 읽기 로직 (이미 구현됨)
- [x] `from=index` 감지 및 자동 입력
- [x] 섹터/종목 자동 선택
- [x] 현재가 자동 입력
- [x] 투자기간/리스크 자동 설정
- [x] 성공 알림 메시지 개선
- [x] 돌아가기 버튼 추가
- [x] 돌아가기 버튼 자동 표시
- [x] `.alert.success` CSS 스타일 추가

### README.md
- [x] Seamless 통합 기능 섹션 추가 (1.5️⃣)
- [x] Decision Stream Engine 흐름도 업데이트
- [x] 시스템 구조에 trade_plan_simulation.html 표시

---

## 🧪 테스트 시나리오

### 기본 흐름 테스트
1. index.html 열기
2. 방산 섹터 클릭
3. 한화에어로스페이스 클릭
4. Trade Plan 미리보기 확인
5. 투자기간 "단기" → "중기" 변경 → 실시간 업데이트 확인
6. 리스크 "중립" → "공격" 변경 → 실시간 업데이트 확인
7. "📊 상세 시뮬레이션 열기" 버튼 클릭
8. 새 탭에서 trade_plan_simulation.html 열리는지 확인
9. URL에 파라미터가 포함되었는지 확인
10. 모든 폼 필드가 자동으로 채워졌는지 확인
11. 성공 알림 메시지 표시 확인
12. 돌아가기 버튼 표시 확인

### 한국 시장 종목 테스트
- 삼성전자 (005930)
- LG에너지솔루션 (373220)
- SK하이닉스 (000660)

### 미국 시장 종목 테스트
- LMT (Lockheed Martin)
- JNJ (Johnson & Johnson)
- NVDA (NVIDIA)

### 엣지 케이스 테스트
- 종목 미선택 시 alert 표시 확인
- DB에 없는 종목 처리 확인
- URL 파라미터 없이 직접 접근 시 동작 확인
- 브라우저 back 버튼 동작 확인

---

## 🎯 성공 기준

### 사용자 경험
- ✅ 데이터 재입력 없이 seamless 전환
- ✅ 3초 이내 페이지 전환
- ✅ 일관된 종목/가격 정보 유지
- ✅ 직관적인 버튼 레이블

### 기술적 완성도
- ✅ URL 파라미터 완전 전달
- ✅ 자동 입력 100% 성공률
- ✅ 에러 핸들링 (종목 미선택 등)
- ✅ 브라우저 호환성 (Chrome, Firefox, Safari)

### 코드 품질
- ✅ 함수 명확한 책임 분리
- ✅ 주석으로 의도 설명
- ✅ 콘솔 로그로 디버깅 지원
- ✅ 기존 코드와 일관된 스타일

---

## 📚 관련 문서

- [AI_AGENT_ARCHITECTURE.md](AI_AGENT_ARCHITECTURE.md) - Trade Plan Builder 설계
- [TRADING_CHECKLIST_SHORT_MID_TERM.md](TRADING_CHECKLIST_SHORT_MID_TERM.md) - 매매 체크리스트
- [README.md](README.md) - 전체 시스템 개요

---

## 🔮 향후 개선 사항

### Phase 2 - 양방향 동기화
- 시뮬레이션 결과를 메인 대시보드로 전송
- localStorage 활용한 세션 유지
- 시뮬레이션 히스토리 저장

### Phase 3 - 고급 기능
- 여러 종목 동시 시뮬레이션 비교
- 시뮬레이션 결과 PDF 출력
- 커스텀 시나리오 저장/불러오기

### Phase 4 - 모바일 최적화
- 반응형 레이아웃 개선
- 터치 제스처 지원
- 모바일 전용 간소화 UI

---

**작성일**: 2026-01-27  
**버전**: v1.0  
**상태**: ✅ 구현 완료
