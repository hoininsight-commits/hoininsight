from pathlib import Path
from typing import Dict, Any

class PreTriggerLayer:
    """
    (IS-11) Detects "about-to-trigger" states and assigns PRE_TRIGGER status.
    """
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        
    def classify_state(self, signal: Dict[str, Any]) -> str:
        """
        Classifies signal into PRE_TRIGGER, READY, HOLD, or REJECT.
        """
        content = signal.get("content", "").lower()
        importance = signal.get("importance", "LOW")
        
        # 1. READY Conditions (Immediate impact)
        if "official" in content or "signed" in content or importance == "CRITICAL":
            return "READY"
            
        # 2. PRE_TRIGGER Conditions (Unavoidable precursor)
        pre_trigger_keywords = ["committee", "passed", "converge", "upcoming", "scheduled"]
        if any(kw in content for kw in pre_trigger_keywords) and importance == "HIGH":
            return "PRE_TRIGGER"
            
        # 3. HOLD / REJECT
        if "potential" in content or "rumor" in content:
            return "HOLD"
            
        return "REJECT"

    def generate_watch_narrative(self, signal: Dict[str, Any]) -> str:
        """
        Generates narrative for PRE_TRIGGER signals.
        """
        return f"WATCH ALERT: '{signal.get('content')}' is approaching a structural threshold. No tickers selected yet, but capital movement convergence is expected soon."
