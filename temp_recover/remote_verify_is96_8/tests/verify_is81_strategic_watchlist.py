import sys
from pathlib import Path
import json
import subprocess
from datetime import datetime

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
    print("=== [VERIFY] IS-81 Strategic Watchlist Layer ===")
    
    # 1. Run Issue Signal Generator
    print("1. Running run_issuesignal...")
    run_command("python3 -m src.issuesignal.run_issuesignal")
    
    # 2. Verify Watchlist JSON
    print("2. Verifying strategic_watchlist_*.json...")
    ymd = datetime.utcnow().strftime("%Y-%m-%d")
    watchlist_path = ROOT_DIR / "data/watchlist" / f"strategic_watchlist_{ymd}.json"
    
    if not watchlist_path.exists():
        print(f"[FAIL] Watchlist file not found: {watchlist_path}")
        sys.exit(1)
        
    data = json.loads(watchlist_path.read_text(encoding="utf-8"))
    items = data.get("watchlist", [])
    if not items:
        print("[FAIL] Watchlist is empty")
        sys.exit(1)
        
    print(f"   Found {len(items)} items in watchlist.")
    
    # Verify Types
    types = [i.get("type") for i in items]
    print(f"   Item Types: {types}")
    if "PREVIEW" not in types:
        print("[WARN] PREVIEW type missing (check mock logic)")
        
    # 3. Run Dashboard Generator
    print("3. Running dashboard_generator...")
    run_command("python3 -m src.dashboard.dashboard_generator")
    
    # 4. Verify HTML Rendering
    print("4. Verifying docs/index.html...")
    html_path = ROOT_DIR / "docs/index.html"
    content = html_path.read_text(encoding="utf-8")
    
    if "이번 주 전략적 관찰" not in content:
        print("[FAIL] Section header not found in HTML")
        sys.exit(1)
        
    if "확정된 사실이 아닌 구조적 시나리오입니다" not in content:
        print("[FAIL] Disclaimer text not found")
        sys.exit(1)
        
    # Check for at least one item theme presence
    first_item_theme = items[0].get("theme")
    if first_item_theme not in content:
        print(f"[FAIL] Watchlist item theme '{first_item_theme}' not found in HTML")
        sys.exit(1)

    print("[PASS] All checks passed!")

if __name__ == "__main__":
    main()
