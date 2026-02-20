from typing import Dict, Any, Tuple

class AudienceGateEngine:
    """
    IS-36: AUDIENCE_GATE_ENGINE
    Classifies content packages into PUBLIC, MEMBERSHIP, or INTERNAL_ONLY.
    """

    AUDIENCE_NAMES = {
        "PUBLIC": "공개",
        "MEMBERSHIP": "멤버십",
        "INTERNAL": "내부전용"
    }

    def classify(self, data: Dict[str, Any]) -> Tuple[str, str]:
        """
        Input: topic_data containing urgency, status, proof strength, etc.
        Output: (audience_ko, reason_ko)
        """
        status = data.get("status", "HOLD")
        urgency = data.get("urgency_score", 0)
        output_form = data.get("output_format_ko", "")
        
        # 1. INTERNAL_ONLY (Hard Overrides)
        # If status is HOLD, it must be internal only.
        if status == "HOLD":
            return self.AUDIENCE_NAMES["INTERNAL"], "신호가 보류(HOLD) 상태이므로 내부용으로만 제한합니다."
        
        # If diversity verdict is not PASS (from IS-32)
        if data.get("diversity_verdict") != "PASS":
            return self.AUDIENCE_NAMES["INTERNAL"], "출처 다양성 검증을 통과하지 못해 내부전용으로 분류합니다."

        # If quote verdict is not PASS (from IS-31)
        if data.get("quote_verdict") != "PASS":
            return self.AUDIENCE_NAMES["INTERNAL"], "핵심 인용구 검증이 완료되지 않아 내부전용으로 분류합니다."

        # 2. MEMBERSHIP
        # High urgency Long-form content with strong evidence
        if "대형 영상" in output_form and urgency >= 70:
            return self.AUDIENCE_NAMES["MEMBERSHIP"], "고강도 트리거 및 대형 영상 포맷으로 멤버십 우선 배포 대상으로 분류합니다."

        # 3. PUBLIC
        # High urgency Shorts or Text cards
        if ("숏츠" in output_form or "텍스트" in output_form) and urgency >= 70:
            # Check for sensitive evidence (placeholder check)
            if not data.get("has_sensitive_leaks", False):
                return self.AUDIENCE_NAMES["PUBLIC"], "대중적 전파가 필요한 핵심 데이터로 공개 배포 대상으로 분류합니다."
            else:
                return self.AUDIENCE_NAMES["MEMBERSHIP"], "민감한 데이터 포함 가능성으로 멤버십으로 상향 조정합니다."

        # 4. DEFAULT (Internal)
        return self.AUDIENCE_NAMES["INTERNAL"], "긴급도가 낮거나 전략적 보류가 필요한 정보입니다."
