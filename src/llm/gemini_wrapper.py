# src/llm/gemini_wrapper.py
# HOIN Insight Gemini Control Layer - Failure Reduction & Hardening (v3.2)

import json
import time
from pathlib import Path
from datetime import datetime
from .gemini_output_contract import validate_gemini_output
from .failure_types import FAILURE_TYPES
from src.llm.prompts import STRICT_JSON_PROMPT

def classify_failure(e):
    err_str = str(e).lower()
    if "429" in err_str or "quota" in err_str or "exhausted" in err_str:
        return "RATE_LIMIT"
    if "503" in err_str or "500" in err_str or "server" in err_str or "internal" in err_str:
        return "SERVER_ERROR"
    if "timeout" in err_str or "deadline" in err_str:
        return "TIMEOUT"
    if "safety" in err_str or "blocked" in err_str or "finish_reason" in err_str:
        return "SAFETY_BLOCKED"
    return "UNKNOWN"

def log_failure(agent, failure_type, retry_count):
    log_path = Path("data/logs/gemini_failure_log.json")
    if not log_path.exists():
        log_path.write_text(json.dumps([], indent=2))
    
    try:
        logs = json.loads(log_path.read_text())
    except:
        logs = []
        
    logs.append({
        "timestamp": datetime.now().isoformat(),
        "agent": agent,
        "failure_type": failure_type,
        "retry_count": retry_count
    })
    
    log_path.write_text(json.dumps(logs[-200:], indent=2, ensure_ascii=False))

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
    """Gemini 상태 추적 및 헬스 리포트 업데이트 (지시서 #077 개정)"""
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

    failure_rate = 0.0
    if health["total_calls"] > 0:
        health["fallback_ratio"] = round(health["fallback_count"] / health["total_calls"], 2)
        failure_rate = health["failures"] / health["total_calls"]

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

MAX_RETRY = 2

def call_gemini_with_control(client, prompt: str, agent: str = "UNKNOWN"):
    """중복 호출 제거 및 WRITER 대응 토큰 확장 (v4.4)"""
    
    # [FIX] WRITER의 경우 방송 대본이 길어질 수 있으므로 8192개까지 최대 개방
    limit = 8000 if agent == "WRITER" else 4000
    current_prompt = prompt
    
    for attempt in range(MAX_RETRY + 1):
        failure_type = None
        try:
            # [CRITICAL] 1회 호출로 통합 (double spend 방지)
            data = client.call_json(current_prompt, max_tokens=limit)
            
            if not data:
                # 파싱 실패는 이미 client 내부에서 복구를 시도했음에도 안 된 경우임
                failure_type = "JSON_PARSE_ERROR"
                raise Exception("Final JSON Parsing Failure")

            # 3. 계약 검증
            if not validate_gemini_output(data, agent=agent):
                failure_type = "CONTRACT_FAIL"
                raise Exception("Contract Violation")

            # 4. 품질 검증 (Quality Gate)
            from src.validation.quality_score import calculate_quality_score
            if isinstance(data, dict):
                q_score = calculate_quality_score(data, is_fallback=False)
            else:
                q_score = 80 if len(data) > 0 else 0
                
            if q_score < 60:
                failure_type = "LOW_QUALITY"
                raise Exception(f"Low Quality Score: {q_score}")

            # 최종 성공
            log_gemini_usage(agent, success=True, fallback_used=False, retry_count=attempt)
            update_gemini_health(success=True, fallback_used=False)
            return data

        except Exception as e:
            if not failure_type:
                failure_type = classify_failure(e)
            
            print(f"  [GEMINI_FAIL] Agent: {agent} | Type: {failure_type} | Attempt: {attempt+1} | Msg: {str(e)[:100]}")
            log_failure(agent, failure_type, attempt)
            
            # 5. 실패 유형별 대응
            if failure_type in ["RATE_LIMIT", "SERVER_ERROR", "TIMEOUT"] and attempt < MAX_RETRY:
                time.sleep((attempt + 1) * 2)
                continue
            
            if failure_type == "JSON_PARSE_ERROR" and attempt == 0:
                print(f"  🔄 Retrying with Strict Protocol...")
                current_prompt = STRICT_JSON_PROMPT + prompt
                continue
            
            break

    # 모든 시도 실패 시
    log_gemini_usage(agent, success=False, fallback_used=True, retry_count=attempt)
    update_gemini_health(success=False, fallback_used=True)
    return None
