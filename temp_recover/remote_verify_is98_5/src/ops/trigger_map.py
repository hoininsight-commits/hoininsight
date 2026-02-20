from typing import Dict, List, Any

class TRIGGER_ENUM:
    NUMERIC_EVIDENCE_APPEAR = "NUMERIC_EVIDENCE_APPEAR"
    SUPPORTING_ANOMALY_DETECTED = "SUPPORTING_ANOMALY_DETECTED"
    FACT_CONFIRMATION_PUBLISHED = "FACT_CONFIRMATION_PUBLISHED"
    TIME_WINDOW_OPENED = "TIME_WINDOW_OPENED"
    CONTRADICTION_CLEARED = "CONTRADICTION_CLEARED"

class TriggerMapBuilder:
    def build_trigger_map(self, shadow_cand: Dict[str, Any]) -> Dict[str, Any]:
        """
        Builds a readiness trigger map for a shadow candidate.
        Input matches shadow_candidates.json entry + quality_codes if available.
        """
        failure_codes = shadow_cand.get("failure_codes", [])
        lane = shadow_cand.get("lane", "ANOMALY")
        impact_window = shadow_cand.get("impact_window", "MID")
        
        missing_triggers = []
        source_hints = []
        earliest_recheck = "AFTER_7D" # Default
        
        # 1. Map failure codes to triggers
        if "LOW_EVIDENCE" in failure_codes or "PLACEHOLDER_EVIDENCE" in failure_codes:
            missing_triggers.append(TRIGGER_ENUM.NUMERIC_EVIDENCE_APPEAR)
            source_hints.append("on-chain metric" if lane == "ANOMALY" else "earnings release")
            
        if "CONTRADICTION" in (c.upper() for c in failure_codes):
            missing_triggers.append(TRIGGER_ENUM.CONTRADICTION_CLEARED)
            source_hints.append("policy announcement")
            
        # 2. Lane-based triggers
        if lane == "FACT":
            if TRIGGER_ENUM.NUMERIC_EVIDENCE_APPEAR not in missing_triggers:
                missing_triggers.append(TRIGGER_ENUM.FACT_CONFIRMATION_PUBLISHED)
                source_hints.append("macro data")
        else:
            if TRIGGER_ENUM.NUMERIC_EVIDENCE_APPEAR not in missing_triggers:
                missing_triggers.append(TRIGGER_ENUM.SUPPORTING_ANOMALY_DETECTED)
                source_hints.append("anomaly flow")

        # 3. Impact-based recheck
        if impact_window == "NEAR":
            missing_triggers.append(TRIGGER_ENUM.TIME_WINDOW_OPENED)
            earliest_recheck = "WINDOW_OPEN"
        elif impact_window == "IMMEDIATE":
            earliest_recheck = "NEXT_EARNINGS" # Shadow for immediate usually means failure
            
        return {
            "missing_triggers": list(set(missing_triggers)),
            "source_hint": list(set(source_hints)),
            "earliest_recheck": earliest_recheck
        }
