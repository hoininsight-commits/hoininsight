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

METRIC_WEIGHTS = {
    "avg_return": 0.5,
    "hit_ratio": 0.3,
    "alignment": 0.2
}

HARD_CONSTRAINTS = {
    "avg_return": -0.3,   # Max allowable drop
    "hit_ratio": -0.2
}

def calculate_weighted_score(before, after):
    """Calculates a weighted performance delta score."""
    score = 0
    details = {}
    for metric, weight in METRIC_WEIGHTS.items():
        b = before.get(metric, 0)
        a = after.get(metric, 0)
        delta = a - b
        weighted = delta * weight
        score += weighted
        details[metric] = {
            "before": b,
            "after": a,
            "delta": round(delta, 3),
            "weighted": round(weighted, 3)
        }
    return round(score, 3), details

def check_hard_constraints(before, after):
    """Detects if any metric drop exceeds the absolute safety floor."""
    violations = []
    for metric, limit in HARD_CONSTRAINTS.items():
        delta = after.get(metric, 0) - before.get(metric, 0)
        if delta < limit:
            violations.append(f"{metric.upper()} ({round(delta, 3)} < {limit})")
    return violations

MIN_SCORE_THRESHOLD = 0.05
MIN_DELTA = 0.01
MAX_CONSECUTIVE_CALIBRATION = 3
COOLDOWN_PERIOD = 2  # Not used directly in check_cooldown but part of the rule

def is_noise_change(details):
    """Returns True if all metric changes are below the noise threshold."""
    for metric, d in details.items():
        if abs(d.get("delta", 0)) > MIN_DELTA:
            return False
    return True

def check_cooldown(log):
    """
    Returns True if the engine should enter cooldown.
    Rule: If last MAX_CONSECUTIVE_CALIBRATION were all 'ACCEPT', enter cooldown.
    """
    if not log or len(log) < MAX_CONSECUTIVE_CALIBRATION:
        return False
    
    # Check the last N entries
    recent = log[-MAX_CONSECUTIVE_CALIBRATION:]
    if all(entry.get("status") == "ACCEPT" for entry in recent):
        return True
    
    return False

def validate_stability(before, after, details, log):
    """
    Evaluates the stability of the proposed calibration.
    1. Rejects Noise (Micro-changes).
    2. Rejects Low-Impact Improvements (< MIN_SCORE_THRESHOLD).
    3. Enforces Cooldown (Prevents drift).
    """
    # 1. Noise Filter
    if is_noise_change(details):
        print("[SafetyGuard] ⚠️ REJECTED: NOISE (Changes too small to warrant calibration)")
        return {"status": "REJECT", "reason": "NOISE"}

    # 2. Score Threshold
    # details['score'] or recalculate
    score, _ = calculate_weighted_score(before, after)
    if score < MIN_SCORE_THRESHOLD:
        print(f"[SafetyGuard] ⚠️ REJECTED: LOW_SCORE ({score} < {MIN_SCORE_THRESHOLD})")
        return {"status": "REJECT", "reason": "LOW_SCORE", "score": score}

    # 3. Cooldown Check
    if check_cooldown(log):
        print(f"[SafetyGuard] 🧊 REJECTED: COOLDOWN (Limit of {MAX_CONSECUTIVE_CALIBRATION} consecutive calibrations reached)")
        return {"status": "REJECT", "reason": "COOLDOWN"}

    return {"status": "PASS"}

def validate_final(before, after, log=None):
    """
    Final Performance Gate:
    1. Check Hard Constraints.
    2. Check Stability (Noise, Score, Cooldown).
    3. Evaluate Weighted Score.
    """
    # 1. Hard Constraints
    violations = check_hard_constraints(before, after)
    if violations:
        print(f"[SafetyGuard] 🚫 REJECTED: Hard Constraint Violation - {', '.join(violations)}")
        return {
            "status": "REJECT",
            "reason": "HARD_CONSTRAINT",
            "violations": violations,
            "score": 0
        }
    
    score, details = calculate_weighted_score(before, after)
    
    # 2. Stability Check (If log provided)
    if log is not None:
        stability_result = validate_stability(before, after, details, log)
        if stability_result["status"] == "REJECT":
            return {
                "status": "REJECT",
                "reason": stability_result["reason"],
                "score": score,
                "details": details
            }
    
    # 3. Weighted Score final Decision
    if score > 0:
        print(f"[SafetyGuard] ✅ ACCEPTED: Weighted Score {score} > 0. Net improvement detected.")
        return {
            "status": "ACCEPT",
            "score": score,
            "details": details
        }
    else:
        print(f"[SafetyGuard] ❌ REJECTED: Weighted Score {score} <= 0. No net benefit.")
        return {
            "status": "REJECT",
            "reason": "NEGATIVE_SCORE",
            "score": score,
            "details": details
        }

def validate_multi_metric(before, after):
    """Deprecated: Replaced by validate_final. Legacy wrapper for compatibility."""
    return validate_final(before, after)
