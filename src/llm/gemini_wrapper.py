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

MAX_RETRY = 2

def call_gemini_with_control(client, prompt: str, agent: str = "UNKNOWN"):
    """중복 호출 제거 및 WRITER 대응 토큰 확장 (v4.4)"""
    
    # [지시서 #082] 분석 밀도 향상에 따른 토큰 한도 전면 개방
    limit = 8192
    current_prompt = prompt
    
    for attempt in range(MAX_RETRY + 1):
        failure_type = None
        try:
            # [GEMINI CALL] 호출 시각 및 에이전트 로깅
            print(f"  [GEMINI CALL] agent={agent}, time={datetime.now().strftime('%H:%M:%S')}")
            
            # [CRITICAL] 1회 호출로 통합 (double spend 방지)
            data = client.call_json(current_prompt, max_tokens=limit)
            
            # [RESPONSE HASH] 응답 다양성 검증을 위한 해시 추출
            import hashlib
            resp_hash = hashlib.md5(str(data).encode()).hexdigest()
            print(f"  [RESPONSE HASH] {resp_hash}")
            
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
            # update_gemini_health 제거 (client.call_json 내부에서 이미 처리됨)
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
            
            if failure_type == "JSON_PARSE_ERROR":
                # [DEBUG] 파싱 실패 시 원본 응답 길이 확인
                print(f"  [RAW_RESPONSE_DEBUG] Length: {len(str(e))} | {str(e)[:200]}")
                
            if failure_type == "JSON_PARSE_ERROR" and attempt == 0:
                print(f"  🔄 Retrying with Strict Protocol...")
                current_prompt = STRICT_JSON_PROMPT + prompt
                continue
            
            break

    # 모든 시도 실패 시
    log_gemini_usage(agent, success=False, fallback_used=True, retry_count=attempt)
    update_gemini_health(client, success=False, fallback_used=True)
    return None
