import json
from pathlib import Path
from datetime import datetime

def decompose_context_aware(entry):
    """
    Refined failure decomposition based on Theme Type (Constraint/Expansion).
    """
    hit = entry.get("hit_ratio", 0)
    align = entry.get("alignment", 0)
    theme_type = entry.get("theme_type", "UNKNOWN")

    result = {
        "theme": "OK",
        "industry": "OK",
        "stock": "OK",
        "timing": "OK"
    }

    # 1. Theme 판단 (구조 적합성)
    if align < 0.25:
        result["theme"] = "FAIL"

    # 2. Industry 판단 (Context-aware)
    impact_chain = entry.get("impact_chain", [])

    if theme_type == "CONSTRAINT":
        # Constraint themes MUST have solvers
        has_solver = any(x.get("directness") == "solver_direct" for x in impact_chain)
        if not has_solver:
            result["industry"] = "FAIL"

    elif theme_type == "EXPANSION":
        # Expansion themes require demand-side (direct/indirect)
        has_demand = any(x.get("directness") in ["direct", "indirect"] for x in impact_chain)
        if not has_demand:
            result["industry"] = "FAIL"

    # 3. Stock 판단 (Top 3 realized return success)
    top3 = impact_chain[:3]
    if top3:
        # Check if all top 3 failed to realize positive return
        success_count = sum(1 for x in top3 if x.get("realized_return", 0) > 0)
        if success_count == 0:
            result["stock"] = "FAIL"
    else:
        # Fallback for hit_ratio if no realized_return data yet
        if hit < 0.3:
            result["stock"] = "FAIL"

    # 4. Timing 판단 (독립 분리)
    if 0.25 <= align < 0.6:
        result["timing"] = "FAIL"

    return result

def classify_context_failure(decomposition):
    """
    Classifies failure type with priority: theme > industry > stock > timing.
    """
    fails = [k for k, v in decomposition.items() if v == "FAIL"]

    if not fails:
        return {
            "type": "SUCCESS",
            "primary": None,
            "secondary": None
        }

    # Priority sorting
    priority = ["theme", "industry", "stock", "timing"]
    fails_sorted = sorted(fails, key=lambda x: priority.index(x))

    if len(fails_sorted) == 1:
        return {
            "type": "SINGLE",
            "primary": fails_sorted[0],
            "secondary": None
        }

    return {
        "type": "MIXED",
        "primary": fails_sorted[0],
        "secondary": fails_sorted[1:]
    }

def build_context_summary(logs):
    """
    Aggregates decomposition stats with context split.
    """
    summary = {
        "total": len(logs),
        "failure_types": {},
        "root_causes": {},
        "context_split": {
            "CONSTRAINT": 0,
            "EXPANSION": 0,
            "UNKNOWN": 0
        },
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    for x in logs:
        # Context Split
        theme_type = x.get("theme_type", "UNKNOWN")
        summary["context_split"][theme_type] = summary["context_split"].get(theme_type, 0) + 1

        # Failure Types
        f_detail = x.get("failure_detail", {})
        f_type = f_detail.get("type", "UNKNOWN")
        summary["failure_types"][f_type] = summary["failure_types"].get(f_type, 0) + 1

        # Root Causes
        decomp = x.get("decomposition", {})
        if isinstance(decomp, dict):
            for k, v in decomp.items():
                if v == "FAIL":
                    summary["root_causes"][k] = summary["root_causes"].get(k, 0) + 1

    return summary
