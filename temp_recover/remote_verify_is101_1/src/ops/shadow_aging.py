from datetime import datetime, timedelta
from typing import Dict, Any

class AGING_ENUM:
    FRESH = "FRESH"
    STALE = "STALE"
    DECAYING = "DECAYING"
    EXPIRED = "EXPIRED"

class ShadowAgingCalculator:
    def calculate_aging(self, first_seen_date: str, run_date: str) -> Dict[str, Any]:
        """
        Calculates aging state and duration.
        Buckets:
        - FRESH: <= 7 days
        - STALE: 8-21 days
        - DECAYING: 22-45 days
        - EXPIRED: > 45 days
        """
        fs_dt = datetime.strptime(first_seen_date, "%Y-%m-%d")
        run_dt = datetime.strptime(run_date, "%Y-%m-%d")
        
        days_diff = (run_dt - fs_dt).days
        
        if days_diff <= 7:
            state = AGING_ENUM.FRESH
        elif days_diff <= 21:
            state = AGING_ENUM.STALE
        elif days_diff <= 45:
            state = AGING_ENUM.DECAYING
        else:
            state = AGING_ENUM.EXPIRED
            
        return {
            "aging_state": state,
            "days_in_shadow": days_diff
        }
