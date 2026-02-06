import os
import sys
from pathlib import Path

def verify_ref006():
    print("=== VERIFYING REF-006: Single Source of Truth ===")
    project_root = Path(__file__).parent.parent
    
    # 1. Canonical Files Existence
    required_files = [
        "src/ui_logic/__init__.py",
        "src/ui/_LEGACY_SHIM_README.md",
        "src/ui_logic/publish/publish_all.py",
        "docs/architecture/path_ownership.md"
    ]
    
    for f in required_files:
        path = project_root / f
        assert path.exists(), f"Required file missing: {f}"
        print(f"✅ File exists: {f}")

    # 2. Verify Legacy Path Role (Example check)
    shim_path = project_root / "src" / "ui" / "operator_main_contract.py"
    with open(shim_path, "r", encoding="utf-8") as f:
        content = f.read()
        # Should contain alias/import header
        assert "alias only" in content.lower() or "from src.ui_logic" in content
    print("✅ Legacy shim guard verified (Alias check).")

    # 3. Verify SSOT Publish
    from src.ui_logic.publish.publish_all import run_publish
    run_publish(project_root)
    
    assert (project_root / "data_outputs" / "ui" / "manifest.json").exists(), "SSOT Data missing in data_outputs/"
    print("✅ SSOT Publish verified.")

    print("\n=== REF-006 VERIFICATION SUCCESS ===")

if __name__ == "__main__":
    verify_ref006()
