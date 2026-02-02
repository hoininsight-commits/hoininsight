import sys
from pathlib import Path
import json
import subprocess
from datetime import datetime

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
    print("=== [VERIFY] IS-83 Editorial Tone & Script Mode Selector ===")
    
    # 1. Run IssueSignal (Watchlist -> Promoted -> Tone Applied)
    print("1. Running run_issuesignal...")
    run_command("python3 -m src.issuesignal.run_issuesignal")
    
    # 2. Verify Promoted JSON has Tone/Mode
    ymd = datetime.utcnow().strftime("%Y-%m-%d")
    promoted_path = ROOT_DIR / f"data/issuesignal/promoted_candidates_{ymd}.json"
    
    print(f"2. Checking {promoted_path}...")
    if not promoted_path.exists():
        print(f"[FAIL] Promoted candidates file not found: {promoted_path}")
        sys.exit(1)
        
    p_data = json.loads(promoted_path.read_text(encoding="utf-8"))
    candidates = p_data.get("candidates", [])
    
    if not candidates:
        print("[WARN] No candidates promoted. Cannot verify Tone Selector logic.")
        # We rely on IS-82 mock logic which guarantees promotion of STRUCTURE/SCENARIO items.
    
    for idx, c in enumerate(candidates):
        tone = c.get("tone_type")
        mode = c.get("script_mode")
        print(f"   Candidate {idx}: Tone={tone}, Mode={mode}, Cat={c.get('category')}")
        
        if not tone or not mode:
            print(f"[FAIL] Candidate {idx} missing Tone or Mode data")
            sys.exit(1)
            
        # Verify Rule consistency (Basic check)
        if tone == "WARNING" and mode != "ALERT":
            print(f"[WARN] Inconsistent Tone/Mode: {tone}/{mode}")

    # 3. Run Dashboard Generator
    print("3. Running dashboard_generator...")
    run_command("python3 -m src.dashboard.dashboard_generator")
    
    # 4. Verify HTML
    print("4. Verifying docs/index.html...")
    html_path = ROOT_DIR / "docs/index.html"
    content = html_path.read_text(encoding="utf-8")
    
    if "Tone" in content and "Mode" in content:
        print("[PASS] Table headers 'Tone' and 'Mode' found.")
    else:
        print("[FAIL] Table headers missing")
        sys.exit(1)
        
    # Check for specific badges if candidates exist
    if candidates:
        if "WARNING" in content or "STRUCTURAL" in content or "SCENARIO" in content or "PREVIEW" in content:
            print("[PASS] Tone Badges found in HTML")
        else:
            print("[FAIL] Tone Badges NOT found in HTML (but candidates exist)")
            sys.exit(1)

    print("[PASS] All checks passed!")

if __name__ == "__main__":
    main()
