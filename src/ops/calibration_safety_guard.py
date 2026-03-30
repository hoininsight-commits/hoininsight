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

def create_snapshot(params, metrics=None):
    """Creates a timestamped snapshot of the current engine parameters and metrics."""
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "params": params,
        "metrics": metrics or {}
    }

def append_snapshot_history(project_root, snapshot):
    """Appends a snapshot to a persistent history file, keeping only the last 10 entries."""
    history_path = Path(project_root) / "data" / "ops" / "calibration_snapshot_history.json"
    history = []
    if history_path.exists():
        with open(history_path, "r", encoding="utf-8") as f:
            history = json.load(f)
    
    history.append(snapshot)
    # Keep last 10
    history = history[-10:]
    
    with open(history_path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)
    print(f"[SafetyGuard] 📚 Snapshot history updated ({len(history)} entries).")

def update_best_state(project_root, current_snapshot):
    """Updates the Best State file if the current state outperforms the existing best state."""
    best_path = Path(project_root) / "data" / "ops" / "calibration_best_state.json"
    best_state = None
    if best_path.exists():
        with open(best_path, "r", encoding="utf-8") as f:
            best_state = json.load(f)
            
    is_new_best = False
    if not best_state:
        is_new_best = True
    else:
        # Primary tie-breaker: Average Return
        current_ret = current_snapshot.get("metrics", {}).get("avg_return", 0)
        best_ret = best_state.get("metrics", {}).get("avg_return", 0)
        
        if current_ret > best_ret:
            is_new_best = True
        elif current_ret == best_ret:
            # Secondary: Hit Ratio
            current_hit = current_snapshot.get("metrics", {}).get("hit_ratio", 0)
            best_hit = best_state.get("metrics", {}).get("hit_ratio", 0)
            if current_hit > best_hit:
                is_new_best = True

    if is_new_best:
        with open(best_path, "w", encoding="utf-8") as f:
            json.dump(current_snapshot, f, indent=2, ensure_ascii=False)
        print(f"[SafetyGuard] 🏆 NEW BEST STATE RECORDED: {current_snapshot.get('metrics')}")
    
    return is_new_best

def rollback(project_root, snapshot):
    """Restores engine parameters from a given snapshot."""
    param_path = Path(project_root) / "data" / "ops" / "engine_parameters.json"
    with open(param_path, "w", encoding="utf-8") as f:
        json.dump(snapshot["params"], f, indent=2, ensure_ascii=False)
    print(f"[SafetyGuard] 🔄 Rollback executed from snapshot: {snapshot['timestamp']}")

def validate_multi_metric(before, after):
    """
    Performance Gate: Accept calibration only if it doesn't degrade any key metrics.
    Metrics: alignment, hit_ratio, avg_return.
    """
    metrics = ["alignment", "hit_ratio", "avg_return"]
    reasons = []
    
    for m in metrics:
        b_val = before.get(m, 0)
        a_val = after.get(m, 0)
        if a_val < b_val:
            reasons.append(f"{m.upper()}_DOWN ({b_val} -> {a_val})")
            
    if reasons:
        print(f"[SafetyGuard] ❌ Rejected: {', '.join(reasons)}")
        return {"status": "REJECT", "reasons": reasons}
    
    print(f"[SafetyGuard] ✅ Accepted: All metrics maintained or improved.")
    return {"status": "ACCEPT", "reasons": []}
