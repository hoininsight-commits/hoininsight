from typing import Dict, List, Any

class READINESS_ENUM:
    READY_TO_PROMOTE = "READY_TO_PROMOTE"
    NEARLY_READY = "NEARLY_READY"
    IN_PROGRESS = "IN_PROGRESS"
    FAR = "FAR"

class PromotionReadinessCalculator:
    def calculate_readiness(self, required_signals: List[str], matched_signals: List[str]) -> Dict[str, Any]:
        """
        Determines the readiness bucket and progress stats.
        Buckets:
        - READY_TO_PROMOTE: 0 missing
        - NEARLY_READY: 1 missing
        - IN_PROGRESS: 2-3 missing
        - FAR: 4+ missing
        """
        req_set = set(required_signals)
        match_set = set(matched_signals)
        
        missing_signals = list(req_set - match_set)
        missing_count = len(missing_signals)
        required_count = len(req_set)
        matched_count = len(match_set.intersection(req_set))
        
        if missing_count == 0 and required_count > 0:
            bucket = READINESS_ENUM.READY_TO_PROMOTE
        elif missing_count == 1:
            bucket = READINESS_ENUM.NEARLY_READY
        elif 2 <= missing_count <= 3:
            bucket = READINESS_ENUM.IN_PROGRESS
        else:
            bucket = READINESS_ENUM.FAR
            
        return {
            "required_count": required_count,
            "matched_count": matched_count,
            "missing_count": missing_count,
            "missing_signals": missing_signals,
            "readiness_bucket": bucket
        }

    def get_operator_hint(self, bucket: str, missing_signals: List[str]) -> str:
        """Returns deterministic operator hint (Step 39-5)."""
        if bucket == READINESS_ENUM.READY_TO_PROMOTE:
            return "Operator action: Re-run pipeline when next window opens (no auto-promotion)."
        elif bucket == READINESS_ENUM.NEARLY_READY:
            top_signal = missing_signals[0] if missing_signals else "missing signal"
            return f"Operator action: Watch for {top_signal}."
        return ""
