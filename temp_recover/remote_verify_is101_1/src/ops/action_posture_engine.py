from typing import Dict, Any

class ActionPostureEngine:
    """
    Step 96: Action Posture Layer.
    Determines the operator's required stance (OBSERVE, MONITOR, PREPARE, STAND_BY)
    based on technical escalation levels and judgment continuity.
    """

    @staticmethod
    def determine(engine_data: Dict[str, Any]) -> Dict[str, str]:
        judgment_stack = engine_data.get("judgment_stack", {})
        narrative_drift = engine_data.get("narrative_drift", {})
        badges = engine_data.get("badges", {})
        
        # 1. Extract Factors
        status = judgment_stack.get("judgment_state", "NEW")
        days = judgment_stack.get("days_active", 1)
        intensity = badges.get("intensity", "FLASH")
        drift_detected = narrative_drift.get("detected", False)
        
        # 2. Calculate Escalation Level
        esc_level = ActionPostureEngine._calculate_escalation_level(status, intensity, drift_detected)
        
        # 3. Determine Posture
        posture = ActionPostureEngine._determine_posture(esc_level, days, intensity, drift_detected)
        
        # 4. Generate Human Output
        return ActionPostureEngine._generate_output(posture)

    @staticmethod
    def _calculate_escalation_level(status: str, intensity: str, drift: bool) -> int:
        level = 1
        
        if status == "SUSTAINED":
            level = 2
        elif status == "ESCALATING":
            if intensity == "STRIKE":
                level = 3
            elif intensity == "DEEP_HUNT":
                level = 4
            else:
                level = 2
        
        # Narrative Drift adds complexity/risk
        if drift:
            level = min(level + 1, 4)
            
        return level

    @staticmethod
    def _determine_posture(level: int, days: int, intensity: str, drift: bool) -> str:
        # Priority Check (Reverse Order)
        
        # STAND_BY: High Level + Deep Hunt + Time Proven
        if level >= 4 and intensity == "DEEP_HUNT" and days >= 3:
            return "STAND_BY"
            
        # PREPARE: Mid-High Level + (Drift OR Strike)
        if level >= 3 and (drift or intensity == "STRIKE"):
            return "PREPARE"
            
        # MONITOR: Sustained or Escalating but early
        if level >= 2 and days >= 2:
            return "MONITOR"
            
        # Default: OBSERVE
        return "OBSERVE"

    @staticmethod
    def _generate_output(posture: str) -> Dict[str, str]:
        responses = {
            "OBSERVE": {
                "headline": "현재 시장에 대한 적절한 자세: OBSERVE (관찰)",
                "description": "지금은 상황을 지켜보는 단계입니다. 구조가 아직 명확하게 드러나지 않았으므로 성급한 판단을 유보하십시오."
            },
            "MONITOR": {
                "headline": "현재 시장에 대한 적절한 자세: MONITOR (감시)",
                "description": "변화가 이어지고 있어 지속적인 관찰이 필요합니다. 판단을 서두르기에는 이른 구간이니 흐름을 놓치지 마십시오."
            },
            "PREPARE": {
                "headline": "현재 시장에 대한 적절한 자세: PREPARE (대비)",
                "description": "환경 변화에 대비할 필요가 있습니다. 다음 전개를 염두에 두고 시나리오를 점검할 시점입니다."
            },
            "STAND_BY": {
                "headline": "현재 시장에 대한 적절한 자세: STAND_BY (긴장)",
                "description": "구조적 압력이 실제로 작동 중입니다. 판단 전환 가능성이 높아진 구간이니 즉각적으로 대응할 준비를 하십시오."
            }
        }
        return dict(responses.get(posture, responses["OBSERVE"]), posture=posture)
