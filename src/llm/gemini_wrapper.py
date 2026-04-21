# src/llm/gemini_wrapper.py
# HOIN Insight Gemini Control Layer - Wrapper with Validation & Logging

import json
from pathlib import Path
from datetime import datetime
from .gemini_output_contract import validate_gemini_output

def log_gemini_usage(agent: str, success: bool, fallback_used: bool, retry_count: int):
    log_path = Path("data/logs/gemini_usage_log.json")
    if not log_path.exists():
        log_path.write_text(json.dumps([], indent=2))
    
    try:
        logs = json.loads(log_path.read_text())
    except:
        logs = []
        
    logs.append({
        "timestamp": datetime.now().isoformat(),
        "agent": agent,
        "success": success,
        "fallback_used": fallback_used,
        "retry_count": retry_count
    })
    
    log_path.write_text(json.dumps(logs[-100:], indent=2, ensure_ascii=False))

def update_gemini_health(success: bool, fallback_used: bool):
    """Gemini 상태 추적 및 헬스 리포트 업데이트 (지시서 #076)"""
    health_path = Path("data/monitoring/gemini_health.json")
    try:
        health = json.loads(health_path.read_text())
    except:
        health = {"status": "HEALTHY", "total_calls": 0, "failures": 0, "fallback_count": 0, "fallback_ratio": 0.0, "last_updated": ""}

    health["total_calls"] += 1
    if not success:
        health["failures"] += 1
    if fallback_used:
        health["fallback_count"] += 1

    if health["total_calls"] > 0:
        health["fallback_ratio"] = round(health["fallback_count"] / health["total_calls"], 2)
        failure_rate = health["failures"] / health["total_calls"]

    # 실패 지표 기반 판단 기준 강화 (#077)
    if failure_rate > 0.5:
        health["status"] = "CRITICAL"
    elif failure_rate > 0.3:
        health["status"] = "DEGRADED"
    elif failure_rate > 0.1:
        health["status"] = "WARNING"
    else:
        health["status"] = "HEALTHY"

    health["last_updated"] = datetime.now().isoformat()
    health_path.write_text(json.dumps(health, indent=2, ensure_ascii=False))

MAX_RETRY = 3

def call_gemini_with_control(client, prompt: str, agent: str = "UNKNOWN"):
    """Gemini 호출을 제어하고 규약을 검증하는 래퍼 (v1.5)"""
    for attempt in range(MAX_RETRY):
        try:
            # 1. API 호출
            data = client.call_json(prompt)
            
            # 2. 계약 검증 (Contract Validation)
            if not data or not validate_gemini_output(data, agent=agent):
                print(f"  ❌ [CONTRACT_FAIL] {agent} Output Protocol Violation. Triggering Fallback.")
                log_gemini_usage(agent, success=False, fallback_used=True, retry_count=attempt)
                update_gemini_health(success=False, fallback_used=True)
                return None

            # 3. 성공 로깅
            log_gemini_usage(agent, success=True, fallback_used=False, retry_count=attempt)
            update_gemini_health(success=True, fallback_used=False)
            return data

        except Exception as e:
            err_msg = str(e).lower()
            if "timeout" in err_msg or "503" in err_msg or "deadline" in err_msg:
                print(f"  ⚠️ Gemini {agent} Attempt {attempt+1} Retry (Server Busy/Timeout): {e}")
                if attempt == MAX_RETRY - 1:
                    log_gemini_usage(agent, success=False, fallback_used=True, retry_count=attempt)
                    update_gemini_health(success=False, fallback_used=True)
                    return None
                continue
            else:
                print(f"  ❌ [GEMINI_ERROR] {agent} Critical Error: {e}")
                log_gemini_usage(agent, success=False, fallback_used=True, retry_count=attempt)
                update_gemini_health(success=False, fallback_used=True)
                return None

    return None
