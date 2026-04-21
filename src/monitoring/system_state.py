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

def get_system_state():
    """시스템의 현재 건전성 요약 반환 (지시서 #077 강화 버전)"""
    health_path = Path("data/monitoring/gemini_health.json")
    stats_path = Path("data/logs/fallback_stats.json")
    
    try:
        health = json.loads(health_path.read_text())
        fallback_stats = json.loads(stats_path.read_text())
    except:
        return "UNKNOWN", "Monitoring data missing"

    fallback_ratio = fallback_stats.get("fallback_ratio", 0)
    gemini_status = health.get("status", "HEALTHY")

    # 1. Fallback Ratio 기반 기초 상태 선정 (#077)
    if fallback_ratio > 0.7:
        state = "CRITICAL"
    elif fallback_ratio > 0.3:
        state = "DEGRADED"
    elif fallback_ratio > 0.1:
        state = "WARNING"
    else:
        state = "NORMAL"

    # 2. Gemini Health 연동 보정
    if gemini_status == "CRITICAL":
        state = "CRITICAL"
    elif gemini_status == "DEGRADED" and state != "CRITICAL":
        state = "DEGRADED"
    elif gemini_status == "WARNING" and state in ["NORMAL"]:
        state = "WARNING"

    # 3. Task 5: Fallback 발생 시 NORMAL 금지 보정
    if fallback_ratio > 0 and state == "NORMAL":
        state = "WARNING"

    # 상태 요약 메시지 생성
    reasons = []
    if fallback_ratio > 0: reasons.append(f"Fallback Ratio: {fallback_ratio}")
    if gemini_status != "HEALTHY": reasons.append(f"Gemini Health: {gemini_status}")
    
    reason_str = ", ".join(reasons) if reasons else "System healthy"
    
    return state, reason_str
