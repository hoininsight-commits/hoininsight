# src/validation/result_classifier.py
# HOIN Insight Result Classification Layer

def classify_result(action, return_pct):
    """
    성과 판정 기준:
    - SUCCESS: 방향 맞고 +1% 이상
    - FAIL: 방향 틀리고 -1% 이하
    - NEUTRAL: 나머지
    """
    if action == "BUY":
        if return_pct >= 1.0:
            return "SUCCESS"
        elif return_pct <= -1.0:
            return "FAIL"
    elif action == "WATCH" or action == "HOLD":
        # WATCH나 HOLD는 보수적 접근이므로 큰 변동이 없어야 본전
        if abs(return_pct) < 1.0:
            return "SUCCESS"
        else:
            return "NEUTRAL"
            
    return "NEUTRAL"
