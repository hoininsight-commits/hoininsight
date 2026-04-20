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

def call_gemini_with_control(client, prompt: str, agent: str = "UNKNOWN"):
    """Gemini 호출을 제어하고 규약을 검증하는 래퍼"""
    retry_count = 0
    for attempt in range(3):
        retry_count = attempt
        try:
            # 기존 GeminiClient의 call_json 또는 call 사용
            # 여기서는 제어 레이어 규약 검증을 위해 JSON 응답을 가정함
            data = client.call_json(prompt)
            
            if not data or not validate_gemini_output(data):
                raise Exception("Gemini Output Contract Violation")

            log_gemini_usage(agent, success=True, fallback_used=False, retry_count=retry_count)
            return data

        except Exception as e:
            print(f"  ⚠️ Gemini Control Layer Attempt {attempt+1} Fail: {e}")
            if attempt == 2:
                log_gemini_usage(agent, success=False, fallback_used=True, retry_count=retry_count)
                raise Exception("GeminiFailure")
            continue

    raise Exception("GeminiFailure")
