import os
import sys
from pathlib import Path

def verify_ref005():
    print("=== VERIFYING REF-005: Structure Integrity ===")
    project_root = Path(__file__).parent.parent
    
    # 1. Check Directory Existence
    required_dirs = [
        "src/ui_logic/contracts",
        "src/ui_logic/card_builders",
        "src/ui_logic/narrators",
        "src/engine/collectors",
        "src/engine/normalize",
        "registry/policies",
        "data_outputs/ui",
        "data_outputs/decision"
    ]
    
    for d in required_dirs:
        path = project_root / d
        assert path.exists(), f"Required directory missing: {d}"
        print(f"✅ Directory exists: {d}")

    # 2. Test Shim Imports
    print("\n[Step 2] Testing Shims (Import mapping)...")
    try:
        from src.ui.manifest_builder import build_manifest
        print("✅ Shim import successful: src.ui.manifest_builder")
        
        from src.ui_contracts.publish import run_publish
        print("✅ Shim import successful: src.ui_contracts.publish")
        
        from src.collectors.fred_collector import FREDCollector
        print("✅ Shim import successful: src.collectors.fred_collector.FREDCollector")
        
        from src.normalizers.fred_normalizers import normalize_fed_funds
        print("✅ Shim import successful: src.normalizers.fred_normalizers.normalize_fed_funds")
        
    except ImportError as e:
        print(f"❌ Shim Import Failed: {e}")
        sys.exit(1)

    # 3. Verify Output Stability (Run publish and check data_outputs)
    print("\n[Step 3] Verifying Output Mirroring (data_outputs)...")
    from src.ui_contracts.publish import run_publish
    run_publish(project_root)
    
    assert (project_root / "data_outputs" / "ui" / "manifest.json").exists(), "Mirror output missing: data_outputs/ui/manifest.json"
    assert (project_root / "docs" / "data" / "ui" / "manifest.json").exists(), "Original output missing: docs/data/ui/manifest.json"
    print("✅ Output mirroring verified.")

    print("\n=== REF-005 VERIFICATION SUCCESS ===")

if __name__ == "__main__":
    verify_ref005()
