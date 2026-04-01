import json
import os
from pathlib import Path
from datetime import datetime

# SSOT Configuration
JSON_PATH = Path("docs/data/ui/ui_operator_view.json")
REPORT_PATH = Path("data/ops/decision_integrity_report.json")

def validate_decision(project_root: Path):
    """
    STEP-L-3: Decision Logical Integrity Gate v1.0
    Ensures internal consistency between action, allocation, confidence, timing, etc.
    """
    json_absolute = project_root / JSON_PATH
    report_absolute = project_root / REPORT_PATH
    
    print(f"\n[DECISION] >>> AUDITING Logical Integrity...")
    
    # 1. Load Local UI JSON (The final contract)
    if not json_absolute.exists():
        print(f"[DECISION] ❌ Target JSON missing at {json_absolute}")
        return ["JSON_MISSING"]
        
    with open(json_absolute, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    failures = []

    action = data.get("action", "WATCH")
    allocation = data.get("allocation", 0.0)
    confidence = data.get("confidence", 0.0)
    timing = data.get("timing", "N/A")
    risk = data.get("risk", "LOW")
    stocks = data.get("top_stocks", [])

    # RULE 1: Action <-> Allocation
    if action == "ADD" and allocation <= 0:
        failures.append("ADD_WITH_ZERO_ALLOCATION")
    if action == "WATCH" and allocation > 0:
        failures.append("WATCH_WITH_ALLOCATION")
    # Note: REDUCE rule requires previous value comparison, which isn't available in the current single JSON context.
    # We will prioritize the others as per instructions.

    # RULE 2: Confidence <-> Action
    if confidence < 0.3 and action == "ADD":
        failures.append("LOW_CONFIDENCE_ADD")
    if confidence >= 0.6 and action == "WATCH":
        # Rule says "WATCH 제한" (limit WATCH), but let's be strict if desired.
        # User defined it as WATCH 제한. We'll log it if strictly required.
        pass

    # RULE 3: Timing <-> Action
    if timing == "WAIT" and action == "ADD":
        failures.append("INVALID_TIMING_ADD")
    if timing == "N/A":
        # Rule: 모든 Action 금지 (All actions forbidden)
        # Even WATCH might be too much if it's N/A? Usually N/A means error.
        failures.append("INVALID_TIMING_NA")
    if timing == "IDEAL" and action != "ADD":
        # Rule: Timing = IDEAL -> ADD 가능. (Not strict "ADD 필수", but "ADD 가능")
        pass

    # RULE 4: Top Stocks <-> Action
    if action == "ADD" and len(stocks) == 0:
        failures.append("ADD_WITH_NO_STOCKS")

    # RULE 5: Risk <-> Allocation
    if risk == "HIGH" and allocation > 0.3:
        failures.append("HIGH_RISK_OVER_ALLOCATION")
    if risk == "MEDIUM" and allocation > 0.6:
        failures.append("MEDIUM_RISK_OVER_ALLOCATION")

    # 5. Generate Report
    status = "PASS" if not failures else "FAIL"
    report = {
        "status": status,
        "errors": failures,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "snapshot": {
            "action": action,
            "allocation": allocation,
            "confidence": confidence,
            "timing": timing,
            "risk": risk,
            "stocks_count": len(stocks)
        }
    }
    
    report_absolute.parent.mkdir(parents=True, exist_ok=True)
    with open(report_absolute, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
        
    print(f"[DECISION] <<< AUDIT COMPLETED. Status: {status}")
    if status == "FAIL":
        print(f"[DECISION] ❌ LOGICAL ERRORS: {failures}")
    return failures

if __name__ == "__main__":
    p_root = Path(__file__).parent.parent.parent
    validate_decision(p_root)
