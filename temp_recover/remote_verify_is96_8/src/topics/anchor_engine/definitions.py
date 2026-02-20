from typing import Dict, List, Any

# 1. BASELINE_SIGNALS_v1.0 (헌법)
BASELINE_SIGNALS = {
    "volatility_surge": {
        "description": "Z-Score > 2.0 or 3-day change > 15%",
        "threshold_z": 2.0,
        "threshold_pct_3d": 0.15
    },
    "correlation_break": {
        "description": "Rolling correlation flip (positive to negative) > 0.5 diff",
        "threshold_diff": 0.5
    },
    "level_breakout": {
        "description": "New 52-week High/Low",
        "check": "is_52w_high_or_low"
    }
}

# 3. ANOMALY_DETECTION_LOGIC_v1.11 (단일 고정본)
ANOMALY_LOGIC_MAP = {
    "Monetary Tightening": {
        "condition": "Rate_Up AND (Equity_Down OR VIX_Up)",
        "why_now": "Capital-driven / Macro Constraint"
    },
    "Risk Off": {
        "condition": "Equity_Down AND Bond_Yield_Down AND Gold_Up",
        "why_now": "Sentiment-driven / Safety Seek"
    },
    "Sector Rotation": {
        "condition": "Index_Flat AND Sector_Divergence_High",
        "why_now": "Structural-driven / Capital Flow"
    },
    "Policy Shock": {
        "condition": "Event_Match AND Market_Inverse_Move",
        "why_now": "Political-driven / Expectation Mismatch"
    }
}

# Why Now Types
WHY_NOW_TYPES = [
    "Schedule-driven",
    "State-driven",
    "Political-driven",
    "Structural-driven",
    "Capital-driven",
    "Hybrid-driven"
]
