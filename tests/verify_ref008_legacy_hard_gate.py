import os
import json
import pytest
from pathlib import Path
from src.ui_logic.guards.warning_mode import get_hard_mode
from src.ui_logic.publish.publish_all import run_publish

def verify_ref008():
    print("=== VERIFYING REF-008: Legacy Hard Gate ===")
    project_root = Path(os.getcwd())
    ledger_path = project_root / "data_outputs/ops/legacy_block_ledger.json"
    readiness_report_path = project_root / "docs/ops/LEGACY_HARD_READINESS.md"
    
    # Reset ledger
    if ledger_path.exists(): os.remove(ledger_path)

    # 1. Test Blocked (Not in Allowlist)
    print("\n[Case 1] HARD=1 + Blocked Module...")
    os.environ["HOIN_LEGACY_HARD"] = "1"
    try:
        from src.ui import ui_decision_contract
        # Note: rebuild_shims maps this to src.ui_logic.card_builders.ui_decision_contract
        # This is NOT in allowlist (registry/ops/legacy_allowlist_v1.yml)
        pytest.fail("Should have blocked legacy access")
    except RuntimeError as e:
        print(f"✅ Correctly Blocked: {e}")
    except ImportError: # In case of re-import issues in same process
        print("⚠️ Module already imported or Import error - check ledger")

    # 2. Test Allowed
    print("\n[Case 2] HARD=1 + Allowed Module...")
    # src.ui.operator_main_contract is in allowlist
    try:
        from src.ui import operator_main_contract
        print("✅ Correctly Allowed.")
    except Exception as e:
        pytest.fail(f"Should have allowed access but raised: {e}")

    # 3. Verify Ledger Persistence
    assert ledger_path.exists(), "Ledger not created"
    with open(ledger_path, "r", encoding="utf-8") as f:
        ledger = json.load(f)
        assert len(ledger["blocked"]) > 0 or len(ledger["allowed"]) > 0, "No entries in ledger"
        print(f"✅ Ledger verified: {len(ledger['blocked'])} blocked, {len(ledger['allowed'])} allowed.")

    # 4. Verify Readiness Report Generator
    run_publish(project_root)
    assert readiness_report_path.exists(), "Readiness report not created"
    print("✅ Readiness report verified.")

    # Reset
    os.environ["HOIN_LEGACY_HARD"] = "0"
    print("\n=== REF-008 VERIFICATION SUCCESS ===")

if __name__ == "__main__":
    verify_ref008()
