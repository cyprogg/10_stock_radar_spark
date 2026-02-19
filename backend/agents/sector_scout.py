"""
Agent 2: Sector Scout 🔍
역할: 섹터별 자금흐름/강도/뉴스를 합쳐 랭킹
"""

from typing import Dict, List, Any


class SectorScout:
    """섹터 분석 및 랭킹 에이전트"""
    
    def __init__(self):
        self.name = "Sector Scout"
        
    def score_sector(self, sector_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        섹터 점수 계산
        
        Args:
            sector_data: 섹터 데이터 딕셔너리
                - sector: 섹터 이름
                - volume_change_20d: 거래대금 20일 변화율 (배수)
                - foreign_net_buy_5d: 외국인 5일 순매수 (억원)
                - inst_net_buy_5d: 기관 5일 순매수 (억원)
                - price_change_20d: 20일 수익률 (%)
                - ma20_slope: 20일선 기울기
                - new_high_stocks: 신고가 종목 수
                - news_count_7d: 7일간 뉴스 건수
                - policy_keywords: 정책 키워드 리스트
                - disclosure_count: 공시 건수
                - duration: 테마 지속 기간 (일)
                
        Returns:
            섹터 점수 및 분석 결과
        """
        # 1) 자금 흐름 점수 (0~100)
        flow_score = self._calculate_flow_score(sector_data)
        
        # 2) 가격 구조 점수 (0~100)
        structure_score = self._calculate_structure_score(sector_data)
        
        # 3) 서사 점수 (0~100)
        narrative_score = self._calculate_narrative_score(sector_data)
        
        # 신호 판정
        signal = self._determine_signal(flow_score)
        
        # Why 생성
        why_reasons = self._generate_why_reasons(sector_data, flow_score, structure_score, narrative_score)
        
        # Counter 생성
        counter_reasons = self._generate_counter_reasons(sector_data, structure_score)
        
        # 신뢰도 계산
        confidence = self._calculate_confidence(flow_score, structure_score, narrative_score)
        
        # 테마 지속 기간 판정
        duration = self._format_duration(sector_data.get('duration', 0))
        
        return {
            "sector": sector_data.get('sector', ''),
            "flow_score": flow_score,
            "signal": signal,
            "duration": duration,
            "rank": 0,  # 상위에서 설정
            "breakdown": {
                "flow": flow_score,
                "structure": structure_score,
                "narrative": narrative_score
            },
            "why": why_reasons,
            "counter": counter_reasons,
            "confidence": confidence
        }
    
    def _calculate_flow_score(self, data: Dict[str, Any]) -> int:
        """자금 흐름 점수 계산 (0~100)"""
        score = 0
        
        # 거래대금 증가 (0~40점)
        volume_change = data.get('volume_change_20d', 1.0)
        if volume_change > 3:
            score += 40
        elif volume_change > 2:
            score += 30
        elif volume_change > 1.5:
            score += 20
        
        # 외국인 순매수 (0~30점)
        foreign_buy = data.get('foreign_net_buy_5d', 0)
        if foreign_buy > 200:
            score += 30
        elif foreign_buy > 100:
            score += 20
        elif foreign_buy > 50:
            score += 10
        
        # 기관 순매수 (0~30점)
        inst_buy = data.get('inst_net_buy_5d', 0)
        if inst_buy > 200:
            score += 30
        elif inst_buy > 100:
            score += 20
        elif inst_buy > 50:
            score += 10
        
        return min(100, score)
    
    def _calculate_structure_score(self, data: Dict[str, Any]) -> int:
        """가격 구조 점수 계산 (0~100)"""
        score = 0
        
        # 가격 상승률 (0~50점)
        price_change = data.get('price_change_20d', 0)
        if price_change > 20:
            score += 50
        elif price_change > 10:
            score += 35
        elif price_change > 5:
            score += 20
        
        # 이평선 기울기 (0~30점)
        ma_slope = data.get('ma20_slope', 0)
        if ma_slope > 1.0:
            score += 30
        elif ma_slope > 0.5:
            score += 20
        elif ma_slope > 0:
            score += 10
        
        # 신고가 종목 수 (0~20점)
        new_highs = data.get('new_high_stocks', 0)
        score += min(20, new_highs * 5)
        
        return min(100, score)
    
    def _calculate_narrative_score(self, data: Dict[str, Any]) -> int:
        """서사 점수 계산 (0~100)"""
        score = 0
        
        # 뉴스 빈도 (0~50점)
        news_count = data.get('news_count_7d', 0)
        score += min(50, news_count * 2)
        
        # 정책 키워드 (0~30점)
        policy_keywords = data.get('policy_keywords', [])
        score += min(30, len(policy_keywords) * 15)
        
        # 공시 이벤트 (0~20점)
        disclosure_count = data.get('disclosure_count', 0)
        score += min(20, disclosure_count * 10)
        
        return min(100, score)
    
    def _determine_signal(self, flow_score: int) -> str:
        """신호 판정"""
        if flow_score >= 80:
            return "SURGE"
        elif flow_score >= 50:
            return "NORMAL"
        else:
            return "WEAK"
    
    def _generate_why_reasons(self, data: Dict[str, Any], 
                             flow: int, structure: int, narrative: int) -> List[str]:
        """긍정 이유 생성"""
        reasons = []
        
        volume_change = data.get('volume_change_20d', 1.0)
        if volume_change > 2:
            reasons.append(f"거래대금 {volume_change:.1f}배 증가 (20일 기준)")
        
        foreign_buy = data.get('foreign_net_buy_5d', 0)
        inst_buy = data.get('inst_net_buy_5d', 0)
        if foreign_buy > 50 or inst_buy > 50:
            reasons.append(f"외국인 {foreign_buy:.0f}억 + 기관 {inst_buy:.0f}억 순매수")
        
        policy_keywords = data.get('policy_keywords', [])
        news_count = data.get('news_count_7d', 0)
        if len(policy_keywords) > 0 and news_count > 10:
            keywords_str = '/'.join(policy_keywords[:3])
            reasons.append(f"정책 키워드 '{keywords_str}' {news_count}건")
        
        price_change = data.get('price_change_20d', 0)
        if price_change > 10:
            reasons.append(f"20일 수익률 +{price_change:.1f}%")
        
        return reasons[:3]  # 최대 3개
    
    def _generate_counter_reasons(self, data: Dict[str, Any], structure: int) -> List[str]:
        """부정 이유 생성"""
        reasons = []
        
        new_highs = data.get('new_high_stocks', 0)
        if new_highs < 3:
            reasons.append(f"신고가 종목 {new_highs}개로 제한적")
        
        duration = data.get('duration', 0)
        if duration > 14:
            reasons.append(f"테마 지속 {duration}일차 (피로도 체크 필요)")
        
        if structure < 50:
            reasons.append("가격 구조 약화 (이평선 지지 확인 필요)")
        
        return reasons[:2]  # 최대 2개
    
    def _calculate_confidence(self, flow: int, structure: int, narrative: int) -> int:
        """신뢰도 계산 (0~100)"""
        # 세 점수의 가중 평균
        confidence = (flow * 0.4 + structure * 0.4 + narrative * 0.2)
        return int(min(100, max(0, confidence)))
    
    def _format_duration(self, days: int) -> str:
        """지속 기간 포맷팅"""
        if days < 7:
            return f"{days}일"
        elif days < 30:
            weeks = days // 7
            return f"{weeks}주"
        else:
            months = days // 30
            return f"{months}개월"
    
    def rank_sectors(self, sectors_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        여러 섹터를 점수 기준으로 랭킹
        
        Args:
            sectors_data: 섹터 데이터 리스트
            
        Returns:
            랭킹된 섹터 결과 리스트
        """
        results = []
        
        for sector_data in sectors_data:
            result = self.score_sector(sector_data)
            results.append(result)
        
        # flow_score 기준 내림차순 정렬
        results.sort(key=lambda x: x['flow_score'], reverse=True)
        
        # 순위 부여
        for idx, result in enumerate(results):
            result['rank'] = idx + 1
        
        return results
