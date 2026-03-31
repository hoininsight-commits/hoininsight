import json
from pathlib import Path

def run_post_structural_validation(project_root):
    """
    [STEP-H-VERIFY] Audits performance before and after the structural fix.
    """
    project_root = Path(project_root)
    tracking_path = project_root / "data" / "ops" / "validation_tracking.json"
    ledger_path = project_root / "data" / "ops" / "outcome_ledger.json"
    
    if not tracking_path.exists():
        return {"status": "ERROR", "message": "Tracking data missing"}
        
    with open(tracking_path, "r", encoding="utf-8") as f:
        tracking = json.load(f)
        
    # 1. Split Before / After
    before = [e for e in tracking if e.get("phase") == "pre_structural"]
    after = [e for e in tracking if e.get("phase") == "post_structural"]
    
    # 2. Compute Metrics
    def get_metrics(data):
        if not data: return {"avg_alignment": 0, "avg_hit_ratio": 0, "failure_rate": 0, "count": 0}
        return {
            "avg_alignment": round(sum(e["outcome_alignment"] for e in data) / len(data), 2),
            "avg_hit_ratio": round(sum(e["hit_ratio"] for e in data) / len(data), 2),
            "failure_rate": round(sum(1 for e in data if e["failure_type"] != "SUCCESS") / len(data), 2),
            "count": len(data)
        }
        
    metrics_before = get_metrics(before)
    metrics_after = get_metrics(after)
    
    # 3. Solver Performance (from Ledger)
    solver_success_rate = 0.0
    if ledger_path.exists():
        with open(ledger_path, "r", encoding="utf-8") as f:
            ledger = json.load(f)
        
        solver_total = 0
        solver_hits = 0
        for entry in ledger:
            # Look for solver_direct stocks in impact_chain if present
            # For verification, we check if the run was successful when solver was present
            impact_chain = entry.get("impact_chain", [])
            has_solver = any(s.get("directness") == "solver_direct" for s in impact_chain)
            if has_solver:
                solver_total += 1
                if entry.get("hit_ratio", 0) > 0:
                    solver_hits += 1
        
        if solver_total > 0:
            solver_success_rate = round(solver_hits / solver_total, 2)

    # 4. Final Final Status
    status = "FAIL"
    if metrics_after["avg_alignment"] >= 0.5 and metrics_after["avg_hit_ratio"] >= 0.3:
        status = "PASS"
    if metrics_after["avg_alignment"] >= 0.7 and metrics_after["avg_hit_ratio"] >= 0.5:
        status = "STRONG PASS"

    results = {
        "status": status,
        "metrics": {
            "before": metrics_before,
            "after": metrics_after,
            "improvement": {
                "alignment": round(metrics_after["avg_alignment"] - metrics_before["avg_alignment"], 2),
                "hit_ratio": round(metrics_after["avg_hit_ratio"] - metrics_before["avg_hit_ratio"], 2)
            }
        },
        "solver_performance": {
            "success_rate": solver_success_rate
        },
        "recommendation": "Ready for production" if status in ["PASS", "STRONG PASS"] else "Further calibration required"
    }
    
    # Save results
    save_path = project_root / "data" / "ops" / "post_structural_validation.json"
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
        
    return results
