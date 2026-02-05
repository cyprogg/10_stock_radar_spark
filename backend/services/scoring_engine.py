"""
Decision Stream Scoring Engine
0~100 점수 시스템 + 설명 가능성

핵심 원칙:
1. 모든 점수는 0~100으로 통일
2. 근거 + 반대 근거 자동 생성
3. 사람이 이해할 수 있는 언어
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class ScoreResult:
    """점수 결과 (근거 포함)"""
    score: float  # 0~100
    reasons: List[str]  # 긍정 근거
    warnings: List[str]  # 반대 근거
    confidence: float  # 신뢰도 0~1
    sources: List[str]  # 데이터 출처


class ScoringEngine:
    """
    투자 의사결정을 위한 점수 엔진
    """
    
    def __init__(self):
        self.min_score = 0
        self.max_score = 100
    
    # ========== 1) 자금 유입 점수 (Flow Score) ==========
    
    def calculate_flow_score(self, stock_data: Dict) -> ScoreResult:
        """
        자금 흐름 = 거래대금 증가 + 기관/외국인 순매수
        
        Args:
            stock_data: {
                "volume_5d": 최근 5일 평균 거래대금,
                "volume_avg_20d": 20일 평균 거래대금,
                "inst_net_buying_5d": 기관 5일 순매수,
                "foreign_net_buying_5d": 외국인 5일 순매수,
                "retail_ratio": 개인 매수 비중 (%)
            }
        
        Returns:
            ScoreResult (0~100)
        """
        score = 0
        reasons = []
        warnings = []
        
        # 1) 거래대금 증가 (40점)
        volume_ratio = stock_data.get("volume_5d", 1) / max(stock_data.get("volume_avg_20d", 1), 1)
        
        if volume_ratio >= 3:
            score += 40
            reasons.append(f"거래대금 5일 평균 {volume_ratio:.1f}배 급증")
        elif volume_ratio >= 2:
            score += 30
            reasons.append(f"거래대금 증가 ({volume_ratio:.1f}배)")
        elif volume_ratio >= 1.5:
            score += 20
            reasons.append(f"거래대금 소폭 증가 ({volume_ratio:.1f}배)")
        else:
            warnings.append(f"거래대금 증가 미미 ({volume_ratio:.1f}배)")
        
        # 2) 기관 순매수 (30점)
        inst_net = stock_data.get("inst_net_buying_5d", 0)
        if inst_net > 0:
            inst_ratio = inst_net / max(stock_data.get("volume_avg_20d", 1), 1)
            if inst_ratio > 0.1:  # 평균 거래량의 10%
                score += 30
                reasons.append(f"기관 5일 대량 순매수 ({inst_ratio*100:.1f}%)")
            else:
                score += 20
                reasons.append("기관 순매수 전환")
        else:
            warnings.append("기관 순매도 중")
        
        # 3) 외국인 순매수 (30점)
        foreign_net = stock_data.get("foreign_net_buying_5d", 0)
        if foreign_net > 0:
            score += 30
            reasons.append("외국인 순매수 동참")
        else:
            warnings.append("외국인 순매도 중")
        
        # 4) 반대 근거: 개인 주도 과열
        retail_ratio = stock_data.get("retail_ratio", 0)
        if retail_ratio > 70:
            warnings.append(f"개인 매수 비중 {retail_ratio:.0f}% (기관 이탈 시 급락 위험)")
        
        # 5) 신뢰도 계산
        confidence = 0.9 if inst_net > 0 and foreign_net > 0 else 0.7
        
        return ScoreResult(
            score=min(score, 100),
            reasons=reasons,
            warnings=warnings,
            confidence=confidence,
            sources=["KRX 투자자별 매매동향", "거래소 시세"]
        )
    
    # ========== 2) 가격 구조 점수 (Structure Score) ==========
    
    def calculate_structure_score(self, stock_data: Dict) -> ScoreResult:
        """
        가격 구조 = 추세 + 고저점 + 조정 패턴
        
        Args:
            stock_data: {
                "price": 현재가,
                "ma20": 20일 이동평균,
                "ma60": 60일 이동평균,
                "recent_high": 최근 20일 고점,
                "recent_low": 최근 20일 저점,
                "pullback_volume_ratio": 조정 시 거래량 비율
            }
        """
        score = 0
        reasons = []
        warnings = []
        
        price = stock_data.get("price", 0)
        ma20 = stock_data.get("ma20", 0)
        ma60 = stock_data.get("ma60", 0)
        recent_high = stock_data.get("recent_high", 0)
        
        # 1) 이동평균 위치 (40점)
        if price > ma20 and price > ma60:
            score += 40
            reasons.append("20일선, 60일선 위 (상승 추세)")
        elif price > ma20:
            score += 20
            reasons.append("20일선 위 (단기 상승)")
        else:
            warnings.append("20일선 아래 (약세)")
        
        # 2) 고점 근처 (30점)
        if recent_high > 0:
            high_proximity = price / recent_high
            if high_proximity >= 0.95:
                score += 30
                reasons.append("최근 20일 고점 근처 (강세)")
            elif high_proximity >= 0.90:
                score += 20
                reasons.append("고점 대비 소폭 조정")
            else:
                warnings.append(f"고점 대비 {(1-high_proximity)*100:.1f}% 하락")
        
        # 3) 조정 시 거래량 (30점)
        pullback_volume = stock_data.get("pullback_volume_ratio", 1)
        if pullback_volume < 0.7:  # 조정 시 거래량 감소
            score += 30
            reasons.append("조정 시 거래량 감소 (건전한 조정)")
        elif pullback_volume > 1.3:
            warnings.append("조정 시 거래량 증가 (약세 신호)")
        
        confidence = 0.85
        
        return ScoreResult(
            score=min(score, 100),
            reasons=reasons,
            warnings=warnings,
            confidence=confidence,
            sources=["차트 분석", "이동평균 계산"]
        )
    
    # ========== 3) 서사 점수 (Narrative Score) ==========
    
    def calculate_narrative_score(self, stock_data: Dict) -> ScoreResult:
        """
        서사 = 뉴스 빈도 + 정책 연관 + 실적 이벤트
        
        Args:
            stock_data: {
                "news_count_7d": 최근 7일 뉴스 건수,
                "news_text": 뉴스 텍스트,
                "has_guidance": 실적 가이던스 여부,
                "has_disclosure": 공시 여부,
                "sector_news_count": 섹터 전체 뉴스 건수
            }
        """
        score = 0
        reasons = []
        warnings = []
        
        news_count = stock_data.get("news_count_7d", 0)
        news_text = stock_data.get("news_text", "")
        
        # 1) 뉴스 빈도 (40점)
        if news_count >= 10:
            score += 40
            reasons.append(f"최근 7일 뉴스 {news_count}건 (고빈도)")
        elif news_count >= 5:
            score += 20
            reasons.append(f"뉴스 {news_count}건")
        elif news_count == 1:
            warnings.append("단일 기사 의존 (가짜 모멘텀 가능성)")
        else:
            warnings.append("뉴스 부족 (관심 저조)")
        
        # 2) 정책/제도 키워드 (30점)
        policy_keywords = ["수주", "정책", "규제", "지원", "승인", "계약"]
        policy_match = sum(1 for kw in policy_keywords if kw in news_text)
        
        if policy_match >= 2:
            score += 30
            reasons.append("정책/제도 관련 복수 재료")
        elif policy_match == 1:
            score += 15
            reasons.append("정책 관련 재료")
        
        # 3) 실적 이벤트 (30점)
        has_guidance = stock_data.get("has_guidance", False)
        has_disclosure = stock_data.get("has_disclosure", False)
        
        if has_guidance:
            score += 30
            reasons.append("실적 가이던스 제시")
        elif has_disclosure:
            score += 20
            reasons.append("주요 공시 발표")
        else:
            warnings.append("실적/공시 이벤트 없음")
        
        # 4) 반대 근거: 섹터 대비 뉴스 부족
        sector_news = stock_data.get("sector_news_count", 0)
        if sector_news > 0 and news_count / sector_news < 0.1:
            warnings.append("섹터 대비 뉴스 비중 낮음 (주목도 낮음)")
        
        confidence = 0.8 if has_guidance or has_disclosure else 0.6
        
        return ScoreResult(
            score=min(score, 100),
            reasons=reasons,
            warnings=warnings,
            confidence=confidence,
            sources=["뉴스 분석", "OpenDART 공시"]
        )
    
    # ========== 4) 리스크 점수 (Risk Score) ==========
    
    def calculate_risk_score(self, stock_data: Dict) -> ScoreResult:
        """
        리스크 = 과열 + 테마 말기 + 유동성
        ⚠️ 점수가 낮을수록 좋음 (역산)
        
        Args:
            stock_data: {
                "rsi": RSI 지표,
                "last_candle": 마지막 봉 형태,
                "sector_rank": 섹터 내 급등 순위,
                "avg_volume_daily": 일평균 거래대금,
                "gap_percent": 갭 비율
            }
        """
        score = 0
        warnings = []
        reasons = []
        
        # 1) 과열 (40점)
        rsi = stock_data.get("rsi", 50)
        if rsi > 75:
            score += 30
            warnings.append(f"RSI {rsi:.0f} (극심한 과열)")
        elif rsi > 70:
            score += 20
            warnings.append(f"RSI {rsi:.0f} (과열 구간)")
        else:
            reasons.append(f"RSI {rsi:.0f} (정상 범위)")
        
        last_candle = stock_data.get("last_candle", "")
        if last_candle == "DISTRIBUTION":
            score += 10
            warnings.append("장대 음봉 (분배 신호)")
        
        # 2) 테마 말기 (30점)
        sector_rank = stock_data.get("sector_rank", 1)
        if sector_rank >= 5:
            score += 30
            warnings.append(f"테마 내 {sector_rank}번째 급등주 (후발주, 위험)")
        elif sector_rank >= 3:
            score += 15
            warnings.append(f"테마 내 {sector_rank}번째 (중반주)")
        else:
            reasons.append(f"테마 선도주 (상위 {sector_rank}위)")
        
        # 3) 유동성 (30점)
        avg_volume = stock_data.get("avg_volume_daily", 0)
        if avg_volume < 1_000_000_000:  # 10억 미만
            score += 30
            warnings.append(f"일평균 거래대금 {avg_volume/1e8:.0f}억 (유동성 부족)")
        elif avg_volume < 5_000_000_000:  # 50억 미만
            score += 15
            warnings.append(f"거래대금 {avg_volume/1e8:.0f}억 (유동성 낮음)")
        else:
            reasons.append(f"거래대금 충분 ({avg_volume/1e8:.0f}억)")
        
        # 4) 갭 리스크
        gap = stock_data.get("gap_percent", 0)
        if abs(gap) > 10:
            score += 10
            warnings.append(f"갭 {gap:+.1f}% (변동성 높음)")
        
        confidence = 0.85
        
        return ScoreResult(
            score=min(score, 100),
            reasons=reasons,
            warnings=warnings,
            confidence=confidence,
            sources=["기술적 분석", "거래량 분석"]
        )
    
    # ========== 5) 모멘텀 품질 점수 ==========
    
    def check_momentum_quality(self, stock_data: Dict, sector_data: Dict) -> Tuple[str, List[str]]:
        """
        진짜 vs 가짜 모멘텀 판별
        
        Returns:
            ("REAL" or "FAKE", reasons)
        """
        fake_signals = []
        real_signals = []
        
        # 1) 단일 기사 체크
        news_count = stock_data.get("news_count_7d", 0)
        if news_count == 1:
            fake_signals.append("단일 기사 의존 (루머 가능성)")
        
        # 2) 혼자 급등 체크
        sector_top_movers = sector_data.get("top_movers", [])
        if len(sector_top_movers) < 3:
            fake_signals.append("혼자 급등 (섹터 동반 상승 없음)")
        else:
            real_signals.append(f"섹터 내 {len(sector_top_movers)}개 종목 동반 상승")
        
        # 3) 정책/제도 재료 체크
        news_text = stock_data.get("news_text", "")
        policy_keywords = ["수주", "정책", "계약", "승인"]
        if any(kw in news_text for kw in policy_keywords):
            real_signals.append("정책/제도 관련 재료 (진짜 모멘텀)")
        
        # 4) 기관 동참 체크
        inst_net = stock_data.get("inst_net_buying_5d", 0)
        if inst_net > 0:
            real_signals.append("기관 순매수 동참")
        else:
            fake_signals.append("기관 미동참 (개인 주도)")
        
        # 판정
        if len(fake_signals) >= 2:
            return "FAKE", fake_signals
        else:
            return "REAL", real_signals
    
    # ========== 종합 판단 ==========
    
    def calculate_comprehensive_score(self, stock_data: Dict, sector_data: Dict) -> Dict:
        """
        9요소 종합 점수 계산
        """
        # 1) 4대 핵심 점수
        flow = self.calculate_flow_score(stock_data)
        structure = self.calculate_structure_score(stock_data)
        narrative = self.calculate_narrative_score(stock_data)
        risk = self.calculate_risk_score(stock_data)
        
        # 2) 모멘텀 품질
        momentum_quality, momentum_reasons = self.check_momentum_quality(stock_data, sector_data)
        
        # 3) 종합 점수 (가중 평균)
        total_score = (
            flow.score * 0.4 +        # 자금 흐름 40%
            structure.score * 0.2 +   # 가격 구조 20%
            narrative.score * 0.2 +   # 서사 20%
            (100 - risk.score) * 0.2  # 리스크 20% (역산)
        )
        
        return {
            "total_score": round(total_score, 1),
            "flow": {
                "score": flow.score,
                "reasons": flow.reasons,
                "warnings": flow.warnings,
                "confidence": flow.confidence,
                "sources": flow.sources
            },
            "structure": {
                "score": structure.score,
                "reasons": structure.reasons,
                "warnings": structure.warnings,
                "confidence": structure.confidence,
                "sources": structure.sources
            },
            "narrative": {
                "score": narrative.score,
                "reasons": narrative.reasons,
                "warnings": narrative.warnings,
                "confidence": narrative.confidence,
                "sources": narrative.sources
            },
            "risk": {
                "score": risk.score,
                "reasons": risk.reasons,
                "warnings": risk.warnings,
                "confidence": risk.confidence,
                "sources": risk.sources
            },
            "momentum_quality": momentum_quality,
            "momentum_reasons": momentum_reasons
        }


# ========== No-Go 판정 로직 ==========

class NoGoDetector:
    """
    No-Go 판정 규칙 (12개 중 핵심 6개)
    하나라도 해당 시 No-Go 자동 분류
    """
    
    @staticmethod
    def check_nogo_rules(stock_data: Dict, sector_data: Dict) -> Tuple[bool, Optional[str]]:
        """
        No-Go 규칙 체크
        
        Returns:
            (is_nogo: bool, reason: str)
        """
        
        # 규칙 1: 단일 기사 급등 + 거래대금 폭증
        news_count = stock_data.get("news_count_7d", 0)
        volume_ratio = stock_data.get("volume_5d", 1) / max(stock_data.get("volume_avg_20d", 1), 1)
        
        if news_count == 1 and volume_ratio >= 5:
            return True, "단일 기사 급등 + 거래대금 폭증 (루머 가능성)"
        
        # 규칙 2: 갭 상승 후 장대 음봉
        gap = stock_data.get("gap_percent", 0)
        last_candle = stock_data.get("last_candle", "")
        
        if gap > 5 and last_candle == "DISTRIBUTION":
            return True, "갭 상승 후 장대 음봉 (분배 신호)"
        
        # 규칙 3: 테마 내 5번째 이후 급등주
        sector_rank = stock_data.get("sector_rank", 1)
        
        if sector_rank >= 5:
            return True, f"테마 내 {sector_rank}번째 급등주 (후발주, 고위험)"
        
        # 규칙 4: 개인 80%↑ + 기관 이탈
        retail_ratio = stock_data.get("retail_ratio", 0)
        inst_net = stock_data.get("inst_net_buying_5d", 0)
        
        if retail_ratio > 80 and inst_net < 0:
            return True, f"개인 주도 {retail_ratio:.0f}% + 기관 이탈 (지속성 낮음)"
        
        # 규칙 5: 핵심 이평 동시 이탈
        price = stock_data.get("price", 0)
        ma20 = stock_data.get("ma20", 0)
        ma60 = stock_data.get("ma60", 0)
        
        if price < ma20 and price < ma60:
            return True, "20일선, 60일선 동시 이탈 (약세 전환)"
        
        # 규칙 6: 손절선 설정 불가 (변동성 과다)
        atr_ratio = stock_data.get("atr_ratio", 0)
        support_level = stock_data.get("support_level", None)
        
        if support_level is None or atr_ratio > 0.15:
            return True, "손절선 설정 불가 (변동성 과다 또는 지지선 부재)"
        
        return False, None


# ========== 테스트 ==========

if __name__ == "__main__":
    # 샘플 데이터
    sample_stock = {
        "price": 185000,
        "ma20": 180000,
        "ma60": 175000,
        "volume_5d": 120_000_000_000,
        "volume_avg_20d": 30_000_000_000,
        "inst_net_buying_5d": 15_000_000_000,
        "foreign_net_buying_5d": 5_000_000_000,
        "retail_ratio": 55,
        "news_count_7d": 8,
        "news_text": "방위 사업청 수주 계약 체결",
        "has_guidance": True,
        "rsi": 68,
        "sector_rank": 2,
        "avg_volume_daily": 80_000_000_000,
        "gap_percent": 2.5,
        "recent_high": 190000,
        "pullback_volume_ratio": 0.6,
        "support_level": 175000,
        "atr_ratio": 0.08
    }
    
    sample_sector = {
        "top_movers": ["LMT", "한화에어로스페이스", "한국항공우주"]
    }
    
    # 점수 엔진 테스트
    engine = ScoringEngine()
    result = engine.calculate_comprehensive_score(sample_stock, sample_sector)
    
    print("=" * 60)
    print("Decision Stream Scoring Engine Test")
    print("=" * 60)
    print(f"\n총점: {result['total_score']}/100")
    print(f"\n자금 흐름: {result['flow']['score']}/100")
    print("  근거:", ", ".join(result['flow']['reasons']))
    print("  경고:", ", ".join(result['flow']['warnings']) if result['flow']['warnings'] else "없음")
    
    print(f"\n가격 구조: {result['structure']['score']}/100")
    print("  근거:", ", ".join(result['structure']['reasons']))
    
    print(f"\n서사: {result['narrative']['score']}/100")
    print("  근거:", ", ".join(result['narrative']['reasons']))
    
    print(f"\n리스크: {result['risk']['score']}/100 (낮을수록 좋음)")
    print("  경고:", ", ".join(result['risk']['warnings']) if result['risk']['warnings'] else "없음")
    
    print(f"\n모멘텀 품질: {result['momentum_quality']}")
    print("  이유:", ", ".join(result['momentum_reasons']))
    
    # No-Go 판정 테스트
    is_nogo, nogo_reason = NoGoDetector.check_nogo_rules(sample_stock, sample_sector)
    print(f"\nNo-Go 판정: {is_nogo}")
    if is_nogo:
        print(f"  사유: {nogo_reason}")
