"""
Agent 5: Devil's Advocate 😈
역할: "왜 이 판단이 틀릴 수 있는지" 2~3개 자동 제시
"""

from typing import Dict, List, Any


class DevilsAdvocate:
    """반론 제시 에이전트"""
    
    def __init__(self):
        self.name = "Devil's Advocate"
        
    def generate_counter_arguments(self, recommendation: Dict[str, Any], 
                                   additional_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        반론 생성
        
        Args:
            recommendation: 추천 결과
                - ticker: 종목 코드
                - name: 종목명
                - action: BUY_NOW | BUY_PULLBACK | AVOID
                - classification: LEADER | FOLLOWER | NO_GO
                - scores: 9요소 점수
                - why: 긍정 이유
                
            additional_data: 추가 데이터 (선택)
                - sector_rank: 섹터 내 순위
                - theme_duration: 테마 지속 기간
                - per: PER
                - pbr: PBR
                - sector_avg_per: 섹터 평균 PER
                - price_gap: 이격도
                
        Returns:
            반론 딕셔너리
        """
        counter_arguments = []
        
        scores = recommendation.get('scores', {})
        classification = recommendation.get('classification', '')
        
        # ========== 1) 밸류에이션 체크 ==========
        valuation_counter = self._check_valuation(scores, additional_data)
        if valuation_counter:
            counter_arguments.append(valuation_counter)
        
        # ========== 2) 리스크 체크 ==========
        risk_counter = self._check_risk(scores)
        if risk_counter:
            counter_arguments.append(risk_counter)
        
        # ========== 3) 모멘텀 체크 ==========
        momentum_counter = self._check_momentum(scores, classification)
        if momentum_counter:
            counter_arguments.append(momentum_counter)
        
        # ========== 4) 기술적 체크 ==========
        technical_counter = self._check_technical(additional_data)
        if technical_counter:
            counter_arguments.append(technical_counter)
        
        # ========== 5) 테마 피로도 체크 ==========
        theme_counter = self._check_theme_fatigue(additional_data)
        if theme_counter:
            counter_arguments.append(theme_counter)
        
        # 최대 3개만 선택 (severity 높은 순)
        counter_arguments.sort(key=lambda x: self._severity_to_num(x['severity']), reverse=True)
        counter_arguments = counter_arguments[:3]
        
        # 최종 노트 생성
        final_note = self._generate_final_note(
            classification, 
            recommendation.get('action', ''),
            counter_arguments
        )
        
        return {
            "counter_arguments": counter_arguments,
            "final_note": final_note
        }
    
    def _check_valuation(self, scores: Dict[str, Any], 
                        additional_data: Dict[str, Any]) -> Dict[str, Any]:
        """밸류에이션 체크"""
        value_score = scores.get('8_value', 100)
        
        if value_score < 50:
            # 추가 데이터가 있으면 상세 설명
            if additional_data:
                per = additional_data.get('per', 0)
                sector_avg_per = additional_data.get('sector_avg_per', 0)
                
                if per > 0 and sector_avg_per > 0:
                    point = f"PER {per:.1f}배로 업종 평균({sector_avg_per:.1f}배) 대비 고평가"
                else:
                    point = "PER/PBR 기준 고평가 구간"
            else:
                point = "밸류에이션 점수 낮음 (고평가 가능성)"
            
            return {
                "category": "밸류에이션",
                "point": point,
                "severity": "medium",
                "source": "재무제표 분석"
            }
        
        return None
    
    def _check_risk(self, scores: Dict[str, Any]) -> Dict[str, Any]:
        """리스크 체크"""
        risk_score = scores.get('6_risk', 0)
        
        if risk_score > 20:
            severity = "high" if risk_score > 30 else "medium"
            
            return {
                "category": "리스크",
                "point": f"하방 리스크 점수 {risk_score} (변동성 주의)",
                "severity": severity,
                "source": "리스크 분석"
            }
        
        return None
    
    def _check_momentum(self, scores: Dict[str, Any], 
                       classification: str) -> Dict[str, Any]:
        """모멘텀 체크"""
        momentum_score = scores.get('9_momentum', 0)
        
        if momentum_score < 70:
            point = "모멘텀 품질 중간 수준 (진위 의심)"
            severity = "high" if momentum_score < 50 else "medium"
            
            return {
                "category": "모멘텀",
                "point": point,
                "severity": severity,
                "source": "모멘텀 분석"
            }
        
        # 리더인데 모멘텀이 85 미만이면 경고
        if classification == "LEADER" and momentum_score < 85:
            return {
                "category": "모멘텀",
                "point": "리더 분류되었으나 모멘텀 품질 임계치 근처",
                "severity": "low",
                "source": "모멘텀 분석"
            }
        
        return None
    
    def _check_technical(self, additional_data: Dict[str, Any]) -> Dict[str, Any]:
        """기술적 체크"""
        if not additional_data:
            return None
        
        price_gap = additional_data.get('price_gap', 0)
        
        # 이격도 8% 이상이면 과열
        if price_gap > 8:
            return {
                "category": "기술적",
                "point": f"20일 이평 급등 후 이격도 {price_gap:.1f}% (과열)",
                "severity": "low",
                "source": "차트 구조"
            }
        
        # 이격도 -5% 이하면 약세
        if price_gap < -5:
            return {
                "category": "기술적",
                "point": f"20일 이평 대비 {price_gap:.1f}% 이탈 (약세)",
                "severity": "medium",
                "source": "차트 구조"
            }
        
        return None
    
    def _check_theme_fatigue(self, additional_data: Dict[str, Any]) -> Dict[str, Any]:
        """테마 피로도 체크"""
        if not additional_data:
            return None
        
        sector_rank = additional_data.get('sector_rank', 0)
        theme_duration = additional_data.get('theme_duration', 0)
        
        # 섹터 내 3번째 이상이면 경고
        if sector_rank >= 3:
            return {
                "category": "모멘텀",
                "point": f"섹터 내 {sector_rank}번째 급등주 (테마 피로도 체크 필요)",
                "severity": "high",
                "source": "섹터 분석"
            }
        
        # 테마 지속 2주 이상이면 경고
        if theme_duration > 14:
            weeks = theme_duration // 7
            return {
                "category": "모멘텀",
                "point": f"테마 지속 {weeks}주차 (피로도 높음)",
                "severity": "medium",
                "source": "섹터 분석"
            }
        
        return None
    
    def _severity_to_num(self, severity: str) -> int:
        """심각도를 숫자로 변환"""
        if severity == "high":
            return 3
        elif severity == "medium":
            return 2
        else:
            return 1
    
    def _generate_final_note(self, classification: str, action: str,
                            counter_arguments: List[Dict[str, Any]]) -> str:
        """최종 노트 생성"""
        if not counter_arguments:
            if classification == "LEADER":
                return "✅ 반론 사항 없음. 리더 종목으로 적극 고려 가능."
            elif classification == "FOLLOWER":
                return "✅ 반론 사항 없음. 눌림 매수 대기 권장."
            else:
                return "⚠️ No-Go 종목. 진입 금지."
        
        # High severity가 있으면 강력 경고
        high_severity_count = sum(1 for arg in counter_arguments if arg['severity'] == 'high')
        
        if high_severity_count >= 2:
            return f"🚨 심각한 반론 {high_severity_count}건. 진입 재검토 필요."
        elif high_severity_count == 1:
            if classification == "LEADER":
                return "⚠️ 리더 종목이나 주요 반론 있음. 진입 타이밍 신중히 검토하세요."
            else:
                return "⚠️ 팔로워 종목에 주요 반론 있음. 눌림 매수 대기 권장."
        else:
            if classification == "LEADER":
                return "⚠️ 리더 종목이나 소폭 반론 있음. 리스크 관리 철저히 하세요."
            elif classification == "FOLLOWER":
                return "⚠️ 팔로워 종목에 소폭 반론 있음. 눌림 매수 대기 및 분할 진입 권장."
            else:
                return "⚠️ No-Go 종목. 진입 금지."
    
    def analyze_recommendation(self, recommendation: Dict[str, Any],
                              additional_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        추천 결과에 대한 종합 분석 (반론 포함)
        
        Returns:
            원본 추천 + 반론이 합쳐진 딕셔너리
        """
        counter_result = self.generate_counter_arguments(recommendation, additional_data)
        
        return {
            **recommendation,
            "devil_advocate": counter_result
        }
