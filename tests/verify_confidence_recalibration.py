import json
from pathlib import Path

def test_confidence_recalibration_integrity():
    project_root = Path(__file__).parent.parent
    brief_path = project_root / "data" / "operator" / "today_operator_brief.json"
    metrics_path = project_root / "data" / "ops" / "confidence_metrics.json"
    
    errors = []
    
    # 1. Check Brief for Structured Confidence
    if not brief_path.exists():
        errors.append(f"Brief missing at {brief_path}")
    else:
        with open(brief_path, "r", encoding="utf-8") as f:
            brief = json.load(f)
            decision_conf = brief.get("investment_decision", {}).get("decision", {}).get("confidence")
            
            if not isinstance(decision_conf, dict):
                errors.append("Confidence is NOT a structured object")
            else:
                mandatory_keys = ["value", "source", "base_confidence", "adjustments", "final_confidence"]
                for key in mandatory_keys:
                    if key not in decision_conf:
                        errors.append(f"Confidence object missing key: {key}")
                
                if decision_conf.get("source") != "recalibrated":
                    errors.append(f"Confidence source is NOT 'recalibrated': {decision_conf.get('source')}")

    # 2. Check Metrics
    if not metrics_path.exists():
        errors.append(f"Confidence Metrics missing at {metrics_path}")
    else:
        with open(metrics_path, "r", encoding="utf-8") as f:
            metrics = json.load(f)
            if not metrics:
                errors.append("Confidence Metrics is empty")

    if errors:
        print("❌ [STEP-G] Confidence Recalibration Verification Failed:")
        for e in errors:
            print(f"  - {e}")
        return False
    else:
        print("✅ [STEP-G] Validation-Weighted Trust Loop Verification Passed!")
        print(f"   Final Confidence: {decision_conf.get('value')}")
        print(f"   Adjustments: {decision_conf.get('adjustments')}")
        return True

if __name__ == "__main__":
    test_confidence_recalibration_integrity()
