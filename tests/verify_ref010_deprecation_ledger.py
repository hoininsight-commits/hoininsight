import os
import json
import subprocess
from pathlib import Path

def test_ref010_deprecation_ledger():
    print("=== VERIFYING REF-010: Deprecation Ledger ===")
    project_root = Path(os.getcwd())
    
    # Run the publish pipeline (which triggers the scanner)
    os.environ["PYTHONPATH"] = os.environ.get("PYTHONPATH", "") + ":" + str(project_root)
    subprocess.run(["python3", "src/ui_logic/publish/publish_all.py"], check=True)
    
    # 1. Ledger file exists
    ledger_path = project_root / "data_outputs/ops/deprecation_ledger.json"
    assert ledger_path.exists(), "Deprecation ledger should be created in data_outputs"
    
    # 2. Schema check
    with open(ledger_path, "r", encoding="utf-8") as f:
        ledger = json.load(f)
        
    required_keys = ["date", "status", "legacy_hits", "summary"]
    for key in required_keys:
        assert key in ledger, f"Ledger missing key: {key}"
        
    # 3. Entries content check
    if ledger["legacy_hits"]:
        hit = ledger["legacy_hits"][0]
        entry_keys = ["legacy_key", "path", "reason", "replacement", "sunset", "severity"]
        for ek in entry_keys:
            assert ek in hit, f"Hit entry missing key: {ek}"
            assert hit[ek] is not None, f"Hit entry key {ek} is null"
            assert hit[ek] != "undefined", f"Hit entry key {ek} is 'undefined'"

    # 4. Status validation
    assert ledger["status"] in ["OK", "WARN", "FAIL"], f"Invalid status: {ledger['status']}"
    
    # 5. Mirror check
    mirror_path = project_root / "docs/data/ops/deprecation_ledger.json"
    assert mirror_path.exists(), "Ledger should be mirrored to docs/data/ops"
    
    # 6. Enforcement Test (Simulated high hit)
    print("\n[Case 2] Testing HOIN_LEGACY_ENFORCE=1...")
    # Add a HIGH severity item to the map if not already there, or just trust the direct_ui_load_without_manifest exists in render.js
    # We'll use the existing direct_ui_load_without_manifest rule
    os.environ["HOIN_LEGACY_ENFORCE"] = "1"
    
    # We expect this to fail if HIGH hits exist.
    # Check if high hits exist first to decide what to expect
    if ledger["summary"]["high"] > 0:
        try:
            subprocess.run(["python3", "src/ui_logic/publish/publish_all.py"], check=True, capture_output=True)
            assert False, "Pipeline should have failed in enforce mode with HIGH hits"
        except subprocess.CalledProcessError as e:
            print(f"✅ Correctly failed in enforce mode: {e.stderr.decode().splitlines()[-1]}")
    else:
        print("ℹ️ No high hits found, skipping enforcement failure test.")

    print("\n=== REF-010 VERIFICATION SUCCESS ===")

if __name__ == "__main__":
    test_ref010_deprecation_ledger()
