# src/validation/quality_gate.py
# HOIN Insight Pipeline Quality Gate (v1.1)

from .quality_score import calculate_quality_score

def validate_minimum_quality(data: dict) -> bool:
    """분석 결과물이 최소한의 통찰을 포함하고 있는지 검증 (지시서 #076)"""
    score = calculate_quality_score(data)
    
    if score < 60:
        print(f"  ❌ [QUALITY_GATE] Quality Score Too Low: {score}/100")
        return False
        
    print(f"  ✅ [QUALITY_GATE] Quality check passed. Score: {score}/100")
    return True
