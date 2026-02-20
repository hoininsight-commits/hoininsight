import os
import json
import yaml
from pathlib import Path

def verify_ref003():
    print("=== VERIFYING REF-003: Contract Authority ===")
    project_root = Path(__file__).parent.parent
    
    # 1. Run Manifest Builder v2 (Enhanced)
    print("\n[Step 1] Running Enhanced Manifest Builder v2...")
    from src.ui_contracts.manifest_builder_v2 import build_manifest_v2
    manifest = build_manifest_v2(project_root)
    
    # 2. Check Authority Field
    assert manifest.get("authority") == "src/ui_contracts", "Authority field missing or incorrect"
    print("✅ Authority field confirmed.")
    
    # 3. Verify Pruning (None-registry files omitted)
    registry_path = project_root / "registry" / "ui_cards" / "ui_card_registry_v1.yml"
    with open(registry_path, "r", encoding="utf-8") as f:
        registry = yaml.safe_load(f)
        registered_keys = [c["key"] for c in registry["cards"]]
        
    for asset in manifest["assets"]:
        assert asset["key"] in registered_keys, f"Unregistered asset found in manifest: {asset['key']}"
    
    # Check if a non-registered file (e.g. legacy/unregistered one) is NOT in manifest
    manifest_keys = [a["key"] for a in manifest["assets"]]
    # We asserted earlier that all keys must be in registered_keys.
    
    # Let's ensure 'hero_summary' is NOT in manifest if it was intentionally omitted from registry
    if "hero_summary" not in registered_keys:
        assert "hero_summary" not in manifest_keys, "Unregistered asset 'hero_summary' should NOT be in manifest"
    
    # Currently data/ui/ contains things like daily_narrative_fusion.json which are NOT in registry.
    assert "daily_narrative_fusion" not in manifest_keys, "Unregistered legacy asset 'daily_narrative_fusion' should have been pruned"
    print("✅ Pruning logic verified: Only registered assets in manifest.")

    # 4. Check for "undefined"
    print("\n[Step 2] Checking for 'undefined' in active assets...")
    for asset in manifest["assets"]:
        if asset["exists"]:
            content = (project_root / asset["path"]).read_text(encoding="utf-8")
            assert '"undefined"' not in content, f"Undefined value found in {asset['key']}"
    print("✅ No 'undefined' strings found in active assets.")

    print("\n=== REF-003 VERIFICATION SUCCESS ===")

if __name__ == "__main__":
    verify_ref003()
