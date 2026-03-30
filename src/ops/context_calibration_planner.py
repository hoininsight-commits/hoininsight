import json
from pathlib import Path
from datetime import datetime

def split_by_context(logs):
    """Splits logs by Theme Type (CONSTRAINT vs EXPANSION)."""
    result = {
        "CONSTRAINT": [],
        "EXPANSION": []
    }
    for x in logs:
        t = x.get("theme_type", "UNKNOWN")
        if t in result:
            result[t].append(x)
    return result

def aggregate_root_causes(logs):
    """Aggregates FAIL counts from decomposition."""
    counts = {}
    for x in logs:
        decomp = x.get("decomposition", {})
        if isinstance(decomp, dict):
            for k, v in decomp.items():
                if v == "FAIL":
                    counts[k] = counts.get(k, 0) + 1
    return counts

def detect_patterns(context_logs):
    """Detects multi-run failure patterns by context."""
    patterns = {}
    for ctx, logs in context_logs.items():
        total = len(logs)
        root = aggregate_root_causes(logs)
        patterns[ctx] = {
            "total": total,
            "root_causes": root
        }
    return patterns

def generate_calibration(patterns):
    """Generates logic-driven calibration proposals."""
    plan = {
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "proposals": {}
    }
    
    for ctx, data in patterns.items():
        root = data["root_causes"]
        actions = []
        
        # Constraint Strategies
        if ctx == "CONSTRAINT":
            if root.get("industry", 0) > 0:
                actions.append({
                    "action": "EXPAND_SOLVER_POOL",
                    "target": "MentionablesEngine",
                    "reason": f"Industry failure detected {root['industry']} times (Solver Mismatch)"
                })
            if root.get("stock", 0) > 0:
                actions.append({
                    "action": "REWEIGHT_SOLVER_PRIORITY",
                    "target": "SelectionCalibrationLayer",
                    "reason": f"Stock failure detected {root['stock']} times (Realized return failure)"
                })
        
        # Expansion Strategies
        elif ctx == "EXPANSION":
            if root.get("stock", 0) > 0:
                actions.append({
                    "action": "BOOST_DEMAND_SIGNALS",
                    "target": "DemandMapping",
                    "reason": f"Stock failure detected {root['stock']} times (Demand-side gap)"
                })
            if root.get("timing", 0) > 0:
                actions.append({
                    "action": "ADJUST_TIMING_THRESHOLD",
                    "target": "TimingLayer",
                    "reason": f"Timing failure detected {root['timing']} times"
                })
        
        plan["proposals"][ctx] = actions
    
    return plan
