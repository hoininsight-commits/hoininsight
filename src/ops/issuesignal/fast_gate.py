from datetime import datetime

class FastGate:
    """
    (IS-3) Validates WHY-NOW signal status.
    """
    def evaluate(self, issue: dict) -> str:
        """
        READY / HOLD / REJECT
        """
        # Minimal Stub Logic
        content = issue.get("content", "").lower()
        
        # Rule: 72h window (simulated as True for now)
        
        # Rule: Irreversibility & Logical Sentence
        if "official" in content or "signed" in content or "confirmed" in content:
            return "READY"
        elif "rumor" in content or "suggests" in content:
            return "HOLD"
        
        return "REJECT"
