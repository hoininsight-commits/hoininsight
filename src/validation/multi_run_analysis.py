# src/validation/multi_run_analysis.py
# Multi-Run Validation Analysis Engine (지시서 #081)

def analyze_runs(results):
    """Task 4: 다회 실행 결과 분석 (avg, min, max, variance)"""
    if not results:
        return {}
        
    scores = [r.get("quality_score", 0) for r in results]
    fallback_ratios = [r.get("fallback_ratio", 0) for r in results]

    return {
        "avg_score": round(sum(scores) / len(scores), 2),
        "min_score": min(scores),
        "max_score": max(scores),
        "avg_fallback": round(sum(fallback_ratios) / len(fallback_ratios), 2),
        "variance": max(scores) - min(scores)
    }

def final_system_state_calc(analysis):
    """Task 5: 분포 기반 최종 상태 판정"""
    if not analysis:
        return "UNKNOWN"
        
    # 1. Fallback 평균이 높은 경우 (의존성 과다)
    if analysis["avg_fallback"] > 0.3:
        return "DEGRADED"

    # 2. 분산이 너무 큰 경우 (안정성 결여)
    if analysis["variance"] > 30:
        return "UNSTABLE"

    # 3. 평균 점수가 높고 안정적인 경우
    if analysis["avg_score"] > 80 and analysis["avg_fallback"] < 0.15:
        return "HEALTHY"

    # 4. 그 외 경고 상태
    return "WARNING"
