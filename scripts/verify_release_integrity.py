#!/usr/bin/env python3
"""
[FREEZE-UI-STRUCTURE] Release Integrity Check
Ensures that the output docs directory is built correctly before deployment.
"""
import sys
import json
from pathlib import Path
import subprocess

def check_file(path: Path, required: bool = True):
    if not path.exists():
        if required:
            print(f"❌ [FAIL] Missing required file: {path}")
            return False
        else:
            print(f"⚠️ [WARN] Missing optional file: {path}")
            return True
    print(f"✅ [OK] Found: {path}")
    return True

def main():
    print("--- [FREEZE-UI-STRUCTURE] Release Integrity Check ---")
    root = Path(".")
    docs = root / "docs"
    docs_ui = docs / "ui"
    docs_decision = docs / "data" / "decision"

    all_passed = True

    # V1. docs/ui 핵심 엔트리 파일 존재
    print("\n[V1] Checking core UI files...")
    ui_files = ["utils.js", "operator_today.js", "operator_history.js"]
    for f in ui_files:
        if not check_file(docs_ui / f):
            all_passed = False

    # V2. docs/data/decision/manifest.json 존재 + entries >= 1
    print("\n[V2] Checking decision manifest...")
    manifest_path = docs_decision / "manifest.json"
    if not check_file(manifest_path):
        all_passed = False
    else:
        try:
            data = json.loads(manifest_path.read_text("utf-8"))
            entries = data.get("files", [])
            if len(entries) < 1:
                print("❌ [FAIL] manifest.json has 0 entries")
                all_passed = False
            else:
                print(f"✅ [OK] manifest.json has {len(entries)} entries")

            # V3. manifest가 가리키는 파일 100% 존재
            print("\n[V3] Checking manifest entries existence...")
            for entry in entries:
                file_path = docs_decision / entry["path"]
                if not check_file(file_path):
                    all_passed = False
        except Exception as e:
            print(f"❌ [FAIL] Could not parse manifest.json: {e}")
            all_passed = False

    # V4. 현재 규격 (docs/data/decision) 필수 파일 존재
    print("\n[V4] Checking data assets (current spec)...")
    if not check_file(docs_decision / "today.json"):
        all_passed = False
    
    # V5. 중복 publish 스크립트 guard 통과
    print("\n[V5] Running NO-DUP-LOCK Guard...")
    guard_script = root / "scripts" / "verify_no_duplicate_publishers.py"
    if guard_script.exists():
        res = subprocess.run(["python3", str(guard_script)], capture_output=True, text=True)
        print(res.stdout)
        if res.returncode != 0:
            print(res.stderr)
            print("❌ [FAIL] NO-DUP-LOCK Guard failed.")
            all_passed = False
        else:
            print("✅ [OK] NO-DUP-LOCK Guard passed.")
    else:
        print("❌ [FAIL] verify_no_duplicate_publishers.py not found.")
        all_passed = False

    if not all_passed:
        print("\n❌ RELEASE INTEGRITY CHECK FAILED.")
        sys.exit(1)
    
    print("\n✅ RELEASE INTEGRITY CHECK PASSED.")
    sys.exit(0)

if __name__ == "__main__":
    main()
