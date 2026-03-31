import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from .rules import ROTATION_RULES, RotationRule

class CapitalRotationEngine:
    """
    (IS-57) Deterministic judgment layer for capital rotation.
    Reads macro state, matches rules, and forces topic output.
    """
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        
    def build_macro_state(self, ymd: str) -> Dict[str, str]:
        """
        Constructs the MacroState object from real data inputs.
        For MVP, we use heuristic mapping if full data isn't perfect.
        """
        state = {
            "rate_regime": "NEUTRAL",
            "inflation_regime": "STABLE",
            "liquidity": "NEUTRAL",
            "yield_curve": "NORMAL",
            "risk_sentiment": "NEUTRAL",
            "geopolitics": "STABLE",
            "growth_regime": "MODERATE"
        }
        
        # 1. Yield Curve Logic (10Y - 2Y)
        try:
            # Locate latest files (assuming simple YYYY-MM-DD.jsonl structure or similar)
            # Utilizing logic: if 10Y < 2Y -> INVERTED
            # Mocking the READ for efficiency in this MVP step, but sticking to "Real Data" principle
            # means we should try to read if file exists.
            
            # TODO: Implement actual file reading from data/raw/rates_* 
            # For now, we infer from what we saw in 'latest_market.json' or 'fact_anchors'.
            # If we don't have the numeric spread, we default to NEUTRAL or infer from RSS facts.
            
            # RSS Fact Inference (Smart Fallback)
            fact_path = self.base_dir / "data" / "facts" / f"fact_anchors_{ymd.replace('-', '')}.json"
            if fact_path.exists():
                facts = json.loads(fact_path.read_text(encoding='utf-8'))
                full_text = " ".join([f['fact_text'] for f in facts]).upper()
                
                if "INFLATION" in full_text and ("HIGH" in full_text or "RISE" in full_text):
                    state["inflation_regime"] = "HIGH"
                if "RATE HIKE" in full_text or "TIGHTENING" in full_text:
                     state["rate_regime"] = "TIGHTENING"
                if "RATE CUT" in full_text or "EASING" in full_text:
                     state["rate_regime"] = "EASING_ANTICIPATION"
                if "RECESSION" in full_text or "INVERSION" in full_text:
                     state["yield_curve"] = "INVERTED"
                     state["risk_sentiment"] = "OFF"
                if "WAR" in full_text or "TENSION" in full_text or "ATTACK" in full_text:
                     state["geopolitics"] = "ESCALATION"
                     
        except Exception as e:
            print(f"[RotationEngine] State Build Warning: {e}")
            
        print(f"[RotationEngine] Built Macro State for {ymd}: {state}")
        return state

    def evaluate(self, macro_state: Dict[str, str]) -> Tuple[Optional[RotationRule], str]:
        """
        Evaluates rules against the current state.
        Returns (MatchedRule, Rationale) or (None, Reason).
        Algorithm: Priority-based First Match.
        """
        # Sort rules by priority descending
        sorted_rules = sorted(ROTATION_RULES, key=lambda x: x.priority, reverse=True)
        
        for rule in sorted_rules:
            match = True
            for k, v in rule.required_states.items():
                if macro_state.get(k) != v:
                    match = False
                    break
            
            if match:
                return rule, f"Matched Rule {rule.rule_id}: {rule.condition_desc}"
                
        return None, "No dominant rotation pattern detected."

    def get_rotation_verdict(self, ymd: str) -> Dict[str, Any]:
        """Entry point for integration."""
        state = self.build_macro_state(ymd)
        rule, reason = self.evaluate(state)
        
        if rule:
            return {
                "triggered": True,
                "rule_id": rule.rule_id,
                "target_sector": rule.target_sector,
                "logic_ko": rule.logic_ko,
                "state_snapshot": state,
                "verdict_reason": reason
            }
        else:
             return {
                "triggered": False,
                "rule_id": None,
                "target_sector": "-",
                "logic_ko": "이번 구조에서는 자본 이동이 강제되지 않으므로, 개별 이슈에 집중합니다.",
                "state_snapshot": state,
                "verdict_reason": reason
            }
