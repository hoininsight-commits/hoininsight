# src/validation/failure_attribution.py
# HOIN Insight Failure Attribution Layer

FAILURE_TYPES = [
    "GEMINI_REASONING_ERROR",
    "FLOW_MISREAD",
    "TIMING_ERROR",
    "OVERCONFIDENCE",
    "UNKNOWN"
]

def attribute_failure(error_msg: str) -> str:
    """에러 메시지를 분석하여 실패 유형 분류 (v1.1)"""
    error_msg = error_msg.lower()
    if "gemini" in error_msg or "reasoning" in error_msg:
        return "GEMINI_REASONING_ERROR"
    if "flow" in error_msg or "direction" in error_msg:
        return "FLOW_MISREAD"
    if "timing" in error_msg or "delay" in error_msg:
        return "TIMING_ERROR"
    if "confidence" in error_msg or "high" in error_msg:
        return "OVERCONFIDENCE"
    return "UNKNOWN"

def enrich_failure(outcome, context):
    """실패 결과에 대해 컨텍스트를 기반으로 원인 보강"""
    if outcome.get("result") == "FAIL":
        if context.get("gemini_used") and context.get("logic_error"):
            return "GEMINI_REASONING_ERROR"
        elif context.get("flow_miss"):
            return "FLOW_MISREAD"
        elif context.get("is_late"):
            return "TIMING_ERROR"
        elif outcome.get("confidence", 0) > 0.8:
            return "OVERCONFIDENCE"
        else:
            return "UNKNOWN"
    return None
