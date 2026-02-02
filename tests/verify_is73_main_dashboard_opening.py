import sys
from pathlib import Path
import json
import subprocess
import re

# Add root to path
ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

def run_command(cmd):
    print(f"[CMD] {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=str(ROOT_DIR), capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[FAIL] Command failed: {cmd}")
        print(result.stderr)
        sys.exit(1)
    return result.stdout

def main():
    print("=== [VERIFY] IS-73 Main Dashboard Opening Sentence ===")
    
    # 1. Run Issue Signal Generator
    print("1. Running run_issuesignal...")
    run_command("python3 -m src.issuesignal.run_issuesignal")
    
    # 2. Verify JSON Output
    print("2. Verifying ISSUE-*.json...")
    packs_dir = ROOT_DIR / "data/issuesignal/packs"
    candidates = list(packs_dir.glob("ISSUE-*.json"))
    if not candidates:
        print("[FAIL] No ISSUE-*.json found in data/issuesignal/packs/")
        sys.exit(1)
        
    candidates.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    latest_json = candidates[0]
    print(f"   Found: {latest_json.name}")
    
    data = json.loads(latest_json.read_text(encoding="utf-8"))
    opening = data.get("opening_sentence")
    
    if not opening or opening == "-":
        print(f"[FAIL] Invalid opening_sentence: {opening}")
        sys.exit(1)
    print(f"   Opening Sentence: {opening}")
    
    # 3. Run Dashboard Generator
    print("3. Running dashboard_generator...")
    run_command("python3 -m src.dashboard.dashboard_generator")
    
    # 4. Verify HTML
    print("4. Verifying docs/index.html...")
    html_path = ROOT_DIR / "docs/index.html"
    if not html_path.exists():
        print("[FAIL] docs/index.html not found")
        sys.exit(1)
        
    html_content = html_path.read_text(encoding="utf-8")
    
    # Check Section Header
    if "📌 오늘의 핵심 한 문장" not in html_content:
        print("[FAIL] Section header not found in HTML")
        sys.exit(1)
        
    # Check Opening Sentence presence (normalized check)
    if opening not in html_content:
        # Try simplistic replacement check just in case of formatting
        if opening.replace("'", "&#39;") not in html_content:
             print(f"[FAIL] Opening sentence not found in HTML.\nExpected: {opening}")
             sys.exit(1)
             
    # Check Long Form presence
    long_form = data.get("content_package", {}).get("long_form", "")
    if long_form and "📝 Long-form Script" not in html_content:
         print("[FAIL] Long-form script section missing")
         sys.exit(1)

    print("[PASS] All checks passed!")

if __name__ == "__main__":
    main()
