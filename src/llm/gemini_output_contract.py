# src/llm/gemini_output_contract.py
# HOIN Insight Gemini Control Layer - Output Contract Validation

REQUIRED_OUTPUT_FIELDS = [
    "topic_core_claim",
    "why_now",
    "surface_fact",
    "structural_truth",
    "capital_flow",
    "primary_beneficiary",
    "risk_kill_switch",
    "one_line_summary"
]

def validate_gemini_output(data, agent: str = "UNKNOWN") -> bool:
    """Gemini 응답 데이터가 필수 계약 필드를 포함하고 있는지 검증 (v1.0)"""
    
    # 1. 리스트 형태 (DETECTOR 등) 처리
    if isinstance(data, list):
        if len(data) == 0:
            return False
        # 리스트 내 개별 항목 검증 (간소화)
        sample = data[0]
        if isinstance(sample, dict) and ("topic" in sample or "event" in sample):
            return True
        return False

    # 2. 딕셔너리 형태 처리
    if not isinstance(data, dict):
        return False

    # 3. 에이전트별 규약 (v1.0)
    if agent == "DETECTOR":
        return "topic" in data or "candidates" in data or isinstance(data, list)
    
    if agent == "TOPIC_EVALUATOR":
        return "topic_fit_score" in data and "topic_decision" in data and "why_now_summary" in data
    
    # ANALYST, WRITER 등 핵심 의사결정 레이어 규약
    essential = ["topic_core_claim", "one_line_summary"]
    for f in essential:
        if f not in data:
            return False

    return True
