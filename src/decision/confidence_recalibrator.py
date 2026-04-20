# src/decision/confidence_recalibrator.py

def recalibrate_confidence(base_conf, history):
    """
    최근 20개 기록의 승률을 바탕으로 신뢰도 보정
    - 승률 < 40%: 신뢰도 30% 감쇄 (x0.7)
    - 승률 > 60%: 신뢰도 10% 강화 (x1.1)
    """
    if not history:
        return base_conf
        
    recent_20 = history[-20:]
    success_count = sum(1 for r in recent_20 if r.get("result") == "SUCCESS")
    success_rate = success_count / len(recent_20)
    
    multiplier = 1.0
    if success_rate < 0.4:
        multiplier = 0.7
    elif success_rate > 0.6:
        multiplier = 1.1
        
    return round(base_conf * multiplier, 2)

def get_current_calibration_factor(history):
    """현재 승률에 따른 보정 계수 반환"""
    if not history:
        return 1.0
        
    recent_20 = history[-20:]
    success_count = sum(1 for r in recent_20 if r.get("result") == "SUCCESS")
    success_rate = success_count / len(recent_20)
    
    if success_rate < 0.4:
        return 0.7
    elif success_rate > 0.6:
        return 1.1
    return 1.0
