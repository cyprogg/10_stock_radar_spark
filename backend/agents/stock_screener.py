"""
Agent 3: Stock Screener 🎯
역할: 섹터 내부 종목을 Leader/Follower/No-go로 분류
"""

from typing import Dict, List, Any


class StockScreener:
    """종목 분류 및 스크리닝 에이전트"""
    
    def __init__(self):
        self.name = "Stock Screener"
        
    def classify_stock(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        종목 분류 (Leader/Follower/No-go)
        
        Args:
            stock_data: 종목 데이터 딕셔너리
                - ticker: 종목 코드
                - name: 종목명
                - sector: 섹터
                - flow_score: 자금 흐름 점수
                - cycle_fit: 사이클 적합 여부
                - quality_score: 품질 점수
                - governance_score: 지배구조 점수
                - narrative_score: 서사 점수
                - risk_score: 리스크 점수 (낮을수록 좋음)
                - time_fit: 타이밍 적합 여부
                - value_score: 밸류에이션 점수
                - momentum_quality: 모멘텀 품질 데이터
                    - sector_sync: 섹터 동반 상승
                    - inst_participation: 기관 참여
                    - news_type: fundamental | rumor | single
                    - group_rally: 여러 종목 동시 상승
                - gap_up_with_distribution: 갭상승 후 분배 여부
                - single_rumor: 단일 루머 급등 여부
                - late_theme: 테마 말기 종목 여부
                - no_structure: 구조 파손 여부
                - retail_dominance: 개인 비중 (0~1)
                
        Returns:
            분류 결과 및 액션
        """
        # ========== No-Go 판정 (우선) ==========
        nogo_result = self._check_nogo_conditions(stock_data)
        if nogo_result:
            return nogo_result
        
        # ========== 9요소 필수 조건 체크 ==========
        mandatory_result = self._check_mandatory_conditions(stock_data)
        if mandatory_result:
            return mandatory_result
        
        # ========== 모멘텀 품질로 Leader/Follower 구분 ==========
        momentum_quality = stock_data.get('momentum_quality', {})
        momentum_score = self._calculate_momentum_quality(momentum_quality)
        
        # 9요소 점수 수집
        scores = {
            "1_flow": stock_data.get('flow_score', 0),
            "2_cycle": stock_data.get('cycle_fit', False),
            "3_quality": stock_data.get('quality_score', 0),
            "4_governance": stock_data.get('governance_score', 0),
            "5_narrative": stock_data.get('narrative_score', 0),
            "6_risk": stock_data.get('risk_score', 0),
            "7_time_fit": stock_data.get('time_fit', False),
            "8_value": stock_data.get('value_score', 0),
            "9_momentum": momentum_score
        }
        
        # Leader/Follower 분류
        if momentum_score >= 85:
            classification = "LEADER"
            action = "BUY_NOW"
            why_reasons = self._generate_leader_reasons(stock_data, momentum_quality)
        else:
            classification = "FOLLOWER"
            action = "BUY_PULLBACK"
            why_reasons = self._generate_follower_reasons(stock_data, momentum_quality)
        
        # Counter 생성
        counter_reasons = self._generate_counter_reasons(stock_data, scores)
        
        # 신뢰도 계산
        confidence = self._calculate_confidence(scores, momentum_score)
        
        return {
            "ticker": stock_data.get('ticker', ''),
            "name": stock_data.get('name', ''),
            "currency": stock_data.get('currency', 'KRW'),
            "classification": classification,
            "action": action,
            "scores": scores,
            "why_leader" if classification == "LEADER" else "why_follower": why_reasons,
            "counter": counter_reasons,
            "confidence": confidence
        }
    
    def _check_nogo_conditions(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """No-Go 조건 체크 (6개 규칙)"""
        nogo_flags = []
        
        # 1) 단일 기사 급등 + 거래대금 폭증
        momentum_quality = data.get('momentum_quality', {})
        if (momentum_quality.get('news_type') == 'single' and 
            data.get('flow_score', 0) > 90):
            nogo_flags.append("단일 기사 급등")
        
        # 2) 갭 상승 후 장대 음봉
        if data.get('gap_up_with_distribution', False):
            nogo_flags.append("갭 상승 후 분배")
        
        # 3) 테마 내 5번째 이후 급등주
        if data.get('late_theme', False):
            nogo_flags.append("테마 말기")
        
        # 4) 개인 순매수 80%↑ + 기관 이탈
        if (data.get('retail_dominance', 0) > 0.8 and 
            not momentum_quality.get('inst_participation', False)):
            nogo_flags.append("개인 독주")
        
        # 5) 핵심 이평(20/60) 동시 이탈
        if data.get('no_structure', False):
            nogo_flags.append("구조 파손")
        
        # 6) 손절선이 구조적으로 설정 불가
        if data.get('risk_score', 0) > 50:
            nogo_flags.append("손절 불가")
        
        # 하나라도 해당 시 No-Go
        if nogo_flags:
            return {
                "ticker": data.get('ticker', ''),
                "name": data.get('name', ''),
                "currency": data.get('currency', 'KRW'),
                "classification": "NO_GO",
                "action": "AVOID",
                "reason": " | ".join(nogo_flags),
                "scores": {},
                "confidence": 95
            }
        
        return None
    
    def _check_mandatory_conditions(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """9요소 필수 조건 체크"""
        failed_conditions = []
        
        if data.get('flow_score', 0) < 70:
            failed_conditions.append("자금 흐름 부족")
        
        if not data.get('cycle_fit', False):
            failed_conditions.append("사이클 부적합")
        
        if data.get('quality_score', 0) < 60:
            failed_conditions.append("품질 미달")
        
        if data.get('governance_score', 0) < 50:
            failed_conditions.append("지배구조 미달")
        
        if data.get('narrative_score', 0) < 60:
            failed_conditions.append("서사 부족")
        
        if data.get('risk_score', 0) > 30:
            failed_conditions.append("리스크 과다")
        
        if not data.get('time_fit', False):
            failed_conditions.append("타이밍 부적합")
        
        if failed_conditions:
            return {
                "ticker": data.get('ticker', ''),
                "name": data.get('name', ''),
                "currency": data.get('currency', 'KRW'),
                "classification": "NO_GO",
                "action": "AVOID",
                "reason": "필수 요소 미달: " + ", ".join(failed_conditions),
                "scores": {},
                "confidence": 90
            }
        
        return None
    
    def _calculate_momentum_quality(self, momentum_quality: Dict[str, Any]) -> int:
        """모멘텀 품질 점수 계산 (0~100)"""
        score = 0
        
        # 진짜 모멘텀 조건
        if momentum_quality.get('sector_sync', False):
            score += 35
        
        if momentum_quality.get('inst_participation', False):
            score += 30
        
        news_type = momentum_quality.get('news_type', '')
        if news_type == 'fundamental':
            score += 25
        elif news_type == 'rumor':
            score -= 50
        elif news_type == 'single':
            score -= 30
        
        if momentum_quality.get('group_rally', False):
            score += 10
        
        return max(0, min(100, score))
    
    def _generate_leader_reasons(self, data: Dict[str, Any], 
                                 mq: Dict[str, Any]) -> List[str]:
        """리더 종목 이유 생성"""
        reasons = []
        
        if mq.get('sector_sync', False):
            reasons.append("섹터 전체 상승 (진짜 모멘텀)")
        
        if mq.get('inst_participation', False):
            reasons.append("기관/외국인 동시 매수")
        
        if mq.get('news_type') == 'fundamental':
            reasons.append("펀더멘털 기반 뉴스 (수주/실적)")
        
        if data.get('quality_score', 0) >= 80:
            reasons.append("높은 품질 지표")
        
        return reasons[:3]
    
    def _generate_follower_reasons(self, data: Dict[str, Any],
                                   mq: Dict[str, Any]) -> List[str]:
        """팔로워 종목 이유 생성"""
        reasons = []
        
        reasons.append("9요소 필수 조건 통과")
        
        if data.get('flow_score', 0) >= 70:
            reasons.append("양호한 자금 흐름")
        
        if not mq.get('sector_sync', False):
            reasons.append("독립 모멘텀 (섹터 동반 미약)")
        
        if data.get('value_score', 0) >= 60:
            reasons.append("적정 밸류에이션")
        
        return reasons[:3]
    
    def _generate_counter_reasons(self, data: Dict[str, Any], 
                                  scores: Dict[str, Any]) -> List[str]:
        """반론 이유 생성"""
        reasons = []
        
        # 밸류에이션 체크
        if scores.get('8_value', 100) < 50:
            reasons.append("밸류에이션 고평가 구간")
        
        # 리스크 체크
        if scores['6_risk'] > 20:
            reasons.append(f"하방 리스크 {scores['6_risk']}점")
        
        # 모멘텀 품질 체크
        if scores['9_momentum'] < 70:
            reasons.append("모멘텀 품질 중간 수준")
        
        return reasons[:2]
    
    def _calculate_confidence(self, scores: Dict[str, Any], momentum: int) -> int:
        """신뢰도 계산 (0~100)"""
        # 핵심 점수들의 평균
        key_scores = [
            scores['1_flow'],
            scores['3_quality'],
            scores['5_narrative'],
            momentum
        ]
        
        avg_score = sum(key_scores) / len(key_scores)
        
        # Boolean 값이 True면 가점
        if scores.get('2_cycle', False):
            avg_score += 5
        if scores.get('7_time_fit', False):
            avg_score += 5
        
        return int(min(100, max(0, avg_score)))
    
    def screen_stocks(self, stocks_data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        여러 종목을 분류
        
        Args:
            stocks_data: 종목 데이터 리스트
            
        Returns:
            분류된 종목 딕셔너리 (leaders, followers, nogo)
        """
        leaders = []
        followers = []
        nogo = []
        
        for stock_data in stocks_data:
            result = self.classify_stock(stock_data)
            
            if result['classification'] == 'LEADER':
                leaders.append(result)
            elif result['classification'] == 'FOLLOWER':
                followers.append(result)
            else:
                nogo.append(result)
        
        # 신뢰도 순으로 정렬
        leaders.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        followers.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        
        return {
            "leaders": leaders,
            "followers": followers,
            "nogo": nogo
        }
