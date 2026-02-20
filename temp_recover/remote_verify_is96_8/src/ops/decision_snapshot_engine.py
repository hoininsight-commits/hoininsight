from typing import Dict, Any, List
from src.utils.human_language_rewriter import HumanLanguageRewriter

class DecisionSnapshotEngine:
    """
    Step 95: Decision Speed Layer (10-second Summary).
    Generates a concise 3-sentence snapshot for immediate judgment.
    """

    @staticmethod
    def generate(engine_data: Dict[str, Any]) -> Dict[str, str]:
        judgment_stack = engine_data.get("judgment_stack", {})
        narrative_drift = engine_data.get("narrative_drift", {})
        badges = engine_data.get("badges", {})
        
        status = judgment_stack.get("judgment_state", "NEW")
        days = judgment_stack.get("days_active", 1)
        intensity = badges.get("intensity", "FLASH")
        drift_detected = narrative_drift.get("detected", False)
        
        return {
            "summary": DecisionSnapshotEngine._get_main_summary(status, days, drift_detected),
            "why_today": DecisionSnapshotEngine._get_why_today(intensity, status),
            "caution": DecisionSnapshotEngine._get_caution(intensity, drift_detected)
        }

    @staticmethod
    def _get_main_summary(status: str, days: int, drift: bool) -> str:
        if drift:
            return "이 이슈는 기존과는 다른 새로운 관점에서 구조적 변화가 감지되었습니다."
            
        if status == "ESCALATING":
            if days >= 3:
                return f"지난 {days}일간 축적된 구조적 압력이 임계점에 가까워진 상황입니다."
            return "갑자기 발생한 단발성 이벤트가 아니라, 구조적 힘이 실리고 있는 국면입니다."
            
        if status == "SUSTAINED":
            return f"{days}일째 같은 구조가 반복되고 있으며, 아직 추세가 꺾이지 않았습니다."
            
        if status == "DEGRADING":
            return "강력했던 구조적 압력이 정점을 지나 분산되기 시작했습니다."
            
        return "새롭게 포착된 구조적 변동성이며, 초기 확산 단계에 있습니다."

    @staticmethod
    def _get_why_today(intensity: str, status: str) -> str:
        if intensity == "STRIKE":
            return "아직 결과는 나오지 않았지만, 시장은 이미 다음 단계를 가격에 반영할 준비를 마쳤습니다."
        if intensity == "DEEP_HUNT":
            return "겉으로 드러난 뉴스보다, 그 이면에 숨겨진 구조적 맥락이 더 중요한 시점입니다."
        if status == "NEW":
            return "지금 즉시 대응하기보다는, 오늘 하루의 확산 강도를 먼저 확인해야 합니다."
            
        return "오늘 시장이 이 이슈에 대해 가장 명확한 구조적 반응을 보이고 있습니다."

    @staticmethod
    def _get_caution(intensity: str, drift: bool) -> str:
        if drift:
            return "과거의 판단을 그대로 적용하지 말고, 변화된 맥락에 맞춰 대응해야 합니다."
        if intensity == "FLASH":
            return "지금은 결론을 내릴 시점이 아니라, 흐름이 꺾이는 신호만 확인해야 합니다."
        return "단기적인 가격 변동에 휩쓸리지 말고, 구조적 방향성이 유지되는지만 주목하십시오."
