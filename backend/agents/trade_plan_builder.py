"""
Agent 4: Trade Plan Builder 📋
역할: 사용자의 기간/성향에 맞춰 진입·손절·익절·분할 자동 설계
"""

from typing import Dict, List, Any


class TradePlanBuilder:
    """매매 계획 생성 에이전트"""
    
    def __init__(self):
        self.name = "Trade Plan Builder"
        
    def build_trade_plan(self, stock_data: Dict[str, Any], 
                        user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        매매 계획 생성
        
        Args:
            stock_data: 종목 데이터
                - ticker: 종목 코드
                - name: 종목명
                - current_price: 현재가
                - support_levels: 지지선 리스트
                - resistance_levels: 저항선 리스트
                - ma20: 20일 이평가
                - ma60: 60일 이평가
                - atr_20d: 20일 평균 진폭
                - volatility: 일간 변동성 (%)
                
            user_profile: 사용자 프로필
                - period: 단기 | 중기
                - risk_profile: 보수 | 중립 | 공격
                - account_size: 계좌 크기 (선택)
                
        Returns:
            매매 계획 딕셔너리
        """
        current_price = stock_data.get('current_price', 0)
        
        # ========== 1) 손절 먼저 고정 (가장 중요) ==========
        stop_loss = self._calculate_stop_loss(stock_data)
        
        # ========== 2) 진입가 설정 ==========
        entry_points = self._calculate_entry_points(stock_data)
        
        # ========== 3) 목표가 설정 (손절 대비 2배 이상) ==========
        targets = self._calculate_targets(stock_data, stop_loss, user_profile)
        
        # ========== 4) 포지션 사이즈 계산 ==========
        position_size = self._calculate_position_size(
            stock_data, stop_loss, user_profile
        )
        
        # ========== 5) 분할 계획 생성 ==========
        split_plan = self._generate_split_plan(
            entry_points, stop_loss, targets, position_size, user_profile
        )
        
        # ========== 6) Why 설명 생성 ==========
        why_reasons = self._generate_why_reasons(
            stock_data, stop_loss, targets, position_size
        )
        
        # 리스크/리워드 비율 계산
        risk = current_price - stop_loss
        reward = targets['aggressive'] - current_price
        risk_reward_ratio = reward / risk if risk > 0 else 0
        
        return {
            "ticker": stock_data.get('ticker', ''),
            "name": stock_data.get('name', ''),
            "currency": stock_data.get('currency', 'KRW'),
            "current_price": current_price,
            "entry": entry_points,
            "stop_loss": stop_loss,
            "targets": targets,
            "position_size": position_size,
            "split_plan": split_plan,
            "risk_reward_ratio": round(risk_reward_ratio, 2),
            "why": why_reasons
        }
    
    def _calculate_stop_loss(self, stock_data: Dict[str, Any]) -> float:
        """손절가 계산"""
        current_price = stock_data.get('current_price', 0)
        ma20 = stock_data.get('ma20', current_price)
        ma60 = stock_data.get('ma60', current_price)
        atr = stock_data.get('atr_20d', current_price * 0.03)
        support_levels = stock_data.get('support_levels', [])
        
        # 기본 손절: 20일선 기준
        if ma20 > ma60:
            # 상승 추세: 20일선 -2%
            stop_loss = ma20 * 0.98
        else:
            # 조정 국면: 첫 번째 지지선 -3%
            if support_levels:
                stop_loss = support_levels[0] * 0.97
            else:
                stop_loss = current_price * 0.93
        
        # ATR 기반 손절 (최소값)
        atr_stop = current_price - (2 * atr)
        
        # 둘 중 높은 값 선택 (손절을 더 가깝게)
        final_stop = max(stop_loss, atr_stop)
        
        # 현재가 대비 최소 3%, 최대 10%
        min_stop = current_price * 0.90
        max_stop = current_price * 0.97
        
        return max(min_stop, min(max_stop, final_stop))
    
    def _calculate_entry_points(self, stock_data: Dict[str, Any]) -> Dict[str, float]:
        """진입가 계산"""
        current_price = stock_data.get('current_price', 0)
        ma20 = stock_data.get('ma20', current_price)
        resistance_levels = stock_data.get('resistance_levels', [])
        
        # 돌파 진입: 첫 번째 저항선 +0.5%
        if resistance_levels:
            breakout = resistance_levels[0] * 1.005
        else:
            breakout = current_price * 1.02
        
        # 눌림 진입: 20일선 +0.5%
        pullback = ma20 * 1.005
        
        return {
            "breakout": round(breakout, 0),
            "pullback": round(pullback, 0),
            "current": round(current_price, 0)
        }
    
    def _calculate_targets(self, stock_data: Dict[str, Any], 
                          stop_loss: float, 
                          user_profile: Dict[str, Any]) -> Dict[str, float]:
        """목표가 계산"""
        current_price = stock_data.get('current_price', 0)
        risk = current_price - stop_loss
        risk_profile = user_profile.get('risk_profile', '중립')
        
        # 리스크 프로필에 따른 배수 설정
        if risk_profile == '보수':
            conservative_multiplier = 2.0
            aggressive_multiplier = 3.0
        elif risk_profile == '공격':
            conservative_multiplier = 3.0
            aggressive_multiplier = 5.0
        else:  # 중립
            conservative_multiplier = 2.5
            aggressive_multiplier = 4.0
        
        conservative_target = current_price + (risk * conservative_multiplier)
        aggressive_target = current_price + (risk * aggressive_multiplier)
        
        # 저항선 고려
        resistance_levels = stock_data.get('resistance_levels', [])
        if resistance_levels:
            # 저항선을 넘지 않도록 조정
            for resistance in resistance_levels:
                if conservative_target > resistance * 0.98:
                    conservative_target = resistance * 0.98
                    break
        
        return {
            "conservative": round(conservative_target, 0),
            "aggressive": round(aggressive_target, 0)
        }
    
    def _calculate_position_size(self, stock_data: Dict[str, Any],
                                 stop_loss: float,
                                 user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """포지션 사이즈 계산"""
        current_price = stock_data.get('current_price', 0)
        risk = current_price - stop_loss
        account_size = user_profile.get('account_size', 0)
        risk_profile = user_profile.get('risk_profile', '중립')
        
        if account_size > 0:
            # Kelly Criterion 간소화
            # 거래당 최대 리스크: 보수 1%, 중립 2%, 공격 3%
            if risk_profile == '보수':
                max_risk_percent = 0.01
            elif risk_profile == '공격':
                max_risk_percent = 0.03
            else:
                max_risk_percent = 0.02
            
            risk_amount = account_size * max_risk_percent
            position_value = (risk_amount / risk) * current_price
            position_percent = (position_value / account_size) * 100
            shares = int(position_value / current_price)
            amount = shares * current_price
            
        else:
            # 계좌 크기 없으면 기본값
            if risk_profile == '보수':
                position_percent = 20
            elif risk_profile == '공격':
                position_percent = 30
            else:
                position_percent = 25
            
            shares = 0
            amount = 0
        
        return {
            "percent": round(position_percent, 1),
            "shares": shares,
            "amount": int(amount)
        }
    
    def _generate_split_plan(self, entry_points: Dict[str, float],
                            stop_loss: float,
                            targets: Dict[str, float],
                            position_size: Dict[str, Any],
                            user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """분할 매매 계획 생성"""
        plan = []
        period = user_profile.get('period', '단기')
        
        if period == '단기':
            # 단기: 2번 분할 진입, 2번 분할 익절
            plan.append({
                "action": "진입",
                "percent": 60,
                "price": int(entry_points['pullback']),
                "condition": "20일선 지지 확인"
            })
            plan.append({
                "action": "추가",
                "percent": 40,
                "price": int(entry_points['pullback'] * 0.98),
                "condition": "2차 지지선"
            })
            plan.append({
                "action": "손절",
                "percent": 100,
                "price": int(stop_loss),
                "condition": "손절선 이탈"
            })
            plan.append({
                "action": "익절",
                "percent": 50,
                "price": int(targets['conservative']),
                "condition": "1차 목표"
            })
            plan.append({
                "action": "익절",
                "percent": 50,
                "price": int(targets['aggressive']),
                "condition": "2차 목표"
            })
        else:
            # 중기: 3번 분할 진입, 3번 분할 익절
            plan.append({
                "action": "진입",
                "percent": 40,
                "price": int(entry_points['pullback']),
                "condition": "20일선 지지"
            })
            plan.append({
                "action": "추가",
                "percent": 30,
                "price": int(entry_points['pullback'] * 0.97),
                "condition": "2차 지지선"
            })
            plan.append({
                "action": "추가",
                "percent": 30,
                "price": int(entry_points['pullback'] * 0.95),
                "condition": "60일선 지지"
            })
            plan.append({
                "action": "손절",
                "percent": 100,
                "price": int(stop_loss),
                "condition": "손절선 이탈"
            })
            plan.append({
                "action": "익절",
                "percent": 30,
                "price": int(targets['conservative']),
                "condition": "1차 목표"
            })
            plan.append({
                "action": "익절",
                "percent": 40,
                "price": int(targets['conservative'] * 1.05),
                "condition": "2차 목표"
            })
            plan.append({
                "action": "익절",
                "percent": 30,
                "price": int(targets['aggressive']),
                "condition": "3차 목표"
            })
        
        return plan
    
    def _generate_why_reasons(self, stock_data: Dict[str, Any],
                             stop_loss: float,
                             targets: Dict[str, float],
                             position_size: Dict[str, Any]) -> List[str]:
        """Why 설명 생성"""
        reasons = []
        
        current_price = stock_data.get('current_price', 0)
        ma20 = stock_data.get('ma20', current_price)
        risk = current_price - stop_loss
        reward = targets['aggressive'] - current_price
        risk_reward = reward / risk if risk > 0 else 0
        
        # 지지선 설명
        reasons.append(f"20일선 {int(ma20):,}원 지지")
        
        # 손절 설명
        stop_loss_percent = ((current_price - stop_loss) / current_price) * 100
        reasons.append(f"손절 -{stop_loss_percent:.1f}% (ATR 기반)")
        
        # 리스크/리워드 설명
        reasons.append(f"리스크/리워드 1:{risk_reward:.1f}")
        
        # 포지션 사이즈 설명
        if position_size['percent'] > 0:
            reasons.append(f"포지션 크기 {position_size['percent']:.1f}%")
        
        return reasons[:4]
