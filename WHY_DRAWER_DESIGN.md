# 🔍 Why Drawer + 😈 Devil's Advocate 구현 가이드

## 개요
사용자가 점수를 클릭하면 팝업 Drawer가 열리며 **3가지 근거 + 2가지 반대의견**을 표시합니다.

---

## 🎯 설계 목표

### Why Drawer (점수 클릭 → 근거 표시)
1. **투명성** - 모든 점수는 설명 가능해야 함
2. **신뢰성** - 근거 = 데이터 출처 링크
3. **균형** - 긍정 근거 + 부정 근거 병렬 표시

### Devil's Advocate (반대 의견 자동 생성)
1. **비판적 사고** - "왜 틀릴 수 있는가?"
2. **리스크 인식** - 낙관론에 대한 견제
3. **의사결정 품질** - 양면 검토 후 판단

---

## 📐 UI 구조

### Why Drawer 모달
```
┌─────────────────────────────────────┐
│ 🔍 Why Score: 85/100?               │
│                              [닫기] │
├─────────────────────────────────────┤
│                                     │
│ 📊 자금 흐름 점수: 85/100           │
│                                     │
│ ✅ 이 점수를 지지하는 근거 (3개)    │
│   1. 외국인 5일 순매수 +15억원      │
│      출처: KRX 투자자별 매매동향 🔗 │
│   2. 기관 20일 누적 +50억원         │
│      출처: KRX 투자자별 매매동향 🔗 │
│   3. 거래대금 20일 평균 대비 +35%   │
│      출처: KRX 시장데이터 🔗        │
│                                     │
│ ⚠️ Devil's Advocate (반대 의견)    │
│   1. 개인 매도세 지속 (-30억원)     │
│      → 외국인/기관 단독 매수 취약  │
│   2. 거래대금 급증은 변동성 증가    │
│      → 단기 과열 신호 가능성       │
│                                     │
│ 🎯 신뢰도: 78%                      │
│                                     │
└─────────────────────────────────────┘
```

---

## 🧮 점수 구성 (AI_AGENT_ARCHITECTURE.md 기반)

### 1. 자금 흐름 점수 (Flow Score)
```python
# 최대 100점
- 외국인 5일 순매수 (0~15점)
- 외국인 20일 누적 (0~15점)
- 기관 5일 순매수 (0~15점)
- 기관 20일 누적 (0~15점)
- 거래대금 증가 (0~20점)
- 섹터 대비 강도 (0~20점)
```

**근거 예시**:
- ✅ "외국인 5일 누적 +25억원 (출처: KRX)"
- ✅ "기관 20일 누적 +80억원 (출처: KRX)"
- ✅ "거래대금 20일 평균 대비 +42% (출처: KRX)"

**반대 의견**:
- ⚠️ "개인 투자자 순매도 지속 (-35억원) → 외국인/기관 단독 매수는 지속성 낮음"
- ⚠️ "거래대금 급증(+42%)은 변동성 증가 신호 → 단기 과열 가능성"

---

### 2. 가격 구조 점수 (Structure Score)
```python
# 최대 100점
- 고점/저점 상승 (0~30점)
- 조정 시 거래량 감소 (0~20점)
- MA20 위 유지 (0~25점)
- MA60 위 유지 (0~25점)
```

**근거 예시**:
- ✅ "3회 연속 고점 갱신 (출처: 차트 분석)"
- ✅ "MA20(174,500원) 위 안정적 거래 (출처: 차트 분석)"
- ✅ "조정 시 거래량 -40% 감소 = 건전한 쉼 (출처: 차트 분석)"

**반대 의견**:
- ⚠️ "MA20 대비 이격률 +8% → 단기 추격 리스크"
- ⚠️ "RSI 72 → 과매수 구간 진입"

---

### 3. 서사 점수 (Narrative Score)
```python
# 최대 100점
- 뉴스 빈도 (0~40점)
- 정책 키워드 (0~30점)
- 공시 이벤트 (0~30점)
```

**근거 예시**:
- ✅ "최근 7일 관련 뉴스 18건 (출처: 네이버 금융)"
- ✅ "정책 키워드 매칭: '방산 수출', '정부 발표' (출처: 뉴스 분석)"
- ✅ "실적 공시: 수주 2조원 발표 (출처: OpenDART)"

**반대 의견**:
- ⚠️ "뉴스 급증(7일 18건)은 테마주 과열 신호"
- ⚠️ "수주 공시는 이미 주가 반영 (당일 +12% 급등)"

---

### 4. 리스크 점수 (Risk Score) ⚠️ 낮을수록 좋음
```python
# 최대 100점 (낮을수록 좋음)
- 과열/분배 봉 (0~40점)
- 테마 말기 (0~30점)
- 유동성 리스크 (0~30점)
```

**근거 예시**:
- ✅ "갭 상승 후 분배 봉 없음 (출처: 차트 분석)"
- ✅ "방산 섹터 내 2번째 급등 (선도주 위치) (출처: 섹터 분석)"
- ✅ "일 평균 거래대금 800억원 (충분한 유동성) (출처: KRX)"

**반대 의견**:
- ⚠️ "리스크 점수 25점 = 낮은 위험이지만, 과신 금지"
- ⚠️ "섹터 내 2번째 = 1번 종목 이탈 시 동반 하락 위험"

---

## 🎨 UI 컴포넌트 설계

### HTML 구조
```html
<!-- Why Drawer Modal -->
<div id="why-drawer" class="drawer" style="display:none;">
  <div class="drawer-overlay" onclick="closeWhyDrawer()"></div>
  <div class="drawer-content">
    <div class="drawer-header">
      <h3 id="drawer-title">🔍 Why Score: ?</h3>
      <button onclick="closeWhyDrawer()" class="close-btn">✕</button>
    </div>
    
    <div class="drawer-body">
      <!-- 점수 요약 -->
      <div class="score-summary">
        <div class="score-big" id="drawer-score">-</div>
        <div class="score-label" id="drawer-label">-</div>
      </div>
      
      <!-- 지지 근거 -->
      <div class="section">
        <h4>✅ 이 점수를 지지하는 근거</h4>
        <div id="supporting-reasons"></div>
      </div>
      
      <!-- 반대 의견 -->
      <div class="section devil">
        <h4>😈 Devil's Advocate (반대 의견)</h4>
        <div id="counter-reasons"></div>
      </div>
      
      <!-- 신뢰도 -->
      <div class="confidence">
        <span>🎯 신뢰도:</span>
        <span id="confidence-level">-</span>
      </div>
    </div>
  </div>
</div>
```

### CSS 스타일
```css
.drawer {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 9999;
}

.drawer-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
}

.drawer-content {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 90%;
  max-width: 600px;
  max-height: 85vh;
  background: linear-gradient(135deg, #1a1f36 0%, #232842 100%);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  overflow: hidden;
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translate(-50%, -40%);
  }
  to {
    opacity: 1;
    transform: translate(-50%, -50%);
  }
}

.drawer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.drawer-header h3 {
  margin: 0;
  font-size: 18px;
  color: #fff;
}

.close-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  font-size: 20px;
  cursor: pointer;
  transition: all 0.2s;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.drawer-body {
  padding: 24px;
  max-height: calc(85vh - 80px);
  overflow-y: auto;
}

.score-summary {
  text-align: center;
  padding: 20px;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 12px;
  margin-bottom: 24px;
}

.score-big {
  font-size: 48px;
  font-weight: 700;
  color: #667eea;
  margin-bottom: 8px;
}

.score-label {
  font-size: 14px;
  color: #aab3d6;
}

.section {
  margin-bottom: 24px;
}

.section h4 {
  font-size: 15px;
  color: #fff;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.section.devil h4 {
  color: #ef4444;
}

.reason-item {
  padding: 12px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  margin-bottom: 8px;
  line-height: 1.6;
}

.reason-item.counter {
  background: rgba(239, 68, 68, 0.1);
  border-left: 3px solid #ef4444;
}

.reason-text {
  font-size: 13px;
  color: #e8eaed;
  margin-bottom: 4px;
}

.reason-source {
  font-size: 11px;
  color: #aab3d6;
}

.reason-source a {
  color: #667eea;
  text-decoration: none;
}

.reason-source a:hover {
  text-decoration: underline;
}

.confidence {
  text-align: center;
  padding: 16px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  font-size: 14px;
  color: #aab3d6;
}

.confidence span:last-child {
  font-weight: 700;
  color: #667eea;
  margin-left: 8px;
}
```

---

## 📊 데이터 구조

### Score Object
```javascript
const scoreData = {
  type: 'flow',  // flow, structure, narrative, risk
  score: 85,
  label: '자금 흐름',
  
  supportingReasons: [
    {
      text: '외국인 5일 누적 순매수 +25억원',
      source: 'KRX 투자자별 매매동향',
      link: 'http://data.krx.co.kr',
      weight: 15  // 점수 기여도
    },
    {
      text: '기관 20일 누적 순매수 +80억원',
      source: 'KRX 투자자별 매매동향',
      link: 'http://data.krx.co.kr',
      weight: 15
    },
    {
      text: '거래대금 20일 평균 대비 +42%',
      source: 'KRX 시장데이터',
      link: 'http://data.krx.co.kr',
      weight: 20
    }
  ],
  
  counterArguments: [
    {
      text: '개인 투자자 순매도 지속 (-35억원)',
      impact: '외국인/기관 단독 매수는 지속성 낮음',
      severity: 'medium'  // low, medium, high
    },
    {
      text: '거래대금 급증(+42%)은 변동성 증가 신호',
      impact: '단기 과열 가능성',
      severity: 'medium'
    }
  ],
  
  confidence: 78  // 0-100%
};
```

---

## 🔧 JavaScript 구현

### 1. Why Drawer 열기
```javascript
function openWhyDrawer(scoreType, stock) {
  // 점수 데이터 생성
  const scoreData = generateScoreData(scoreType, stock);
  
  // UI 업데이트
  $('#drawer-title').innerText = `🔍 Why ${scoreData.label}: ${scoreData.score}/100?`;
  $('#drawer-score').innerText = scoreData.score;
  $('#drawer-label').innerText = scoreData.label;
  
  // 지지 근거 렌더링
  renderSupportingReasons(scoreData.supportingReasons);
  
  // 반대 의견 렌더링
  renderCounterArguments(scoreData.counterArguments);
  
  // 신뢰도 표시
  $('#confidence-level').innerText = `${scoreData.confidence}%`;
  
  // 모달 표시
  $('#why-drawer').style.display = 'block';
}

function closeWhyDrawer() {
  $('#why-drawer').style.display = 'none';
}
```

### 2. 점수 데이터 생성 (Devil's Advocate 로직)
```javascript
function generateScoreData(scoreType, stock) {
  // Mock 데이터 (실제로는 API에서 가져옴)
  const baseData = {
    flow: {
      score: 85,
      label: '자금 흐름',
      supportingReasons: [
        {
          text: `외국인 5일 누적 순매수 +${(Math.random() * 30 + 10).toFixed(0)}억원`,
          source: 'KRX 투자자별 매매동향',
          link: 'http://data.krx.co.kr',
          weight: 15
        },
        {
          text: `기관 20일 누적 순매수 +${(Math.random() * 80 + 40).toFixed(0)}억원`,
          source: 'KRX 투자자별 매매동향',
          link: 'http://data.krx.co.kr',
          weight: 15
        },
        {
          text: `거래대금 20일 평균 대비 +${(Math.random() * 40 + 20).toFixed(0)}%`,
          source: 'KRX 시장데이터',
          link: 'http://data.krx.co.kr',
          weight: 20
        }
      ]
    },
    structure: {
      score: 78,
      label: '가격 구조',
      supportingReasons: [
        {
          text: '3회 연속 고점 갱신 (상승 추세 확립)',
          source: '차트 분석',
          link: '#',
          weight: 30
        },
        {
          text: `MA20(${stock.price * 0.97}원) 위 안정적 거래`,
          source: '차트 분석',
          link: '#',
          weight: 25
        },
        {
          text: '조정 시 거래량 -40% 감소 (건전한 쉼)',
          source: '차트 분석',
          link: '#',
          weight: 20
        }
      ]
    },
    narrative: {
      score: 72,
      label: '서사',
      supportingReasons: [
        {
          text: '최근 7일 관련 뉴스 18건',
          source: '네이버 금융',
          link: 'https://finance.naver.com',
          weight: 30
        },
        {
          text: '정책 키워드: 방산 수출, 정부 발표',
          source: '뉴스 분석',
          link: '#',
          weight: 20
        },
        {
          text: '실적 공시: 수주 2조원 발표',
          source: 'OpenDART',
          link: 'https://dart.fss.or.kr',
          weight: 30
        }
      ]
    },
    risk: {
      score: 25,
      label: '리스크 (낮을수록 좋음)',
      supportingReasons: [
        {
          text: '갭 상승 후 분배 봉 없음',
          source: '차트 분석',
          link: '#',
          weight: -40  // 리스크이므로 음수
        },
        {
          text: '방산 섹터 내 2번째 급등 (선도주 위치)',
          source: '섹터 분석',
          link: '#',
          weight: -30
        },
        {
          text: '일 평균 거래대금 800억원 (충분한 유동성)',
          source: 'KRX',
          link: 'http://data.krx.co.kr',
          weight: -30
        }
      ]
    }
  };
  
  const data = baseData[scoreType];
  
  // Devil's Advocate: 자동으로 반대 의견 생성
  data.counterArguments = generateCounterArguments(scoreType, data);
  
  // 신뢰도 계산
  data.confidence = calculateConfidence(data);
  
  return data;
}
```

### 3. Devil's Advocate 로직
```javascript
function generateCounterArguments(scoreType, data) {
  const arguments = {
    flow: [
      {
        text: `개인 투자자 순매도 지속 (-${(Math.random() * 30 + 20).toFixed(0)}억원)`,
        impact: '외국인/기관 단독 매수는 지속성 낮음',
        severity: 'medium'
      },
      {
        text: `거래대금 급증은 변동성 증가 신호`,
        impact: '단기 과열 가능성',
        severity: 'medium'
      }
    ],
    structure: [
      {
        text: `MA20 대비 이격률 +${(Math.random() * 10 + 5).toFixed(1)}%`,
        impact: '단기 추격 리스크',
        severity: 'low'
      },
      {
        text: `RSI ${(Math.random() * 15 + 65).toFixed(0)}`,
        impact: '과매수 구간 진입',
        severity: 'medium'
      }
    ],
    narrative: [
      {
        text: '뉴스 급증(7일 18건)은 테마주 과열 신호',
        impact: '단기 모멘텀 피로도 증가',
        severity: 'high'
      },
      {
        text: '수주 공시는 이미 주가 반영 (당일 +12% 급등)',
        impact: '추가 상승 모멘텀 제한적',
        severity: 'medium'
      }
    ],
    risk: [
      {
        text: '리스크 점수 25점 = 낮은 위험이지만, 과신 금지',
        impact: '예상치 못한 이벤트 발생 가능',
        severity: 'low'
      },
      {
        text: '섹터 내 2번째 = 1번 종목 이탈 시 동반 하락',
        impact: '섹터 리더 의존 리스크',
        severity: 'medium'
      }
    ]
  };
  
  return arguments[scoreType] || [];
}
```

### 4. UI 렌더링
```javascript
function renderSupportingReasons(reasons) {
  const container = $('#supporting-reasons');
  container.innerHTML = '';
  
  reasons.forEach((reason, idx) => {
    const div = document.createElement('div');
    div.className = 'reason-item';
    div.innerHTML = `
      <div class="reason-text">${idx + 1}. ${reason.text}</div>
      <div class="reason-source">
        출처: <a href="${reason.link}" target="_blank">${reason.source} 🔗</a>
        ${reason.weight ? ` | 기여도: ${Math.abs(reason.weight)}점` : ''}
      </div>
    `;
    container.appendChild(div);
  });
}

function renderCounterArguments(arguments) {
  const container = $('#counter-reasons');
  container.innerHTML = '';
  
  arguments.forEach((arg, idx) => {
    const severityColor = {
      low: '#fbbf24',
      medium: '#fb923c',
      high: '#ef4444'
    }[arg.severity];
    
    const div = document.createElement('div');
    div.className = 'reason-item counter';
    div.innerHTML = `
      <div class="reason-text">
        <span style="color:${severityColor};">⚠️</span> ${idx + 1}. ${arg.text}
      </div>
      <div class="reason-source">
        → ${arg.impact}
      </div>
    `;
    container.appendChild(div);
  });
}
```

### 5. 신뢰도 계산
```javascript
function calculateConfidence(data) {
  let confidence = data.score;
  
  // 반대 의견이 많을수록 신뢰도 하락
  const severityWeight = { low: 5, medium: 10, high: 15 };
  data.counterArguments.forEach(arg => {
    confidence -= severityWeight[arg.severity];
  });
  
  // 0-100 범위 유지
  return Math.max(0, Math.min(100, confidence));
}
```

---

## 🎬 사용자 시나리오

### 시나리오 1: 자금 흐름 점수 확인
```
1. 사용자가 Watch & Checklist에서 종목 선택
2. "자금 흐름: 85점" 표시
3. 사용자가 "85점" 클릭
4. Why Drawer 열림
5. 3가지 근거 확인:
   - 외국인 5일 +25억원
   - 기관 20일 +80억원
   - 거래대금 +42%
6. 2가지 반대 의견 확인:
   - 개인 순매도 -35억원
   - 거래대금 급증 = 과열 신호
7. 신뢰도 78% 확인
8. 종합 판단 후 닫기
```

---

## 📚 관련 문서

- [AI_AGENT_ARCHITECTURE.md](AI_AGENT_ARCHITECTURE.md) - Agent 5: Devil's Advocate 설계
- [INVESTMENT_FRAMEWORK_9_FACTORS.md](INVESTMENT_FRAMEWORK_9_FACTORS.md) - 점수 계산 철학
- [ALGORITHM_9_FACTORS_INTEGRATION.md](ALGORITHM_9_FACTORS_INTEGRATION.md) - 점수 통합 로직

---

**작성일**: 2026-01-27  
**버전**: v1.0  
**상태**: ✅ 설계 완료 → 구현 준비
