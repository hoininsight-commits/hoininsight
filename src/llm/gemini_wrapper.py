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

MAX_RETRY = 3

def call_gemini_with_control(client, prompt: str, agent: str = "UNKNOWN"):
    """Gemini 호출을 제어하고 규약을 검증하는 래퍼 (v1.2)"""
    for attempt in range(MAX_RETRY):
        try:
            # 1. API 호출
            data = client.call_json(prompt)
            
            # 2. 계약 검증 (Contract Validation)
            if not data or not validate_gemini_output(data, agent=agent):
                # 규약 위반 시 재시도하지 않고 즉시 None 반환 (Task 3: Immediate Fallback)
                print(f"  ❌ [CONTRACT_FAIL] {agent} Output Protocol Violation. Triggering Fallback.")
                log_gemini_usage(agent, success=False, fallback_used=True, retry_count=attempt)
                return None

            # 3. 성공 로깅
            log_gemini_usage(agent, success=True, fallback_used=False, retry_count=attempt)
            return data

        except Exception as e:
            err_msg = str(e).lower()
            # 타임아웃이나 503 Busy 에러인 경우에만 재시도 수행
            if "timeout" in err_msg or "503" in err_msg or "deadline" in err_msg:
                print(f"  ⚠️ Gemini {agent} Attempt {attempt+1} Retry (Server Busy/Timeout): {e}")
                if attempt == MAX_RETRY - 1:
                    log_gemini_usage(agent, success=False, fallback_used=True, retry_count=attempt)
                    return None
                continue
            else:
                # 기타 파싱 에러나 구조적 에러는 즉시 중단 및 Fallback
                print(f"  ❌ [GEMINI_ERROR] {agent} Critical Error: {e}")
                log_gemini_usage(agent, success=False, fallback_used=True, retry_count=attempt)
                return None

    return None
