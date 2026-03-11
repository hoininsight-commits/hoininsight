from typing import Dict, Any, List

class FollowUpEngine:
    """
    IS-37: FOLLOW_UP_ENGINE
    Decides what should be talked about next based on what was said today.
    """

    UNRESOLVED_DIMENSIONS = {
        "POLICY": ["정책 이행 여부 점검", "집행 리스크 모니터링", "현장 피드백"],
        "EARNINGS": ["실적 컨펌", "가이던스 달성률", "어닝 서프라이즈 후폭풍"],
        "CAPITAL_FLOW": ["자본 이동 완결성", "추가 유동성 유입", "공급망 반응"],
        "TECHNOLOGY": ["수율 확보 여부", "양산 일정 지연 리스크", "경쟁사 대응"]
    }

    TIMING_MAP = {
        "IMMEDIATE": "즉시 (24~48시간)",
        "SHORT_TERM": "단기 (1~2주)",
        "EVENT_BASED": "이벤트 기반 (실적/발표/인도)"
    }

    def plan_follow_ups(self, data: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Generates 1~3 follow-up topic recommendations.
        """
        status = data.get("status", "HOLD")
        if status == "SILENT":
            return []

        # Logic to identify trigger type (heuristic)
        content = (data.get("raw_content") or "").lower()
        trigger_type = "CAPITAL_FLOW" # Default
        if "금리" in content or "정책" in content or "정부" in content:
            trigger_type = "POLICY"
        elif "실적" in content or "수익" in content or "매출" in content:
            trigger_type = "EARNINGS"
        elif "양산" in content or "기술" in content or "공정" in content:
            trigger_type = "TECHNOLOGY"

        dimensions = self.UNRESOLVED_DIMENSIONS.get(trigger_type, self.UNRESOLVED_DIMENSIONS["CAPITAL_FLOW"])
        
        plans = []
        # Generate 1~2 follow-ups based on dimensions
        for dim in dimensions[:2]:
            timing = "SHORT_TERM"
            if "점검" in dim or "모니터링" in dim:
                timing = "IMMEDIATE"
            elif "실적" in dim or "양산" in dim:
                timing = "EVENT_BASED"
            
            plans.append({
                "topic": f"{data.get('title', '오늘의 주제')} 관련 {dim}",
                "timing": self.TIMING_MAP.get(timing, self.TIMING_MAP["SHORT_TERM"]),
                "reason": f"{trigger_type} 차원의 미해결 리스크{(' 및 ' + dim) if dim else ''}를 추적하기 위함입니다."
            })
            
        return plans
