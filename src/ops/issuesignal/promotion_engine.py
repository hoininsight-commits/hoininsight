from pathlib import Path
from typing import Dict, Any, List, Optional
import re

class PromotionEngine:
    """
    (IS-22) Decides when to promote a PRE_TRIGGER state to a TRIGGER state.
    """
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir

    def evaluate_promotion(self, current_pre: Dict[str, Any], new_signals: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Monitors new signals to see if they trigger promotion for a PRE_TRIGGER event.
        Returns a promoted state dict if successful, else None.
        """
        conditions_met = set()

        # 1. Official Action detection
        if self._check_official_action(new_signals):
            conditions_met.add("OFFICIAL_ACTION")

        # 2. Capital Commitment detection
        if self._check_capital_commitment(new_signals):
            conditions_met.add("CAPITAL_COMMITMENT")

        # 3. Time Collapse detection
        if self._check_time_collapse(new_signals):
            conditions_met.add("TIME_COLLAPSE")

        # 4. Market Acknowledgment detection
        if self._check_market_acknowledgment(new_signals):
            conditions_met.add("MARKET_ACKNOWLEDGMENT")

        # Threshold: At least 2 conditions
        if len(conditions_met) >= 2:
            # Final check: Ensure no forbidden signals alone are driving this
            if self._is_forbidden(new_signals):
                return None
            return self._promote(current_pre)
        
        return None

    def _is_forbidden(self, signals: List[Dict[str, Any]]) -> bool:
        forbidden_keywords = ["rumor", "anonymous", "source says", "unconfirmed", "unnamed"]
        # If all signals contain forbidden keywords or are weak, deny.
        # But if at least one solid signal exists among others, we might allow it.
        # Strict rule: If ANY signal is a rumor AND we don't have a high-confidence official one, reject.
        for s in signals:
            content = str(s).lower()
            if any(fk in content for fk in forbidden_keywords):
                # If it's a rumor, we need to be very careful. 
                # For this implementation, let's say if ANY signal is explicitly a rumor, 
                # it shouldn't be the basis for promotion unless matched with 3+ solid ones.
                if len(signals) < 3:
                    return True
        return False

    def _check_official_action(self, signals: List[Dict[str, Any]]) -> bool:
        keywords = ["signing", "official", "announcement", "sec", "filing", "gazette", "bill"]
        return any(any(kw in str(s).lower() for kw in keywords) for s in signals)

    def _check_capital_commitment(self, signals: List[Dict[str, Any]]) -> bool:
        keywords = ["capex", "contract", "signed", "order", "canceled", "downpayment"]
        return any(any(kw in str(s).lower() for kw in keywords) for s in signals)

    def _check_time_collapse(self, signals: List[Dict[str, Any]]) -> bool:
        keywords = ["fixed", "deadline", "no delay", "immediate", "effective now"]
        return any(any(kw in str(s).lower() for kw in keywords) for s in signals)

    def _check_market_acknowledgment(self, signals: List[Dict[str, Any]]) -> bool:
        keywords = ["price spike", "limit up", "massive volume", "arbitrage", "distortion"]
        return any(any(kw in str(s).lower() for kw in keywords) for s in signals)

    def _promote(self, pre_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transforms PRE_TRIGGER data into TRIGGER data.
        """
        promoted = pre_data.copy()
        promoted["state"] = "TRIGGER"
        
        # Transition Headline Rule (Immutable)
        # PRE: "아직 [사건]은 터지지 않았지만, [주체]는 이미 [행동]을 해야 하는 상태다."
        # TRIGGER: "오늘 [사건]이 발생했고, [주체]는 더 이상 선택 없이 [행동]을 해야 한다."
        
        event = pre_data.get("event", "[사건]")
        actor = pre_data.get("actor", "[주체]")
        action = pre_data.get("action", "[행동]")
        
        promoted["one_sentence_headline"] = f"오늘 {event}이 발생했고, {actor}는 더 이상 선택 없이 {action}을 해야 한다."
        
        return promoted
