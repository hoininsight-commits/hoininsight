import json
from pathlib import Path

def test_outcome_validation_integrity():
    project_root = Path(__file__).parent.parent
    ledger_path = project_root / "data" / "ops" / "outcome_ledger.json"
    summary_path = project_root / "data" / "ops" / "outcome_summary.json"
    
    errors = []
    
    # 1. Check Ledger
    if not ledger_path.exists():
        errors.append(f"Outcome Ledger missing at {ledger_path}")
    else:
        with open(ledger_path, "r", encoding="utf-8") as f:
            ledger = json.load(f)
            if not ledger:
                errors.append("Outcome Ledger is empty")
            else:
                last_entry = ledger[-1]
                mandatory_keys = ["date", "core_theme", "evaluation", "validation_window"]
                for key in mandatory_keys:
                    if key not in last_entry:
                        errors.append(f"Ledger entry missing key: {key}")
                
                eval_obj = last_entry.get("evaluation", {})
                if "failure_type" not in eval_obj:
                    errors.append("Evaluation missing failure_type")
                if "hit_ratio" not in eval_obj:
                    errors.append("Evaluation missing hit_ratio")

    # 2. Check Summary
    if not summary_path.exists():
        errors.append(f"Outcome Summary missing at {summary_path}")
    else:
        with open(summary_path, "r", encoding="utf-8") as f:
            summary = json.load(f)
            if "last_7d" not in summary:
                errors.append("Summary missing last_7d stats")
            if "theme_accuracy" not in summary.get("last_7d", {}):
                errors.append("Summary stats missing theme_accuracy")

    if errors:
        print("❌ [STEP-F] Outcome Validation Verification Failed:")
        for e in errors:
            print(f"  - {e}")
        return False
    else:
        print("✅ [STEP-F] Performance & Truth Loop Verification Passed!")
        print(f"   Ledger Entries: {len(ledger)}")
        print(f"   Current Accuracy: {summary.get('last_7d', {}).get('theme_accuracy')}")
        return True

if __name__ == "__main__":
    test_outcome_validation_integrity()
