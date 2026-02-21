"""
Agent 1: Market Regime Analyst 🌍
역할: "오늘 장이 어떤 장인지" 규칙 + 요약
"""

from typing import Dict, List, Any
from datetime import datetime


class MarketRegimeAnalyst:
    """시장 상태 분석 에이전트"""
    
    def __init__(self):
        self.name = "Market Regime Analyst"
        
    def analyze(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        시장 상태 분석
        
        Args:
            market_data: 시장 데이터 딕셔너리
                - us_10y: 미국 10년물 국채 수익률
                - us_10y_change_20d: 최근 20일 변화율
                - usd_krw: 원달러 환율
                - usd_krw_change_20d: 환율 20일 변화율
                - kospi: 코스피 지수
                - kospi_vs_ma20: 20일 이평 대비
                - kospi_vs_ma60: 60일 이평 대비
                - kospi_from_high: 고점 대비 낙폭 (%)
                - sp500: S&P 500 지수
                - sp500_vs_ma20: 20일 이평 대비
                - sp500_vs_ma60: 60일 이평 대비
                - vix: VIX 지수
                - vkospi: VKOSPI 지수
                - kospi_advancers: 상승 종목 수
                - kospi_decliners: 하락 종목 수
                - breadth_ratio: 상승/하락 비율
                
        Returns:
            분석 결과 딕셔너리
        """
        score = 0
        signals_positive = []
        signals_negative = []
        
        # 1) VIX 체크
        vix = market_data.get('vix', 20)
        if vix < 15:
            score += 1
            signals_positive.append(f"VIX {vix:.1f} 이하 (안정)")
        elif vix > 25:
            score -= 1
            signals_negative.append(f"VIX {vix:.1f} 초과 (공포)")
        
        # 2) 이동평균 체크
        kospi_vs_ma20 = market_data.get('kospi_vs_ma20', 1.0)
        kospi_vs_ma60 = market_data.get('kospi_vs_ma60', 1.0)
        if kospi_vs_ma20 > 1 and kospi_vs_ma60 > 1:
            score += 1
            signals_positive.append("코스피 20일선/60일선 위")
        elif kospi_vs_ma20 < 1 or kospi_vs_ma60 < 1:
            signals_negative.append("코스피 주요 이평선 이탈")
        
        # 3) 시장 폭 체크
        breadth_ratio = market_data.get('breadth_ratio', 1.0)
        if breadth_ratio > 1.2:
            score += 1
            signals_positive.append(f"상승/하락 비율 {breadth_ratio:.1f}:1")
        elif breadth_ratio < 0.8:
            score -= 1
            signals_negative.append(f"상승/하락 비율 {breadth_ratio:.1f}:1 (약세)")
        
        # 4) 낙폭 체크
        kospi_from_high = market_data.get('kospi_from_high', 0)
        if kospi_from_high < -10:
            signals_negative.append(f"고점 대비 {kospi_from_high:.1f}% (과매도)")
        elif kospi_from_high > -3:
            signals_positive.append(f"고점 대비 {kospi_from_high:.1f}% (고점 근처)")
        
        # 5) 미국 시장 체크
        sp500_vs_ma20 = market_data.get('sp500_vs_ma20', 1.0)
        sp500_vs_ma60 = market_data.get('sp500_vs_ma60', 1.0)
        if sp500_vs_ma20 > 1 and sp500_vs_ma60 > 1:
            score += 0.5
            signals_positive.append("S&P500 주요 이평선 위")
        
        # 최종 판정
        state = "RISK_ON" if score >= 2 else "RISK_OFF"
        final_score = max(0, min(3, int(score)))
        
        # Playbook 생성
        playbook = self._generate_playbook(state, final_score, signals_positive, signals_negative)
        
        # 신뢰도 계산
        confidence = self._calculate_confidence(signals_positive, signals_negative)
        
        return {
            "state": state,
            "score": final_score,
            "max_score": 3,
            "confidence": confidence,
            "playbook": playbook,
            "signals": {
                "positive": signals_positive,
                "negative": signals_negative
            },
            "lasting_themes": [],  # 외부 데이터 필요
            "sources": [
                {
                    "type": "api",
                    "name": "Market Data API",
                    "timestamp": datetime.now().isoformat()
                }
            ]
        }
    
    def _generate_playbook(self, state: str, score: int, 
                          positive: List[str], negative: List[str]) -> str:
        """상황에 맞는 플레이북 생성"""
        if state == "RISK_ON":
            if score == 3:
                return "적극 매수 국면. 브레이크아웃 진입 적극 고려."
            elif score == 2:
                return "눌림 매수 대기. 20일선 지지 확인 후 진입."
            else:
                return "신중 매수. 리더 종목 위주 선택적 진입."
        else:
            if len(negative) >= 3:
                return "방어 모드. 현금 비중 확대 및 손절 엄격 준수."
            else:
                return "관망 국면. 시장 회복 신호 확인 후 재진입."
    
    def _calculate_confidence(self, positive: List[str], negative: List[str]) -> float:
        """신뢰도 계산 (0.0~1.0)"""
        total_signals = len(positive) + len(negative)
        if total_signals == 0:
            return 0.5
        
        # 긍정 신호가 많을수록 신뢰도 상승
        confidence = 0.5 + (len(positive) - len(negative)) * 0.1
        return max(0.0, min(1.0, confidence))
    
    def get_risk_state(self, market_data: Dict[str, Any]) -> str:
        """간단한 RISK_ON/RISK_OFF 상태만 반환"""
        result = self.analyze(market_data)
        return result['state']
