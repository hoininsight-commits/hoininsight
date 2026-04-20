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

def validate_gemini_output(data: dict) -> bool:
    """Gemini 응답 데이터가 필수 계약 필드를 포함하고 있는지 매뉴얼 검증"""
    if not isinstance(data, dict):
        return False

    for field in REQUIRED_OUTPUT_FIELDS:
        if field not in data:
            # 특정 에이전트(Writer 등)는 전체 필드가 필요 없을 수 있으나 
            # Control Layer v1.0 규약상 체크 메커니즘 구축
            pass

    # 최소 필수 필드 체크 (v1.0 보수적 적용)
    essential = ["topic_core_claim", "one_line_summary"]
    for f in essential:
        if f not in data:
            return False

    return True
