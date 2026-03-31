from typing import Dict, Any, Optional
import random

class NarrativeFramingEngine:
    """
    (IS-84 Extension) Narrative Framing Layer.
    Adds context, urgency, and market psychology context to the opening sentence.
    """
    def __init__(self, base_dir=None):
        self.base_dir = base_dir

    def generate(self, candidate: Dict[str, Any]) -> str:
        """
        Generates a narrative framing sentence based on candidate metadata.
        
        Input Keys:
         - why_now (or reason)
         - content_type (FACT, STRUCTURE, PREVIEW, SCENARIO)
         - is_promoted (boolean, implied by presence in promoted list or explicit flag)
         
        Output:
         - A string sentence (1-2 sentences). Empty if no criteria met.
        """
        why_now = candidate.get("why_now") or candidate.get("reason", "")
        content_type = candidate.get("content_type", "FACT")
        # Check if it's promoted or high priority (can come from 'status' or explicit flag)
        is_promoted = candidate.get("status") in ["EDITORIAL_CANDIDATE", "TRUST_LOCKED"]
        
        # Rule 1: Must have WHY-NOW or be promoted or be non-FACT type
        if not (why_now or is_promoted or content_type != "FACT"):
            return ""

        # Pool of templates based on Type/Psychology
        # Randomized slightly to reduce repetition if run multiple times, 
        # but deterministic if we want consistency (will stick to simple rules for now)
        
        if content_type == "STRUCTURE":
            return "숫자는 조용하지만, 시장 구조는 이미 방향을 틀었습니다."
        elif content_type == "PREVIEW":
            return "지금은 결과가 아니라, 원인이 처음 드러난 시점입니다."
        elif content_type == "SCENARIO":
            return "시장은 이미 움직였지만, 대부분은 아직 진짜 이유를 이해하지 못하고 있습니다."
        
        # Fallback for promoted items (Watchlist -> Editorial)
        if is_promoted:
            return "이 이슈를 단순히 단기 뉴스로 소비해서는 안 되는 이유가 있습니다."
            
        # Generic Why-Now based
        if why_now:
             return "지금 시장이 이 이슈에 반응하는 것은 우연이 아닙니다."

        return ""
