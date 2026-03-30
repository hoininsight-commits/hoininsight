import os
import json
import sys
from pathlib import Path

# Setup Project Root
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
sys.path.append(str(PROJECT_ROOT))

from src.ops.engine_validation_audit import EngineValidationAudit

def test_audit_generation():
    print(">>> Testing Engine Validation Audit [STEP-H] Generation...")
    
    # Ensure data directory exists
    ops_dir = PROJECT_ROOT / "data" / "ops"
    ops_dir.mkdir(parents=True, exist_ok=True)
    
    # Mock data if missing for the test
    ledger_path = ops_dir / "outcome_ledger.json"
    if not ledger_path.exists():
        print("[Test] Mocking outcome ledger for verification...")
        mock_ledger = [
            {
                "date": "2026-03-27",
                "core_theme": "AI Power Constraint",
                "decision": {"confidence": {"value": 0.44}},
                "evaluation": {"hit_ratio": 0.45, "failure_type": "THEME_RIGHT_DECISION_WRONG"}
            },
            {
                "date": "2026-03-28",
                "core_theme": "Semiconductor Shift",
                "decision": {"confidence": {"value": 0.62}},
                "evaluation": {"hit_ratio": 0.65, "failure_type": "SUCCESS"}
            }
        ]
        with open(ledger_path, "w", encoding="utf-8") as f:
            json.dump(mock_ledger, f, indent=2)

    auditor = EngineValidationAudit(PROJECT_ROOT)
    report = auditor.run_audit()
    
    if not report:
        print("❌ Audit generation failed.")
        return False
        
    print(f"✅ Audit Status: {report['status']}")
    print(f"✅ Failure Distribution: {report['failure_distribution']}")
    print(f"✅ Confidence Stability: {report['confidence_stability']}")
    print(f"✅ Outcome Alignment: {report['outcome_alignment']}")
    
    # Check if report file exists
    report_path = PROJECT_ROOT / "data" / "ops" / "validation_audit_report.json"
    if report_path.exists():
        print(f"✅ Report file verified at {report_path}")
        return True
    else:
        print("❌ Report file missing.")
        return False

if __name__ == "__main__":
    if test_audit_generation():
        print("\n=== STEP-H VERIFICATION SUCCESS ===")
    else:
        print("\n=== STEP-H VERIFICATION FAILED ===")
        sys.exit(1)
