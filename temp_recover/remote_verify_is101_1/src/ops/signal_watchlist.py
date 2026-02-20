from typing import Dict, List, Any

class WATCH_SIGNAL_ENUM:
    NUMERIC_EVIDENCE_APPEAR = "NUMERIC_EVIDENCE_APPEAR"
    SUPPORTING_ANOMALY_DETECTED = "SUPPORTING_ANOMALY_DETECTED"
    POLICY_EVENT_TRIGGERED = "POLICY_EVENT_TRIGGERED"
    EARNINGS_RELEASE = "EARNINGS_RELEASE"
    ONCHAIN_CONFIRMATION = "ONCHAIN_CONFIRMATION"
    MACRO_THRESHOLD_CROSSED = "MACRO_THRESHOLD_CROSSED"

class SignalWatchlistBuilder:
    def build_watchlist(self, shadow_cand: Dict[str, Any]) -> Dict[str, Any]:
        """
        Input: Shadow candidate object (including trigger_map)
        Output: Watchlist block
        """
        trigger_map = shadow_cand.get("trigger_map", {})
        missing_triggers = trigger_map.get("missing_triggers", [])
        source_hints = trigger_map.get("source_hint", [])
        
        watch_signals = []
        
        # Mapping Logic based on fixed rules
        if "NUMERIC_EVIDENCE_APPEAR" in missing_triggers:
            watch_signals.append(WATCH_SIGNAL_ENUM.NUMERIC_EVIDENCE_APPEAR)
            
        if "SUPPORTING_ANOMALY_DETECTED" in missing_triggers:
            watch_signals.append(WATCH_SIGNAL_ENUM.SUPPORTING_ANOMALY_DETECTED)
            
        if "FACT_CONFIRMATION_PUBLISHED" in missing_triggers:
            watch_signals.append(WATCH_SIGNAL_ENUM.MACRO_THRESHOLD_CROSSED)
            
        if "CONTRADICTION_CLEARED" in missing_triggers:
            watch_signals.append(WATCH_SIGNAL_ENUM.POLICY_EVENT_TRIGGERED)
            
        if "TIME_WINDOW_OPENED" in missing_triggers:
            # Check source hint for specific event type
            if any("earnings" in s.lower() for s in source_hints):
                watch_signals.append(WATCH_SIGNAL_ENUM.EARNINGS_RELEASE)
            else:
                watch_signals.append(WATCH_SIGNAL_ENUM.POLICY_EVENT_TRIGGERED) # Default fallback

        # Check source hints directly for extra precision
        if any("on-chain" in s.lower() for s in source_hints):
            if WATCH_SIGNAL_ENUM.ONCHAIN_CONFIRMATION not in watch_signals:
                watch_signals.append(WATCH_SIGNAL_ENUM.ONCHAIN_CONFIRMATION)
        
        if any("macro" in s.lower() for s in source_hints):
             if WATCH_SIGNAL_ENUM.MACRO_THRESHOLD_CROSSED not in watch_signals:
                watch_signals.append(WATCH_SIGNAL_ENUM.MACRO_THRESHOLD_CROSSED)

        return {
            "topic_id": shadow_cand.get("topic_id"),
            "watch_signals": list(set(watch_signals)),
            "recheck_window": shadow_cand.get("impact_window", "MID"),
            "aging_state": shadow_cand.get("aging", {}).get("aging_state", "FRESH")
        }
