# src/monitoring/system_state.py
import json
from pathlib import Path
from datetime import datetime

def update_fallback_stats(is_fallback: bool):
    """시스템 전체 오퍼레이션 중 Fallback 의존도를 기록 (지시서 #076)"""
    stats_path = Path("data/logs/fallback_stats.json")
    try:
        stats = json.loads(stats_path.read_text())
    except:
        stats = {"total_runs": 0, "fallback_runs": 0, "fallback_ratio": 0.0}

    stats["total_runs"] += 1
    if is_fallback:
        stats["fallback_runs"] += 1

    if stats["total_runs"] > 0:
        stats["fallback_ratio"] = round(stats["fallback_runs"] / stats["total_runs"], 2)

    stats_path.write_text(json.dumps(stats, indent=2, ensure_ascii=False))

def validate_system_state(state, fallback_ratio, quality_score):
    """Task 2: 상태 sanity check - 가짜 정상 상태 완전 차단"""
    if fallback_ratio > 0.1 and state == "NORMAL":
        raise Exception(f"Invalid State: fallback ({fallback_ratio}) exists but state is NORMAL")

    if quality_score < 60 and state == "NORMAL":
        raise Exception(f"Invalid State: low quality ({quality_score}) but state is NORMAL")

def get_system_state(quality_score=0):
    """시스템의 현재 건전성 요약 반환 (지시서 #081 교정 버전)"""
    health_path = Path("data/monitoring/gemini_health.json")
    stats_path = Path("data/logs/fallback_stats.json")
    
    try:
        health = json.loads(health_path.read_text())
        fallback_stats = json.loads(stats_path.read_text())
    except:
        return "UNKNOWN", "Monitoring data missing"

    total_calls = max(health.get("total_calls", 0), 1)
    failures = health.get("failures", 0)
    failure_rate = failures / total_calls
    fallback_ratio = fallback_stats.get("fallback_ratio", 0)

    # 1. 상태 계산 (지시서 #081 Task 1)
    if fallback_ratio > 0.7 or failure_rate > 0.5:
        state = "CRITICAL"
    elif fallback_ratio > 0.3 or failure_rate > 0.3:
        state = "DEGRADED"
    elif fallback_ratio > 0.1 or failure_rate > 0.1:
        state = "WARNING"
    elif quality_score < 70:
        state = "WARNING"
    else:
        state = "NORMAL"

    # 2. Sanity Check 수행
    try:
        validate_system_state(state, fallback_ratio, quality_score)
    except Exception as e:
        # 오류 발생 시 강제 하향 조정
        state = "WARNING"
        return state, str(e)

    # 상태 요약 메시지 생성
    reasons = []
    if fallback_ratio > 0: reasons.append(f"Fallback: {fallback_ratio}")
    if failure_rate > 0: reasons.append(f"Failure: {round(failure_rate, 2)}")
    if quality_score > 0: reasons.append(f"Quality: {quality_score}")
    
    reason_str = ", ".join(reasons) if reasons else "System healthy"
    
    return state, reason_str
