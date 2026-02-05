# 🧩 섹터 판단 프레임워크 - Decision Stream v2.0

## 🎯 핵심 철학

> **"섹터는 '고르는 대상'이 아니라 종목 판단의 '배경 조건'이다"**

**섹터는 많을수록 좋은 것이 아니라, '설명 가능한 최소 개수'가 정답입니다.**

---

## 1️⃣ 섹터는 총 몇 개가 적당한가?

### ✅ 권장 개수 (시장별)

| 시장 | 섹터 개수 | 비고 |
|------|----------|------|
| **한국** | 12~15개 | 자금과 이슈가 같이 움직이는 묶음 |
| **미국** | 10~12개 | ETF 기준 매핑 (XLK, XLE 등) |
| **테마성** | 3~5개 | 조건부 활성화 |

### 📊 총합 권장: **15~18개 이내**

#### 📌 이유

```
✅ 이보다 많으면: 사용자도, 시스템도 판단이 흐려짐
✅ 이보다 적으면: 설명이 거칠어짐
✅ 최적 범위: 관리 가능 + 판단 안정성
```

---

## 2️⃣ 섹터 선정 기준 (중요)

### ❌ 하지 않는 방식

```
- KRX/WICS/GICS 산업 분류표를 그대로 나열
- "기계", "화학", "섬유" 같은 교과서식 분류
- 종목 수가 많다는 이유로 포함
```

### ⭐ Decision Stream v2.0 방식

```python
def is_valid_sector(sector):
    """
    섹터 유효성 검증
    
    기준:
    1. 자금과 이슈가 '같이 움직이는 묶음'
    2. "뉴스 한 줄로 묶을 수 있는가?"
    3. ETF/펀드가 존재하는가? (미국)
    
    Returns:
        valid: True/False
        reason: 판정 사유
    """
    
    # 1. 동조성 체크
    stocks = get_stocks_in_sector(sector)
    correlation = calculate_price_correlation(stocks, days=20)
    
    if correlation < 0.5:
        return False, "개별 종목 움직임이 분산됨"
    
    # 2. 이슈 통일성
    news_keywords = extract_common_keywords(sector, days=7)
    if len(news_keywords) < 2:
        return False, "공통 이슈 없음"
    
    # 3. 자금 흐름 추적 가능성
    has_etf = check_etf_exists(sector)
    if not has_etf and sector not in CORE_SECTORS:
        return False, "자금 흐름 추적 불가"
    
    return True, "유효한 섹터"
```

---

## 3️⃣ 한국 시장 권장 섹터 세트 (14개)

### 기술/성장 섹터 (7개)

| 섹터 | 대표 종목 | 뉴스 묶음 예시 |
|------|----------|----------------|
| **반도체/장비** | 삼성전자, SK하이닉스 | "반도체 수출 증가" |
| **2차전지** | LG에너지솔루션, 삼성SDI | "배터리 수주" |
| **자동차** | 현대차, 기아 | "전기차 판매" |
| **바이오** | 삼성바이오로직스, 셀트리온 | "신약 승인" |
| **헬스케어** | 의료기기, 건강관리 | "고령화, 원격진료" |
| **IT플랫폼** | 네이버, 카카오 | "플랫폼 규제" |
| **AI/로봇** | AI 반도체, 로봇 | "AI 투자" |

### 전통/방어 섹터 (4개)

| 섹터 | 대표 종목 | 뉴스 묶음 예시 |
|------|----------|----------------|
| **금융** | KB금융, 신한지주 | "금리 변화" |
| **건설** | HD현대건설, 삼성물산 | "건설 수주" |
| **소재** | 포스코, LG화학 | "원자재 가격" |
| **소비** | BGF리테일, 신세계 | "소비 회복" |

### 테마/정책 섹터 (3개)

| 섹터 | 대표 종목 | 뉴스 묶음 예시 |
|------|----------|----------------|
| **방산** | 한화에어로스페이스 | "방산 수출" |
| **에너지** | 한국전력, 신재생 | "원전/신재생" |
| **통신** | SK텔레콤, KT | "5G/6G" |

### 📌 **"뉴스 한 줄로 묶을 수 있는가?"**가 기준

---

## 4️⃣ 미국 시장 권장 섹터 세트 (11개)

### Core 11 Sectors (ETF 매핑)

| 섹터 | ETF | 대표 종목 |
|------|-----|----------|
| **Technology** | XLK | AAPL, MSFT, NVDA |
| **Energy** | XLE | XOM, CVX |
| **Financials** | XLF | JPM, BAC |
| **Healthcare** | XLV | JNJ, UNH |
| **Consumer Discretionary** | XLY | AMZN, TSLA |
| **Consumer Staples** | XLP | PG, KO |
| **Industrials** | XLI | BA, CAT |
| **Defense** | ITA | LMT, RTX |
| **Utilities** | XLU | NEE, DUK |
| **Communication** | XLC | GOOGL, META |
| **Materials** | XLB | LIN, APD |

### 📌 ETF 기준으로 매핑 가능 = 자금 흐름 추적 가능

---

## 5️⃣ 섹터 판단은 "선정"이 아니라 "상태 평가"

### 섹터마다 매일 계산하는 4가지

#### 1) 상대 강도 (Relative Strength)

```python
def calculate_relative_strength(sector, market_index, days=20):
    """
    섹터의 시장 대비 상대 강도
    
    Returns:
        rs: -100 ~ +100
        status: "OUTPERFORM", "INLINE", or "UNDERPERFORM"
    """
    
    sector_return = calculate_return(sector, days)
    market_return = calculate_return(market_index, days)
    
    rs = ((sector_return - market_return) / market_return) * 100
    
    if rs > 5:
        status = "OUTPERFORM"
    elif rs < -5:
        status = "UNDERPERFORM"
    else:
        status = "INLINE"
    
    return {
        "rs": rs,
        "status": status,
        "message": f"시장 대비 {rs:+.1f}%"
    }
```

**📌 랭킹 ❌ / 상태 ⭕**

---

#### 2) 자금 집중도

```python
def calculate_capital_concentration(sector):
    """
    섹터 내 자금 쏠림 정도
    
    Returns:
        concentration: 0~100 (낮을수록 분산)
        warning: 쏠림 경고
    """
    
    stocks = get_stocks_in_sector(sector)
    volumes = [s['volume'] for s in stocks]
    
    # 상위 3종목이 전체의 몇 %?
    top3_volume = sum(sorted(volumes, reverse=True)[:3])
    total_volume = sum(volumes)
    
    concentration = (top3_volume / total_volume) * 100
    
    if concentration > 70:
        warning = "HIGH"
        message = "⚠️ 특정 종목 쏠림 (섹터 확산 미흡)"
    elif concentration > 50:
        warning = "MODERATE"
        message = "⚠️ 일부 쏠림"
    else:
        warning = "LOW"
        message = "✅ 고른 분산"
    
    return {
        "concentration": concentration,
        "warning": warning,
        "message": message
    }
```

**📌 쏠림 심할수록 경고**

---

#### 3) 이슈 지속성

```python
def analyze_catalyst_persistence(sector, days=14):
    """
    섹터 이슈의 지속성 분석
    
    Returns:
        persistence: "PERSISTENT", "EMERGING", or "FADING"
        duration: 지속 일수
    """
    
    # 뉴스 추이
    news_trend = get_news_trend(sector, days)
    
    # 가격 추이
    price_trend = get_price_trend(sector, days)
    
    # 1. 뉴스가 먼저 → 가격 따라옴 (건강)
    if news_trend['start'] < price_trend['start']:
        news_first = True
    else:
        news_first = False
    
    # 2. 반복성
    price_peaks = count_price_peaks(sector, days)
    
    if news_first and price_peaks >= 2:
        persistence = "PERSISTENT"
        message = "✅ 지속 가능한 이슈"
    elif price_peaks == 1:
        persistence = "EMERGING"
        message = "⚠️ 이슈 초기 (관찰)"
    else:
        persistence = "FADING"
        message = "❌ 이슈 소멸 중"
    
    return {
        "persistence": persistence,
        "news_first": news_first,
        "duration": days,
        "message": message
    }
```

**📌 뉴스가 먼저? 가격이 먼저? 반복성은?**

---

#### 4) 시장 정합성

```python
def check_market_alignment(sector, market_regime):
    """
    섹터와 시장 정합성 체크
    
    Returns:
        aligned: True/False
        action: 추천 행동
    """
    
    sector_state = get_sector_state(sector)
    
    # 시장 Risk-On + 섹터 강세 = 정합
    if market_regime == "RISK_ON" and sector_state == "STRONG":
        aligned = True
        action = "TRADE"
        message = "✅ 시장-섹터 정합"
    
    # 시장 Risk-Off + 섹터 강세 = 주의
    elif market_regime == "RISK_OFF" and sector_state == "STRONG":
        aligned = False
        action = "CAUTION"
        message = "⚠️ 시장 역행 (단기 가능, 중기 위험)"
    
    # 시장 Risk-On + 섹터 약세 = 관찰
    elif market_regime == "RISK_ON" and sector_state == "WEAK":
        aligned = False
        action = "WATCH"
        message = "⚠️ 섹터 낙후 (회복 대기)"
    
    # 시장 Risk-Off + 섹터 약세 = 회피
    else:
        aligned = True  # 둘 다 약세는 정합
        action = "AVOID"
        message = "❌ 시장-섹터 모두 약세"
    
    return {
        "aligned": aligned,
        "action": action,
        "message": message
    }
```

**📌 시장 🔴 + 섹터 🟢 = 주의 / 시장 🟢 + 섹터 🔴 = 관찰**

---

## 6️⃣ 섹터 상태는 3단계만 사용

### 섹터 점수가 아닌 '상태' 중심

| 상태 | 의미 | 판단 난이도 |
|------|------|------------|
| 🟢 **구조적 (STRUCTURAL)** | 설명 가능한 자금 흐름 + 이슈 지속 | ⭐ 쉬움 (진입 가능) |
| 🟡 **관찰 (WATCH)** | 혼합 신호 (뉴스 O + 가격 X, 또는 반대) | ⭐⭐ 보통 (신중) |
| 🔴 **과열/소외 (HOT/COLD)** | 단기 급등 or 장기 침체 | ⭐⭐⭐ 어려움 (회피) |

### 구현

```python
def classify_sector_state(sector, metrics):
    """
    섹터 상태 분류
    
    Args:
        metrics: {
            "relative_strength": {...},
            "concentration": {...},
            "persistence": {...},
            "market_alignment": {...}
        }
    
    Returns:
        state: "STRUCTURAL", "WATCH", or "HOT_COLD"
        confidence: 신뢰도 (0~100)
    """
    
    rs = metrics['relative_strength']
    conc = metrics['concentration']
    pers = metrics['persistence']
    align = metrics['market_alignment']
    
    # 1. 구조적 (최고 등급)
    if (rs['status'] == "OUTPERFORM" and
        conc['warning'] == "LOW" and
        pers['persistence'] == "PERSISTENT" and
        align['aligned']):
        
        state = "STRUCTURAL"
        confidence = 90
        message = "✅ 설명 가능한 자금 흐름 + 이슈 지속"
    
    # 2. 과열 (단기 급등)
    elif (rs['rs'] > 20 and
          conc['warning'] == "HIGH"):
        
        state = "HOT_COLD"
        substate = "HOT"
        confidence = 70
        message = "🔥 단기 급등 (과열 주의)"
    
    # 3. 소외 (장기 침체)
    elif (rs['status'] == "UNDERPERFORM" and
          pers['persistence'] == "FADING"):
        
        state = "HOT_COLD"
        substate = "COLD"
        confidence = 70
        message = "❄️ 장기 침체 (회복 대기)"
    
    # 4. 관찰 (기본값)
    else:
        state = "WATCH"
        confidence = 50
        message = "⚠️ 혼합 신호 (관찰 필요)"
    
    return {
        "state": state,
        "confidence": confidence,
        "message": message,
        "metrics": metrics
    }
```

### 📌 "유망/비유망" ❌
### 📌 "지금은 판단하기 쉬운가?" ⭕

---

## 7️⃣ 섹터 → 종목 연결 원칙 (아주 중요)

### ❌ 하면 안 되는 연결

```
🔴 섹터 과열 + 🟢 종목 강세 → 추천

(이유: 섹터가 과열이면 종목도 위험)
```

### ⭕ Decision Stream v2.0 연결 규칙

| 섹터 상태 | 종목 노출 전략 |
|-----------|----------------|
| 🟢 **구조적** | 정상 노출 (Leader/Follower 구분) |
| 🟡 **관찰** | 조건부 노출 (Leader만 표시) |
| 🔴 **과열/소외** | 종목 강조 금지 (카드 흐리게 표시) |

### 구현

```python
def apply_sector_filter_to_stocks(sector_state, stocks):
    """
    섹터 상태에 따른 종목 필터링
    
    Args:
        sector_state: "STRUCTURAL", "WATCH", or "HOT_COLD"
        stocks: [{"ticker", "classification", "scores"}]
    
    Returns:
        filtered_stocks: 노출 전략 적용된 종목 리스트
    """
    
    filtered = []
    
    for stock in stocks:
        if sector_state == "STRUCTURAL":
            # 정상 노출
            stock['display'] = "NORMAL"
            stock['message'] = None
            filtered.append(stock)
        
        elif sector_state == "WATCH":
            # Leader만 표시
            if stock['classification'] == "LEADER":
                stock['display'] = "NORMAL"
                stock['message'] = "⚠️ 섹터 혼합 신호 - 신중 진입"
                filtered.append(stock)
            else:
                stock['display'] = "DIMMED"
                stock['message'] = "섹터 관찰 구간"
                filtered.append(stock)
        
        elif sector_state == "HOT_COLD":
            # 모든 종목 강조 금지
            stock['display'] = "DIMMED"
            stock['message'] = "❌ 섹터 과열/소외 - 진입 금지"
            filtered.append(stock)
    
    return filtered
```

### 📌 핵심: 🔴 섹터에서는 "종목이 아무리 좋아 보여도 카드 강조 ❌"

---

## 8️⃣ 테마성 섹터는 어떻게 처리하나?

### 원칙

- 상시 섹터 ❌
- 조건부 섹터 ⭕

### 테마성 섹터 예시

```
- AI
- 로봇
- 우주
- 양자
- 원전
```

### 처리 방식

```python
def manage_thematic_sectors(sectors):
    """
    테마성 섹터 조건부 활성화
    
    Args:
        sectors: 전체 섹터 리스트
    
    Returns:
        active_sectors: 활성화된 섹터만
    """
    
    active = []
    
    for sector in sectors:
        if sector['type'] != "THEMATIC":
            # 상시 섹터는 항상 활성화
            active.append(sector)
        else:
            # 테마성 섹터는 조건 확인
            heat = calculate_theme_heat(sector)
            
            # 활성화 조건:
            # 1. 뉴스 빈도 > 10건/주
            # 2. 거래대금 증가율 > 50%
            # 3. 지속 기간 < 30일 (과열 방지)
            
            if (heat['news_count'] > 10 and
                heat['volume_increase'] > 0.5 and
                heat['duration'] < 30):
                
                sector['status'] = "ACTIVE"
                sector['message'] = f"🔥 테마 활성화 ({heat['duration']}일)"
                active.append(sector)
            else:
                sector['status'] = "HIDDEN"
                # 리스트에 추가하지 않음 (자동 숨김)
    
    return active
```

### 📌 이게 과열 방지 장치입니다

---

## 9️⃣ 이 설계의 핵심 철학

> **"섹터는 '고르는 대상'이 아니라 종목 판단의 '배경 조건'이다"**

### 그래서:

```
✅ 섹터는 많을수록 ❌
✅ 섹터는 단순할수록 ⭕
✅ 섹터는 설명 가능해야 ⭕
```

### 실천 원칙

1. **섹터 개수**: 15~18개 (한국 14개 + 미국 11개 - 중복 제거)
2. **섹터 선정**: "뉴스 한 줄로 묶을 수 있는가?"
3. **섹터 상태**: 구조적/관찰/과열 3단계만
4. **섹터 → 종목**: 과열 섹터는 종목 강조 금지
5. **테마성 섹터**: 조건부 활성화 (과열 방지)

---

## 🔟 한 문장으로 정리

> **"Decision Stream에서 섹터란 돈이 아니라 '설명'을 묶은 단위다"**

---

## 📊 전체 섹터 관리 시스템

### 시스템 구조

```
1. 데이터 수집
   ↓
2. 섹터별 4가지 지표 계산
   - 상대 강도
   - 자금 집중도
   - 이슈 지속성
   - 시장 정합성
   ↓
3. 섹터 상태 분류
   - 🟢 구조적
   - 🟡 관찰
   - 🔴 과열/소외
   ↓
4. 종목 노출 전략 적용
   - 구조적: 정상 노출
   - 관찰: Leader만
   - 과열/소외: 강조 금지
   ↓
5. 테마성 섹터 조건부 활성화
   - 조건 충족 → 활성화
   - 조건 미달 → 자동 숨김
```

---

## 🎯 섹터 판단 체크리스트

### 설계 단계
- [x] 섹터 개수 정의 (15~18개)
- [x] 한국 시장 섹터 세트 (14개)
- [x] 미국 시장 섹터 세트 (11개)
- [x] 섹터 선정 기준 정의
- [x] 4가지 평가 지표 설계
- [x] 3단계 상태 분류
- [x] 섹터-종목 연결 규칙
- [x] 테마성 섹터 관리

### 구현 단계 (다음)
- [ ] 섹터별 데이터 수집 코드
- [ ] 4가지 지표 계산 함수
- [ ] 상태 분류 알고리즘
- [ ] 종목 필터링 로직
- [ ] 테마 활성화 시스템
- [ ] API 엔드포인트 (/sectors)
- [ ] 프론트엔드 UI

---

## 🚀 다음 단계

```bash
cd backend
mkdir -p sectors

# 섹터 관리 코드
touch sectors/sector_manager.py
touch sectors/relative_strength.py
touch sectors/concentration.py
touch sectors/persistence.py
touch sectors/alignment.py
touch sectors/thematic_manager.py
```

---

**이제 섹터 판단은 '관리 가능한 범위 + 설명 가능한 판단'으로 완성되었습니다! 🎉**
