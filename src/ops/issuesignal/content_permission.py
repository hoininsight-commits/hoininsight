import logging
from typing import List, Dict, Any, Tuple

logger = logging.getLogger("ContentPermission")

class ContentPermissionLayer:
    """
    IS-80: Content Permission Layer
    투자 확정(TRUST_LOCKED)과 별개로 발화 가능한 콘텐츠 성격을 분류하고 허가합니다.
    """

    TYPE_DISCLAIMERS = {
        "FACT": "본 내용은 확정된 사실 기반의 정보입니다.",
        "PREVIEW": "본 내용은 예정된 일정 기반의 시장 해석이며, 결과는 달라질 수 있습니다.",
        "STRUCTURE": "본 내용은 시장 구조 해석을 위한 콘텐츠이며, 확정된 투자 판단이 아닙니다.",
        "SCENARIO": "본 내용은 시나리오 기반 해석이며 결과는 상황에 따라 달라질 수 있습니다."
    }

    @staticmethod
    def classify_and_authorize(topic: Dict[str, Any], evidence: List[Dict[str, Any]]) -> Tuple[str, bool, str]:
        """
        토픽의 성격을 분류하고 발화 허가 여부를 결정합니다.
        
        Returns:
            (content_type, permission_granted, disclaimer)
        """
        fact_text = topic.get("fact_text", "").lower()
        has_hard_fact = any(e.get("evidence_grade") == "HARD_FACT" for e in evidence)
        
        # 1. Classification Logic
        content_type = "FACT"
        
        # 키워드 및 증거 기반 분류
        if "회담" in fact_text or "발표" in fact_text or "예정" in fact_text or "일정" in fact_text:
            content_type = "PREVIEW"
        elif "구조" in fact_text or "재편" in fact_text or "이동" in fact_text or "지배" in fact_text:
            content_type = "STRUCTURE"
        elif "시나리오" in fact_text or "경우" in fact_text:
            content_type = "SCENARIO"
        elif not has_hard_fact:
            # 명확한 하드 팩트가 없으면 기본적으로 구조 해석으로 분류
            content_type = "STRUCTURE"
        else:
            content_type = "FACT"

        # 2. Permission Logic (IS-80 Rules)
        # FACT, PREVIEW, STRUCTURE, SCENARIO 모두 즉시 발화 허가 (해석형 콘텐츠 활성화)
        permission_granted = True
        
        # 3. Disclaimer
        disclaimer = ContentPermissionLayer.TYPE_DISCLAIMERS.get(content_type, "본 내용은 시장 해석을 위한 콘텐츠입니다.")

        return content_type, permission_granted, disclaimer

    @staticmethod
    def apply_safety_rules(content_type: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """
        분류별 안전 규칙 적용 (예: 종목 마스킹 등)
        """
        if content_type in ["PREVIEW", "STRUCTURE"]:
            # 종목 도출 금지 (마스킹 또는 제거)
            if "ticker" in details:
                details["ticker"] = "MASKED_FOR_SAFETY"
            if "ticker_path" in details:
                details["ticker_path"] = {}
        
        if content_type == "SCENARIO":
            # 종목 도출 제한
            pass
            
        return details
