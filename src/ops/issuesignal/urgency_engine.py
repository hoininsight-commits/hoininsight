import re
from typing import Dict, Any, Optional

class UrgencyEngine:
    """
    IS-34: URGENCY_ENGINE
    Calculates urgency scores and identifies 'too-late' scenarios.
    """

    def __init__(self):
        # Keywords that indicate high urgency or time pressure
        self.URGENCY_KEYWORDS = {
            "time_pressure": [r"deadline", r"마감", r"임박", r"urgent", r"긴급", r"immediately"],
            "capital_commitment": [r"invest", r"investment", r"capital", r"fund", r"투자", r"자금", r"집행"],
            "policy_cutoff": [r"effective", r"starting", r"시행", r"발효", r"final", r"최종"],
        }
        
        # Keywords that indicate info might be priced-in or too late
        self.TOO_LATE_KEYWORDS = [
            r"already priced", r"선반영", r"old news", r"이미 반영", r"done deal", r"이미 종료"
        ]

    def calculate_urgency(self, trigger: Dict[str, Any]) -> int:
        """
        Calculates a score from 0 to 100.
        """
        content = (trigger.get("raw_content") or trigger.get("title") or "").lower()
        score = 30 # Base score for valid triggers
        
        # 1. Time Pressure (40%)
        if any(re.search(p, content) for p in self.URGENCY_KEYWORDS["time_pressure"]):
            score += 30
            
        # 2. Capital Commitment (30%)
        if any(re.search(p, content) for p in self.URGENCY_KEYWORDS["capital_commitment"]):
            score += 20
            
        # 3. Policy Cutoff (20%)
        if any(re.search(p, content) for p in self.URGENCY_KEYWORDS["policy_cutoff"]):
            score += 15
            
        # 4. Impact boost (e.g. Rate hike/cut)
        if "interest rate" in content or "금리" in content:
            score += 10

        return min(100, score)

    def check_too_late(self, trigger: Dict[str, Any]) -> Optional[str]:
        """
        Returns a reason string if it's too late, else None.
        """
        content = (trigger.get("raw_content") or trigger.get("title") or "").lower()
        
        for pattern in self.TOO_LATE_KEYWORDS:
            if re.search(pattern, content):
                return "이미 가격에 반영됨(Priced-in) 또는 인지도 높음"
        
        # Check elapsed time from IS-33
        elapsed_hours = trigger.get("elapsed_hours", 0)
        if elapsed_hours > 36:
            return "트리거 발생 후 36시간 이상 경과하여 정보 가치 하락"
            
        return None
