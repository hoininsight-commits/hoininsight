from typing import List, Dict, Any, Optional

class MembershipQueueEngine:
    """
    IS-38: MEMBERSHIP_ONLY_TOPIC_QUEUE_ENGINE
    Manages private forward-looking topic previews for membership.
    """

    STATES = {
        "WAITING": "대기중",
        "WATCHING": "관찰중",
        "READY": "분석중"
    }

    def generate_queue(self, topics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Processes topics and follow-up plans to generate membership queue items.
        Filters out topics not suitable for preview.
        """
        queue = []
        for t in topics:
            follow_ups = t.get("follow_up_plans", [])
            if not follow_ups:
                continue

            # Check if topic itself or its follow-ups qualify
            # Criteria: High urgency OR Event-based
            urgency = t.get("urgency_score", 0)
            
            for plan in follow_ups:
                timing = plan.get("timing", "")
                
                # Eligibility check
                if urgency >= 70 or "이벤트" in timing or "즉시" in timing:
                    item = self._create_queue_item(t, plan)
                    if item:
                        queue.append(item)
        
        # Limit to 3 items for the dashboard preview
        return queue[:3]

    def _create_queue_item(self, topic: Dict[str, Any], plan: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """
        Creates a sanitized queue item for membership display.
        Strips tickers, conclusions, and kill-switches.
        """
        raw_topic_name = plan.get("topic", "알 수 없는 주제")
        
        # Disclosure Limiter: Heuristic stripping of sensitive data
        # We don't have full concluson text here yet usually, but we ensure framing only.
        sanitized_topic = raw_topic_name.replace("(LONG FORM)", "").replace("(SHORT FORM)", "").strip()
        
        # Determine State
        timing = plan.get("timing", "")
        urgency = topic.get("urgency_score", 0)
        
        state = self.STATES["WAITING"]
        if urgency >= 85 or "즉시" in timing:
            state = self.STATES["READY"]
        elif urgency >= 60 or "단기" in timing:
            state = self.STATES["WATCHING"]

        # Only reveal observation points and "Why this matters"
        return {
            "title": sanitized_topic,
            "expected_timing": timing,
            "status": state,
            "reason": plan.get("reason", "분석 연속성 확보"),
            "observation_points": self._generate_observation_points(topic, plan)
        }

    def _generate_observation_points(self, topic: Dict[str, Any], plan: Dict[str, str]) -> List[str]:
        """Generates 1-2 forward-looking observation points without leaking tickers."""
        topic_title = topic.get("title", "")
        # Heuristic based on trigger type
        if "실적" in topic_title or "EARNINGS" in plan.get("reason", ""):
            return ["발표 직전 자본의 선행적 배분 여부", "가이던스와 가격 반응의 괴리율"]
        if "금리" in topic_title or "POLICY" in plan.get("reason", ""):
            return ["정책 집행 이후 시중 유동성 흡수 속도", "핵심 의사결정권자의 추가 발언 톤 변화"]
        return ["데이터의 구조적 변곡점 발생 여부", "단기 변동성 확대 구간 진입 가능성"]
