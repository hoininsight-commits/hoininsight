from pathlib import Path
from typing import Dict, Any

class KillSwitchEngine:
    """
    (IS-14) Defines objective death conditions for each ticker/thesis.
    """
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        
    def generate_kill_switch(self, ticker: str, trigger_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates exactly one objective kill-switch per ticker.
        """
        category = trigger_context.get("category", "UNKNOWN")
        
        # 1. Rule-based Kill Switch Assignment
        condition = "Universal logic failure"
        monitoring_signal = "General market news"
        
        if category == "POLICY_SCHEDULE":
            condition = "Official policy reversal or bill veto within 48 hours."
            monitoring_signal = "Legislative tracking portal / Official Gazette"
        elif category == "MARKET_STRUCTURE":
            condition = "Supply shock resolves via unexpected capacity release > 20%."
            monitoring_signal = "Industry inventory reports"
        elif category == "CORPORATE_BEHAVIOR":
            condition = "Alternative technology validation from major competitor."
            monitoring_signal = "Peer capex / R&D announcements"
            
        return {
            "ticker": ticker,
            "condition": condition,
            "monitoring_signal": monitoring_signal
        }
