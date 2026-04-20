# src/validation/failure_attribution.py
# HOIN Insight Failure Attribution Layer

FAILURE_TYPES = [
    "RULE_ERROR",
    "GEMINI_REASONING_ERROR",
    "DATA_ERROR",
    "TIMING_ERROR",
    "OVERCONFIDENCE"
]

def attribute_failure(error_msg: str) -> str:
    """에러 메시지를 분석하여 실패 유형 분류 (v1.0 단순 매칭)"""
    error_msg = error_msg.lower()
    if "gemini" in error_msg or "contract" in error_msg:
        return "GEMINI_REASONING_ERROR"
    if "data" in error_msg or "missing" in error_msg:
        return "DATA_ERROR"
    if "timeout" in error_msg or "timing" in error_msg:
        return "TIMING_ERROR"
    return "RULE_ERROR"
