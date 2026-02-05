# 🎯 모멘텀의 성격 분석: 진짜 vs 가짜

## 핵심 철학

> **"혼자 오르는 종목은 위험, 같이 오르는 종목은 돈 냄새"**

Decision Stream은 단순한 가격 상승이 아닌, **모멘텀의 질(Quality of Momentum)**을 판단합니다.

---

## 📊 모멘텀 분류

### ✅ 진짜 모멘텀 (Real Momentum)

#### 특징
1. **정책/제도 기반**
   - 정부 정책 확정
   - 법안 통과
   - 규제 변화
   - 예산 집행 시작

2. **실적 기반**
   - 대형 수주 (장기 계약)
   - 실적 가이던스 상향
   - 실제 매출/영업이익 증가
   - 신규 사업 본격화

3. **산업 단위 연쇄 상승**
   - 여러 종목이 동시에 움직임
   - 섹터 전체 상승
   - 가치사슬 전반으로 확산
   - 지속 기간 3일 이상

4. **구조적 변화**
   - 글로벌 공급망 재편
   - 에너지 전환
   - 인구 구조 변화
   - 전쟁/지정학 리스크

#### 신호
- ✅ 같은 섹터 3개 이상 동시 상승
- ✅ 기관/외국인 동시 순매수
- ✅ 거래대금 지속 증가 (3일 이상)
- ✅ 뉴스 키워드 빈도 증가 (정책/수주/실적)

---

### ❌ 가짜 모멘텀 (Fake Momentum)

#### 특징
1. **단일 기사 기반**
   - "~할 전망"
   - "~할 가능성"
   - "~를 검토 중"
   - 확정되지 않은 루머

2. **루머성 재료**
   - 커뮤니티 확산
   - 익명 제보
   - "내부자 정보"
   - 검증되지 않은 소식

3. **특정 유튜버/커뮤니티 확산**
   - 동시다발 언급
   - 급격한 관심 폭증
   - 과거 유사 패턴 반복
   - 실체 없는 기대감

4. **혼자 오르는 종목**
   - 섹터 내 다른 종목은 반응 없음
   - 기관/외국인은 매도
   - 거래량만 폭발 (1~2일)
   - 다음 날 급락

#### 신호
- ❌ 혼자만 급등 (섹터 다른 종목 무반응)
- ❌ 개인만 순매수, 기관/외국인 매도
- ❌ 거래량 1~2일 폭발 후 감소
- ❌ 뉴스 키워드 "전망", "가능성", "검토"

---

## 🎯 모멘텀 품질 점수 (Momentum Quality Score)

### 계산 로직

```python
def calculate_momentum_quality(stock, sector):
    """
    모멘텀의 진짜/가짜 판단
    
    Returns:
        quality: "REAL", "FAKE", or "UNCERTAIN"
        score: 0~100
        signals: 세부 신호
    """
    
    # ========== 진짜 모멘텀 체크 (Real Signals) ==========
    
    # 1. 산업 동반 상승 (가장 중요) ⭐
    sector_breadth = check_sector_breadth(sector)
    # - 섹터 내 3개 이상 동시 상승: +30점
    # - 섹터 내 2개: +15점
    # - 혼자만 상승: 0점
    
    # 2. 기관/외국인 동참
    institution_support = check_institution_flow(stock)
    # - 기관 + 외국인 동시 순매수: +25점
    # - 기관 또는 외국인 순매수: +15점
    # - 둘 다 매도: -20점 (가짜 신호)
    
    # 3. 거래대금 지속성
    volume_persistence = check_volume_duration(stock)
    # - 3일 이상 지속: +20점
    # - 2일: +10점
    # - 1일만 폭발: -15점 (가짜 신호)
    
    # 4. 뉴스 성격 (정책/수주/실적)
    news_quality = analyze_news_type(stock)
    # - 정책 확정/수주/실적: +25점
    # - 전망/검토: +5점
    # - 루머: -20점 (가짜 신호)
    
    # ========== 가짜 모멘텀 체크 (Fake Signals) ==========
    
    # 5. 커뮤니티 과열
    community_heat = check_community_sentiment(stock)
    # - 급격한 언급 증가: -15점
    # - 유튜버 동시 언급: -10점
    # - 정상 범위: 0점
    
    # 6. 과거 패턴
    historical_pattern = check_pump_dump_history(stock)
    # - 과거 급등급락 이력: -20점
    # - 정상 패턴: 0점
    
    # ========== 종합 점수 ==========
    
    total_score = (
        sector_breadth +
        institution_support +
        volume_persistence +
        news_quality -
        community_heat -
        abs(historical_pattern)
    )
    
    # 0~100 범위로 정규화
    normalized_score = max(0, min(100, total_score))
    
    # 판정
    if normalized_score >= 70:
        quality = "REAL"
        action = "BUY"
    elif normalized_score >= 40:
        quality = "UNCERTAIN"
        action = "WATCH"
    else:
        quality = "FAKE"
        action = "AVOID"
    
    return {
        "quality": quality,
        "score": normalized_score,
        "action": action,
        "signals": {
            "sector_breadth": sector_breadth,
            "institution_support": institution_support,
            "volume_persistence": volume_persistence,
            "news_quality": news_quality,
            "community_heat": community_heat,
            "historical_pattern": historical_pattern
        }
    }
```

---

## 📊 섹터 동반 상승 체크 (가장 중요)

### 로직

```python
def check_sector_breadth(sector):
    """
    "같이 오르는가?" 체크
    
    Returns:
        score: 0~30 (가장 높은 가중치)
        count: 동반 상승 종목 수
        pattern: "SECTOR_WIDE", "PARTIAL", or "ISOLATED"
    """
    
    # 섹터 내 전체 종목 수집
    sector_stocks = get_sector_stocks(sector)
    
    # 최근 3일 상승 종목 수
    rising_stocks = []
    for stock in sector_stocks:
        price_change = get_price_change(stock, days=3)
        volume_increase = get_volume_change(stock, days=3)
        
        if price_change > 3 and volume_increase > 1.2:  # 3% 이상, 거래량 20% 증가
            rising_stocks.append(stock)
    
    rising_count = len(rising_stocks)
    total_count = len(sector_stocks)
    
    # 비율 계산
    rising_ratio = rising_count / total_count if total_count > 0 else 0
    
    # 점수 부여
    if rising_count >= 3 and rising_ratio >= 0.5:
        score = 30  # 섹터 전반 상승
        pattern = "SECTOR_WIDE"
        message = f"✅ {sector} 섹터 전체 상승 ({rising_count}개 종목)"
    elif rising_count >= 2:
        score = 15  # 부분 상승
        pattern = "PARTIAL"
        message = f"⚠️ {sector} 일부 상승 ({rising_count}개 종목)"
    else:
        score = 0   # 혼자 상승
        pattern = "ISOLATED"
        message = f"❌ 혼자 오르는 종목 (위험)"
    
    return {
        "score": score,
        "count": rising_count,
        "total": total_count,
        "ratio": rising_ratio,
        "pattern": pattern,
        "message": message,
        "stocks": [s['ticker'] for s in rising_stocks]
    }
```

---

## 🎬 실전 예시

### Case 1: 진짜 모멘텀 - 방산 섹터 (2026-01-26)

```python
# 방산 섹터 분석
momentum = calculate_momentum_quality(
    stock="LMT",
    sector="방산"
)

# 결과:
{
    "quality": "REAL",
    "score": 85,
    "action": "BUY",
    "signals": {
        "sector_breadth": 30,        # ✅ 3개 이상 동시 상승
        "institution_support": 25,   # ✅ 기관+외국인 순매수
        "volume_persistence": 20,    # ✅ 3일 이상 지속
        "news_quality": 25,          # ✅ 정책 확정 (국방비 증액)
        "community_heat": -10,       # ⚠️ 약간 과열
        "historical_pattern": -5     # ⚠️ 정상 범위
    },
    "explanation": """
    ✅ 진짜 모멘텀 (85점)
    
    1. 섹터 동반 상승:
       - LMT (Lockheed Martin) +5.2%
       - 한화에어로스페이스 (012450) +4.8%
       - LIG넥스원 (079550) +3.9%
       → 3개 종목 동시 상승 ✅
    
    2. 기관/외국인 동참:
       - 기관 순매수: +$120M
       - 외국인 순매수: +$85M
       → 큰손들이 함께 매수 ✅
    
    3. 거래대금 지속:
       - 1일차: +120%
       - 2일차: +95%
       - 3일차: +80%
       → 3일 연속 증가 ✅
    
    4. 뉴스 성격:
       - "미국 국방비 5% 증액 확정"
       - "NATO 회원국 방산 수주 증가"
       → 정책 확정 + 실제 수주 ✅
    
    결론: 같이 오르고, 큰손이 사고, 지속되고, 근거가 확실함
          → 진짜 모멘텀! 매수 가능
    """
}
```

### Case 2: 가짜 모멘텀 - 특정 테마주

```python
# 가짜 모멘텀 예시
momentum = calculate_momentum_quality(
    stock="XYZ_STOCK",
    sector="AI"
)

# 결과:
{
    "quality": "FAKE",
    "score": 25,
    "action": "AVOID",
    "signals": {
        "sector_breadth": 0,         # ❌ 혼자만 상승
        "institution_support": -20,  # ❌ 기관+외국인 매도
        "volume_persistence": -15,   # ❌ 1일만 폭발
        "news_quality": 5,           # ❌ "~할 전망" 기사
        "community_heat": -15,       # ❌ 커뮤니티 과열
        "historical_pattern": -20    # ❌ 과거 급등급락 이력
    },
    "explanation": """
    ❌ 가짜 모멘텀 (25점)
    
    1. 혼자 오름:
       - XYZ_STOCK +18.5%
       - 같은 AI 섹터 다른 종목: 0~1%
       → 혼자만 급등 ❌
    
    2. 기관/외국인 이탈:
       - 기관 순매도: -$30M
       - 외국인 순매도: -$15M
       - 개인만 순매수: +$45M
       → 큰손들은 팔고 있음 ❌
    
    3. 거래량 1일 폭발:
       - 1일차: +450% (폭발)
       - 2일차: -60% (급감)
       → 지속성 없음 ❌
    
    4. 뉴스 성격:
       - "XYZ사, AI 사업 진출 검토 중"
       - "관계자 '가능성 타진' 언급"
       → 확정 아님, 루머성 ❌
    
    5. 커뮤니티 과열:
       - 특정 유튜버 동시 언급 3건
       - 커뮤니티 게시글 +300%
       → 인위적 확산 의심 ❌
    
    6. 과거 패턴:
       - 6개월 전 유사 패턴 (+15% → -22%)
       - 3개월 전 유사 패턴 (+20% → -18%)
       → 반복되는 급등급락 ❌
    
    결론: 혼자 오르고, 큰손은 팔고, 1일만 폭발, 루머성 뉴스
          → 가짜 모멘텀! 절대 회피
    """
}
```

---

## 🎯 통합: 9요소 + 모멘텀 품질

### 최종 판단 로직

```python
def final_classification_with_momentum_quality(stock, sector):
    """
    9요소 + 모멘텀 품질 통합 판단
    """
    
    # 1. 기존 9요소 체크
    nine_factors = classify_stock_9_factors(stock, sector)
    
    # 2. 모멘텀 품질 체크 (추가)
    momentum_quality = calculate_momentum_quality(stock, sector)
    
    # 3. 통합 판단
    if nine_factors['classification'] == "NO_GO":
        return nine_factors  # 필수 요소 미달 시 즉시 탈락
    
    # 모멘텀 품질로 최종 판단
    if momentum_quality['quality'] == "FAKE":
        return {
            "classification": "NO_GO",
            "action": "AVOID",
            "reason": "가짜 모멘텀 감지",
            "details": momentum_quality
        }
    
    if momentum_quality['quality'] == "REAL":
        if nine_factors['classification'] == "FOLLOWER":
            # 진짜 모멘텀 + Follower = 즉시 매수로 승격
            return {
                "classification": "LEADER",
                "action": "BUY_NOW",
                "reason": "진짜 모멘텀 + 9요소 충족",
                "confidence": "HIGH"
            }
        else:
            return nine_factors  # LEADER 유지
    
    # UNCERTAIN: 기존 판단 유지
    return nine_factors
```

---

## 📚 핵심 메시지

### 1. 섹터 동반 상승이 최우선 ⭐
```
혼자 오르는 종목 = 위험
같이 오르는 종목 = 돈 냄새
```

### 2. 큰손의 행동을 따라가라
```
개인만 매수 = 가짜
기관+외국인 매수 = 진짜
```

### 3. 지속성이 증명한다
```
1일 폭발 = 가짜
3일 이상 = 진짜
```

### 4. 뉴스의 성격을 구분하라
```
"검토", "전망", "가능성" = 가짜
"확정", "수주", "실적" = 진짜
```

### 5. 커뮤니티 과열은 경고 신호
```
급격한 확산 = 인위적
자연스러운 확산 = 실체
```

---

## 🎉 결론

Decision Stream은 이제 **모멘텀의 질**을 판단합니다:
- ✅ 진짜 모멘텀: 같이 오르고, 큰손이 사고, 지속되고, 근거가 확실
- ❌ 가짜 모멘텀: 혼자 오르고, 개인만 사고, 1일 폭발, 루머성 뉴스

**"혼자 오르는 종목은 위험, 같이 오르는 종목은 돈 냄새"**
