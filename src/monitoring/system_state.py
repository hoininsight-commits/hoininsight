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
    """시스템의 현재 건전성 요약 반환"""
    health_path = Path("data/monitoring/gemini_health.json")
    stats_path = Path("data/logs/fallback_stats.json")
    
    try:
        health = json.loads(health_path.read_text())
        fallback_stats = json.loads(stats_path.read_text())
    except:
        return "UNKNOWN", "Monitoring data missing"

    # 1. Critical 조건: 전체 실행 중 Fallback 의존도가 70% 이상
    if fallback_stats.get("fallback_ratio", 0) > 0.7:
        return "CRITICAL", "Extremely high fallback dependency"

    # 2. Degraded 조건: 최근 Gemini API 실패율이 50% 이상
    if health.get("status") == "DEGRADED" or health.get("fallback_ratio", 0) > 0.5:
        return "DEGRADED", "Gemini failure rate high"

    return "NORMAL", "System healthy"
