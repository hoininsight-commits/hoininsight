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

    # V6. remote_verify_* freeze policy
    print("\n[V6] Checking remote_verify_* freeze policy...")
    frozen_dirs = list(root.glob("remote_verify_*"))
    for d in frozen_dirs:
        if d.is_dir():
            for child in d.rglob("*"):
                if child.is_file() and child.name != "DEPRECATED.md":
                    print(f"❌ [FAIL] Active file found in frozen directory: {child}")
                    all_passed = False
    if not frozen_dirs:
        print("✅ [OK] No remote_verify_* directories found.")

    # V7. docs/ui/ data fetch constraints
    print("\n[V7] Checking docs/ui/ data fetch constraints...")
    forbidden_endpoints = ["data_outputs/", "remote_verify/", "legacy/"]
    for js_file in docs_ui.rglob("*.js"):
        try:
            content = js_file.read_text(encoding="utf-8")
            for forbidden in forbidden_endpoints:
                if forbidden in content:
                    print(f"❌ [FAIL] Disallowed fetch endpoint '{forbidden}' found in {js_file}")
                    all_passed = False
        except Exception as e:
            print(f"⚠️ [WARN] Could not read {js_file} for V7 checking: {e}")
            
    # V8. Narrative Score Generation Guard
    print("\n[V8] Checking Narrative Score Generation (PHASE-14B)...")
    try:
        today_publish = docs_decision / "today.json"
        if today_publish.exists():
            data = json.loads(today_publish.read_text(encoding="utf-8"))
            topics = data if isinstance(data, list) else data.get("top_topics", [data])
            
            has_score = False
            for t in topics:
                if "narrative_score" in t and t["narrative_score"] is not None:
                    has_score = True
                    break
                    
            if not has_score:
                print("⚠️ [WARN] No narrative_score found in today.json.")
                print("          This is allowed (e.g. inactive days), but if persistent for 3 days, it's a Publish Drop.")
            else:
                print("✅ [OK] Narrative score successfully verified in today.json.")
        else:
            print("⚠️ [WARN] today.json not found for narrative check.")
    except Exception as e:
        print(f"⚠️ [WARN] Could not verify narrative score: {e}")

    # V9. Native Fake Sequence & Hash UI Blocker
    print("\n[V9] Checking UI against Fake Hash Narrative Injections...")
    import re
    # Patterns that represent the fake hash generation
    disallowed_patterns = [
        r"hash.*score",
        r"hash.*narrative_score",
        r"hash.*intensity",
        r"charCodeAt.*%",
        r"charCodeAt.*mod",
        r"Math\.random",
        r"salt.*score",
        r"salt.*narrative",
        r"salt %"
    ]
    for js_file in docs_ui.rglob("*.js"):
        try:
            content = js_file.read_text(encoding="utf-8")
            for pattern in disallowed_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    print(f"❌ [FAIL] Disallowed fake score pattern '{pattern}' found in {js_file}")
                    all_passed = False
        except Exception as e:
            print(f"⚠️ [WARN] Could not read {js_file} for V9 checking: {e}")

    if not all_passed:
        print("\n❌ RELEASE INTEGRITY CHECK FAILED.")
        sys.exit(1)
    
    print("\n✅ RELEASE INTEGRITY CHECK PASSED.")
    sys.exit(0)

if __name__ == "__main__":
    main()
