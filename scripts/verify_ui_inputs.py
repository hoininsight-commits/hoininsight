
import os
import json
import sys
from pathlib import Path

def verify_ui_inputs():
    project_root = Path(os.getcwd())
    docs_ui = project_root / "docs" / "ui"
    docs_data_ui = project_root / "docs" / "data" / "ui"
    docs_data_decision = project_root / "docs" / "data" / "decision"

    required_ui_files = [
        "hero_summary.json",
        "operator_main_card.json",
        "narrative_entry_hook.json",
        "upcoming_risk_topN.json"
    ]
    
    required_decision_files = [
        "interpretation_units.json",
        "speakability_decision.json"
    ]
    
    missing = []
    
    # Check UI files
    if not docs_data_ui.exists():
        print(f"❌ Missing Directory: {docs_data_ui}")
        missing.append("docs/data/ui/")
    else:
        for f in required_ui_files:
            if not (docs_data_ui / f).exists():
                print(f"❌ Missing File: docs/data/ui/{f}")
                missing.append(f"docs/data/ui/{f}")
    
    # Check Decision files
    if not docs_data_decision.exists():
        print(f"❌ Missing Directory: {docs_data_decision}")
        missing.append("docs/data/decision/")
    else:
        # [TASK E] Manifest Check
        manifest_path = docs_data_decision / "manifest.json"
        if not manifest_path.exists():
            print(f"❌ Missing Manifest: docs/data/decision/manifest.json")
            missing.append("docs/data/decision/manifest.json")
        else:
            try:
                with open(manifest_path, "r") as f:
                    manifest = json.load(f)
                if not manifest.get("files"):
                    print(f"⚠️ Manifest Empty: docs/data/decision/manifest.json")
                    # Not a hard fail but a warning
            except Exception as e:
                print(f"❌ Manifest Corrupt: {e}")
                missing.append("docs/data/decision/manifest.json")

        for f in required_decision_files:
            if not (docs_data_decision / f).exists():
                print(f"❌ Missing File: docs/data/decision/{f}")
                missing.append(f"docs/data/decision/{f}")

    if missing:
        print("\n🚨 UI Input Verification FAILED!")
        sys.exit(1)
    
    print("✅ UI Input Verification PASSED!")
    sys.exit(0)

if __name__ == "__main__":
    verify_ui_inputs()
