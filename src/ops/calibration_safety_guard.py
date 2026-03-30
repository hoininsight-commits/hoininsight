import json
from pathlib import Path
from datetime import datetime

# Parameter Bounds (Min/Max to prevent runaway values)
PARAM_LIMITS = {
    "solver_pool_size": {
        "min": 3,
        "max": 10
    },
    "solver_weight": {
        "min": 0.5,
        "max": 2.0
    },
    "demand_weight": {
        "min": 0.3,
        "max": 1.5
    },
    "timing_threshold": {
        "min": 0.2,
        "max": 0.8
    }
}

def apply_limits(param, new_value):
    """Clamps a parameter to its predefined min/max boundaries."""
    limits = PARAM_LIMITS.get(param)
    if not limits:
        return new_value
    return round(max(limits["min"], min(limits["max"], new_value)), 2)

def is_duplicate_action(action, log):
    """Checks if the proposed action is already present in the recent execution log."""
    if not log:
        return False
        
    # Check the last 5 entries to prevent short-term thrashing
    recent_entries = log[-5:]
    for entry in recent_entries:
        if entry.get("action") == action.get("action") and \
           entry.get("target") == action.get("target"):
            return True
    return False

def create_snapshot(params):
    """Creates a timestamped snapshot of the current engine parameters."""
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "params": params
    }

def rollback(project_root, snapshot):
    """Restores engine parameters from a given snapshot."""
    param_path = Path(project_root) / "data" / "ops" / "engine_parameters.json"
    with open(param_path, "w", encoding="utf-8") as f:
        json.dump(snapshot["params"], f, indent=2, ensure_ascii=False)
    print(f"[SafetyGuard] 🔄 Rollback executed from snapshot: {snapshot['timestamp']}")

def validate_calibration_effect(before_metrics, after_metrics):
    """
    Performance Gate: Accept calibration only if it doesn't degrade key metrics.
    Currently focuses on 'alignment'.
    """
    b_align = before_metrics.get("alignment", 0)
    a_align = after_metrics.get("alignment", 0)
    
    if a_align < b_align:
        print(f"[SafetyGuard] ❌ Rejected: Performance degraded ({b_align} -> {a_align})")
        return "REJECT"
    
    print(f"[SafetyGuard] ✅ Accepted: Performance maintained or improved ({b_align} -> {a_align})")
    return "ACCEPT"
