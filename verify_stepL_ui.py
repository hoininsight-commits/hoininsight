import os
import json
from pathlib import Path

def check_file(path):
    exists = os.path.exists(path)
    if exists:
        print(f"[OK] File exists: {path}")
    else:
        print(f"[FAIL] File missing: {path}")
    return exists

def check_json(path):
    if not os.path.exists(path):
        print(f"[FAIL] JSON missing: {path}")
        return False
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if data:
            print(f"[OK] JSON valid and not empty: {path}")
            return True
        else:
            print(f"[FAIL] JSON is empty: {path}")
            return False
    except Exception as e:
        print(f"[FAIL] JSON error in {path}: {e}")
        return False

def check_pipeline_integration():
    path = "src/ops/run_daily_pipeline.py"
    if not os.path.exists(path):
        print(f"[FAIL] Pipeline script missing: {path}")
        return False
    
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    if "from src.ui.build_operator_view import build_operator_view" in content and "build_operator_view(project_root)" in content:
        print(f"[OK] Pipeline integration found in {path}")
        return True
    else:
        print(f"[FAIL] Pipeline integration MISSING in {path}")
        return False

def run():
    print("\n=== STEP-L UI IMPLEMENTATION VERIFICATION ===")
    results = {}

    # 1. Code Existence
    results["build_script"] = check_file("src/ui/build_operator_view.py")
    results["html"] = check_file("docs/ui/index.html")
    results["js"] = check_file("docs/ui/operator_simple.js")

    # 2. JSON Generation
    results["json"] = check_json("docs/data/ui/ui_operator_view.json")

    # 3. Pipeline Integration
    results["pipeline"] = check_pipeline_integration()

    print("\n--- Summary ---")
    for k, v in results.items():
        print(f"{k}: {'OK' if v else 'FAIL'}")

    if all(results.values()):
        print("\n[VERIFY][OK] UI fully implemented")
        return True
    else:
        print("\n[VERIFY][FAIL] UI missing components")
        return False

if __name__ == "__main__":
    run()
