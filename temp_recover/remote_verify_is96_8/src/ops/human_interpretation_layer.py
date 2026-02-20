import logging
from typing import Dict, Any, List

class HumanInterpretationLayer:
    """
    Step 89: Human Interpretation Layer
    Translates engine results (WHY_NOW, Patterns, Entity States) into 
    operator-friendly natural language explanations.
    """

    FORBIDDEN_WORDS = ["매수", "수익", "투자", "추천", "가격"]

    @staticmethod
    def interpret(engine_data: Dict[str, Any]) -> str:
        """
        Generates a human-friendly narrative summary for the Top-1 Topic.
        Deterministic assembly based on existing structural logic.
        """
        # 1. Extraction
        why_now = engine_data.get("why_now", {})
        badges = engine_data.get("badges", {})
        
        wn_type = why_now.get("type", "Unknown")
        wn_anchor = why_now.get("anchor", "Hidden Pattern")
        intensity = badges.get("intensity", "FLASH")
        rhythm = badges.get("rhythm", "N/A")
        
        # 2. Base Narrative Templates
        # Template mapping for WHY_NOW types
        templates = {
            "Mechanism Activation": "특정 구조적 기제가 활성화되었습니다.",
            "Schedule Pressure": "예정된 구조적 압력이 작동하기 시작했습니다.",
            "Anomaly Detection": "구조적 변칙성이 감지되었습니다.",
            "Trend Escalation": "기존 추세가 구조적으로 가속화되고 있습니다."
        }
        
        base_sentence = templates.get(wn_type, "구조적 정합성이 확보된 시그널이 발생했습니다.")
        
        # 3. Pattern/Rhythm Interpretation
        pattern_desc = ""
        if "STRUCTURE_FLOW" in rhythm:
            pattern_desc = "오늘 이 토픽은 시스템의 구조적 흐름과 동기화된 상태로 확인됩니다."
        elif "STRIKE" in intensity:
            pattern_desc = "지금 즉시 대응이 필요한 핵심적인 전환점으로 식별됩니다."
        elif "DEEP_HUNT" in intensity:
            pattern_desc = "심층적인 구조 변화가 수면 위로 드러나고 있는 시점입니다."
        else:
            pattern_desc = "현재 시점에서의 구조적 유효성이 확보되었습니다."

        # 4. Final Assembly (Deterministic)
        interpretation = f"왜 지금 이 토픽인가\n- {base_sentence}\n- {pattern_desc}"
        
        # 5. Safety Filtering
        for word in HumanInterpretationLayer.FORBIDDEN_WORDS:
            if word in interpretation:
                interpretation = interpretation.replace(word, "[검열된 용어]")
        
        return interpretation

if __name__ == "__main__":
    # Test Data
    mock_data = {
        "why_now": {"type": "Mechanism Activation", "anchor": "Pattern Match"},
        "badges": {"intensity": "STRIKE", "rhythm": "STRUCTURE_FLOW"}
    }
    print(HumanInterpretationLayer.interpret(mock_data))
