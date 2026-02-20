
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
    # [PHASE 5] Enhanced Manifest & Decision Validation
    manifest_path = docs_data_decision / "manifest.json"
    if not manifest_path.exists():
        print(f"❌ Missing Manifest: {manifest_path}")
        missing.append("manifest.json")
    else:
        try:
            with open(manifest_path, "r") as f:
                manifest = json.load(f)
            files = manifest.get("files", [])
            if not files:
                print(f"⚠️ Manifest is empty.")
            
            # Check if each file in manifest exists and is valid
            valid_count = 0
            for fname in files:
                fpath = docs_data_decision / fname
                if not fpath.exists():
                    print(f"❌ Manifest entry missing on disk: {fname}")
                    missing.append(fname)
                    continue
                
                try:
                    with open(fpath, "r") as df:
                        data = json.load(df)
                    items = data if isinstance(data, list) else [data]
                    for item in items:
                        # Schema assertion (v2.2)
                        if "title" in item:
                            valid_count += 1
                except Exception as e:
                    print(f"❌ Decision file corrupt: {fname} ({e})")
                    missing.append(fname)
            
            if valid_count == 0:
                print("❌ No valid decision items found in any manifest file.")
                missing.append("empty_decisions")

        except Exception as e:
            print(f"❌ Manifest parsing failed: {e}")
            missing.append("manifest_error")

    # [PHASE 6] Anti-Undefined JS Template Scan
    js_dir = project_root / "docs" / "ui"
    unsafe_literals = []
    if js_dir.exists():
        for js_file in js_dir.glob("*.js"):
            try:
                content = js_file.read_text().lower()
                # We check for 'undefined' or 'null' in literal strings, but allow it in code (like utils.js logic)
                # This is a heuristic: check if common UI patterns have them
                if "innerText = 'undefined'" in js_file.read_text() or "innerHTML = 'undefined'" in js_file.read_text():
                    print(f"❌ Unsafe literal detected in {js_file.name}")
                    unsafe_literals.append(js_file.name)
            except Exception: pass
    
    if unsafe_literals:
        missing.append("unsafe_js_templates")

    # Final Summary
    if missing:
        print("\n🚨 UI Input Verification FAILED!")
        print(f"Missing/Issues: {', '.join(missing)}")
        sys.exit(1)
    
    print(f"✅ UI Input Verification PASSED! (Validated {valid_count} entries)")
    sys.exit(0)

if __name__ == "__main__":
    verify_ui_inputs()
