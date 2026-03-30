import json
from pathlib import Path
from datetime import datetime

def decompose_failure(entry):
    """
    Structural failure decomposition based on metrics.
    """
    hit = entry.get("hit_ratio", 0)
    align = entry.get("alignment", 0)

    result = {
        "theme": "OK",
        "industry": "OK",
        "stock": "OK",
        "timing": "OK"
    }

    # Theme 판단
    if align < 0.3:
        result["theme"] = "FAIL"

    # Stock 판단
    if hit < 0.3:
        result["stock"] = "FAIL"

    # Timing 판단
    if 0.3 <= align < 0.6:
        result["timing"] = "FAIL"

    # Industry 판단 (solver mismatch 기준)
    impact_chain = entry.get("impact_chain", [])
    if not impact_chain:
        # Check if we have solver_direct in top_stocks if provided as objects
        top_stocks = entry.get("top_stocks", [])
        if top_stocks and isinstance(top_stocks[0], dict):
             has_solver = any(x.get("directness") == "solver_direct" for x in top_stocks)
        else:
             has_solver = False
        
        if not has_solver:
            result["industry"] = "FAIL"
    else:
        has_solver = any(x.get("directness") == "solver_direct" for x in impact_chain)
        if not has_solver:
            result["industry"] = "FAIL"

    return result

def classify_failure(decomposition):
    """
    Classifies failure type (SUCCESS, SINGLE, MIXED).
    """
    fails = [k for k, v in decomposition.items() if v == "FAIL"]

    if not fails:
        return {
            "type": "SUCCESS",
            "primary": None,
            "secondary": None
        }

    if len(fails) == 1:
        return {
            "type": "SINGLE",
            "primary": fails[0],
            "secondary": None
        }

    return {
        "type": "MIXED",
        "primary": fails[0],
        "secondary": fails[1:]
    }

def build_decomposition_summary(logs):
    """
    Aggregates decomposition stats.
    """
    summary = {
        "total": len(logs),
        "failure_types": {},
        "root_causes": {},
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    for x in logs:
        f = x.get("failure_detail", {}).get("type", "UNKNOWN")
        summary["failure_types"][f] = summary["failure_types"].get(f, 0) + 1

        for k, v in x.get("decomposition", {}).items():
            if v == "FAIL":
                summary["root_causes"][k] = summary["root_causes"].get(k, 0) + 1

    return summary
