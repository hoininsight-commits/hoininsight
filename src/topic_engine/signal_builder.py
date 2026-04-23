from typing import List, Dict
import math

class SignalBuilder:
    """[TASK #101.2] 시장 지표 기반 결정론적 시그널 추출기 (Production v1.0)"""

    def __init__(self):
        pass

    def build_signals(self, market_data: Dict) -> List[Dict]:
        signals = []
        stats = market_data.get("multi_period_stats", {})
        
        for name, data in stats.items():
            z_score = data.get("z_score_20d", 0)
            chg_5d = data.get("chg_5d", 0)
            current = data.get("current")
            avg_20d = data.get("avg_20d")
            
            if current is None: continue

            # 1. 시그널 유형 판별
            signal_type = None
            signal_msg = ""
            
            # BREAK: Z-score가 비정상적일 때 (임계값 1.5로 하향 조정하여 Early Signal 포착)
            if abs(z_score) > 1.5:
                signal_type = "BREAK"
                direction = "상방" if z_score > 0 else "하방"
                signal_msg = f"{name.upper()} {direction} 이상징후 (Z-score: {z_score:.2f})"
            
            # DIVERGENCE: 5일 변화율과 Z-score 방향이 다를 때
            elif (chg_5d > 3.0 and z_score < -0.5) or (chg_5d < -3.0 and z_score > 0.5):
                signal_type = "DIVERGENCE"
                signal_msg = f"{name.upper()} 단기 추세 vs 장기 평균 괴리 (Mismatch 후보)"
            
            # TREND: 지속적인 방향성
            elif abs(chg_5d) > 2.0:
                signal_type = "TREND"
                direction = "강세" if chg_5d > 0 else "약세"
                signal_msg = f"{name.upper()} 5일 누적 {direction} 추세 ({chg_5d:+.2f}%)"
            
            if not signal_type:
                continue

            signals.append({
                "signal": signal_msg,
                "metrics": [name],
                "current": {name: current},
                "previous": {name: avg_20d},
                "change": {name: chg_5d},
                "z_scores": {name: z_score},
                "signal_type": signal_type
            })
            
        return signals
