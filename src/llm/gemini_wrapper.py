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

def update_gemini_health(client, success: bool, fallback_used: bool):
    """GeminiClient의 통합 헬스 관리 기능을 호출 (v4.6)"""
    client._update_health(success=success)

def call_gemini_with_control(client, prompt: str, agent: str = "UNKNOWN", tier: int = 3):
    """중복 호출 제거 및 TIER별 재시도/백오프 적용 (v4.5)"""
    
    # [지시서 #093] TIER별 설정 (v4.7 Hardened)
    tier_config = {
        1: {"max_retries": 6, "backoff": [5, 10, 20, 30, 45, 60]}, # 필수: 끈질기게 재시도
        2: {"max_retries": 3, "backoff": [5, 10, 20]},           # 중요: 적절히 재시도
        3: {"max_retries": 1, "backoff": [5]}                    # 보조: 1회만 재시도
    }
    
    config = tier_config.get(tier, tier_config[3])
    max_retries = config["max_retries"]
    backoff = config["backoff"]
    
    limit = 8192
    current_prompt = prompt
    
    for attempt in range(max_retries + 1):
        failure_type = None
        try:
            # [GEMINI CALL] 호출 시각 및 에이전트 로깅
            print(f"  [GEMINI CALL] agent={agent}, tier={tier}, time={datetime.now().strftime('%H:%M:%S')}")
            
            # [CRITICAL] 1회 호출로 통합 (double spend 방지)
            data = client.call_json(current_prompt, max_tokens=limit)
            
            # [RESPONSE HASH] 응답 다양성 검증을 위한 해시 추출
            import hashlib
            resp_hash = hashlib.md5(str(data).encode()).hexdigest()
            print(f"  [RESPONSE HASH] {resp_hash}")
            
            if not data:
                failure_type = "JSON_PARSE_ERROR"
                raise Exception("Final JSON Parsing Failure")

            # 3. 계약 검증
            if not validate_gemini_output(data, agent=agent):
                failure_type = "CONTRACT_FAIL"
                raise Exception("Contract Violation")

            # 4. 품질 검증 (Quality Gate) - Analyst 등 일부 에이전트만 수행
            if agent == "ANALYST":
                from src.validation.quality_score import calculate_quality_score
                q_score = calculate_quality_score(data, is_fallback=False)
                if q_score < 60:
                    failure_type = "LOW_QUALITY"
                    raise Exception(f"Low Quality Score: {q_score}")

            # 최종 성공
            log_gemini_usage(agent, success=True, fallback_used=False, retry_count=attempt)
            return data

        except Exception as e:
            if not failure_type:
                failure_type = classify_failure(e)
            
            print(f"  [GEMINI_FAIL] Agent: {agent} | Tier: {tier} | Type: {failure_type} | Attempt: {attempt+1} | Msg: {str(e)[:100]}")
            log_failure(agent, failure_type, attempt)
            
            # 5. 실패 유형별 대응
            if failure_type in ["RATE_LIMIT", "SERVER_ERROR", "TIMEOUT"] and attempt < max_retries:
                wait_time = backoff[attempt] if attempt < len(backoff) else backoff[-1]
                time.sleep(wait_time)
                continue
            
            if failure_type == "JSON_PARSE_ERROR" and attempt == 0 and max_retries > 0:
                print(f"  🔄 Retrying with Strict Protocol...")
                current_prompt = STRICT_JSON_PROMPT + prompt
                continue
            
            break

    # 모든 시도 실패 시
    log_gemini_usage(agent, success=False, fallback_used=True, retry_count=attempt)
    update_gemini_health(client, success=False, fallback_used=True)
    return None
