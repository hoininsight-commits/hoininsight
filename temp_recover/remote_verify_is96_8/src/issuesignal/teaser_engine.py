from typing import Dict, Any, List, Optional
import random

class NextSignalTeaserEngine:
    """
    IS-40: NEXT_SIGNAL_TEASER_ENGINE
    Generates a single-sentence teaser for the next topic in the hierarchy.
    """

    def generate_teaser(self, membership_queue: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Creates a teaser from the top item of the membership queue.
        """
        if not membership_queue:
            return None

        top_item = membership_queue[0]
        timing = top_item.get("expected_timing", "조만간")
        # Extract base timing word
        timing_word = "이번 주"
        if "단기" in timing: timing_word = "이번 주"
        elif "즉시" in timing: timing_word = "내일"
        elif "이벤트" in timing: timing_word = "다음 공식 일정"

        # Observation point (take first)
        points = top_item.get("observation_points", ["데이터의 구조적 변곡점"])
        point = points[0] if points else "변동성의 본질"

        teaser_sentence = self._build_sentence(timing_word, point)
        
        return {
            "sentence": teaser_sentence,
            "timing": timing,
            "audience": "멤버십" if "멤버십" in str(top_item.get("status", "")) else "공개"
        }

    def _build_sentence(self, timing: str, point: str) -> str:
        """Constructs a single authoritative sentence."""
        templates = [
            f"다음 발화는 {timing} {point} 사실이 데이터로 증명되는 지점에서 시작된다.",
            f"자본의 다음 강제적 이동은 {timing} {point} 변수가 확인되는 순간 결정된다.",
            f"우리는 {timing} {point} 지점을 주시하며 다음 신호의 필연성을 받아들여야 한다."
        ]
        # For consistency, we can pick based on point content or just fixed
        return templates[0]

    def _enforce_teaser_rules(self, sentence: str) -> str:
        """Heuristic check to ensure voice lock and one sentence."""
        # Force all soft endings to declarative
        # IS-39 style enforcement
        sentence = sentence.replace("가능성이 있습니다", "이미 결정됐다")
        sentence = sentence.replace("가능성이 있다", "이미 결정됐다")
        sentence = sentence.replace("전망됩니다", "필연이다")
        sentence = sentence.replace("일 수 있습니다", "해야 한다")
        
        # Split by period and take first if multiple
        parts = sentence.split(".")
        clean = parts[0].strip()
        if not clean.endswith("."):
            clean += "."
        
        return clean
