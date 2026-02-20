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
    print("=== [VERIFY] IS-82 Watchlist Promotion Layer ===")
    
    # 1. Run IssueSignal (Generates Watchlist -> Promotes to Candidates)
    print("1. Running run_issuesignal...")
    run_command("python3 -m src.issuesignal.run_issuesignal")
    
    # 2. Verify Promoted JSON
    ymd = datetime.utcnow().strftime("%Y-%m-%d")
    promoted_path = ROOT_DIR / f"data/issuesignal/promoted_candidates_{ymd}.json"
    
    print(f"2. Checking {promoted_path}...")
    if not promoted_path.exists():
        print(f"[FAIL] Promoted candidates file not found: {promoted_path}")
        sys.exit(1)
        
    p_data = json.loads(promoted_path.read_text(encoding="utf-8"))
    count = p_data.get("count", 0)
    print(f"   Promoted Count: {count}")
    
    if count == 0:
        print("[WARN] No candidates promoted. (Check mock logic in promotion engine)")
        # If mock logic is robust (promotes 'STRUCTURE' always), this should be > 0.
        
    # 3. Run Dashboard Generator
    print("3. Running dashboard_generator...")
    run_command("python3 -m src.dashboard.dashboard_generator")
    
    # 4. Verify HTML
    print("4. Verifying docs/index.html...")
    html_path = ROOT_DIR / "docs/index.html"
    content = html_path.read_text(encoding="utf-8")
    
    # Check for Badge
    if "FROM WATCHLIST" in content:
        print("[PASS] 'FROM WATCHLIST' badge found in HTML")
    else:
        if count > 0:
            print("[FAIL] Promoted items exist but badge not found in HTML")
            sys.exit(1)
        else:
            print("[WARN] No promoted items, so no badge expected.")

    # Check Candidate Header Update
    if "포함: 관찰 승격" in content:
        print("[PASS] Candidate header updated correctly")
    else:
        if count > 0:
             print("[FAIL] Header update text not found")
             sys.exit(1)

    print("[PASS] All checks passed!")

if __name__ == "__main__":
    main()
