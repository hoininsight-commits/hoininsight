import subprocess
import json
import sys
from pathlib import Path

def run_pipeline():
    print("Running Pipeline...")
    result = subprocess.run(
        [sys.executable, "src/issuesignal/run_issuesignal.py"],
        capture_output=True,
        text=True
    )
    print(result.stdout)
    if result.returncode != 0:
        print(f"Pipeline failed: {result.stderr}")
        sys.exit(1)

def verify():
    base_dir = Path(".")
    
    # 1. Check if narrative candidates were generated with statements
    nc_files = list((base_dir / "data" / "narratives").glob("narrative_candidates_*.json"))
    if not nc_files:
        print("[FAIL] narrative_candidates_*.json not found")
        sys.exit(1)
    
    latest_nc = max(nc_files, key=lambda p: p.stat().st_mtime)
    with open(latest_nc, "r", encoding="utf-8") as f:
        data = json.load(f)
        candidates = data.get("candidates", [])
        stmt_candidates = [c for c in candidates if "NC-STMT-" in c.get("id", "")]
        
        print(f"Found {len(stmt_candidates)} statement candidates in fusion output.")
        if len(stmt_candidates) == 0:
            print("[FAIL] No statement candidates found in fusion output")
            sys.exit(1)
            
    # 2. Check if main issue pack includes them
    issue_files = list((base_dir / "data" / "issuesignal" / "packs").glob("ISSUE-*.json"))
    if not issue_files:
        print("[FAIL] ISSUE-*.json not found")
        sys.exit(1)
        
    latest_issue = max(issue_files, key=lambda p: p.stat().st_mtime)
    with open(latest_issue, "r", encoding="utf-8") as f:
        issue_data = json.load(f)
        if "narrative_candidates" not in issue_data:
            print("[FAIL] narrative_candidates missing in main issue pack")
            sys.exit(1)

    # 3. Check Dashboard HTML
    dash_path = base_dir / "dashboard" / "index.html"
    if not dash_path.exists():
        dash_path = base_dir / "docs" / "index.html"
        
    if not dash_path.exists():
        print("[FAIL] dashboard/index.html not found")
        sys.exit(1)
        
    html_content = dash_path.read_text(encoding="utf-8")
    if "오늘의 해석 구도" not in html_content:
         print("[WARN] 오늘의 해석 구도 missing (IS-92)")
    
    if "발언/문서 기반 이슈 후보" in html_content:
        print("[OK] Dashboard contains Statement Layer section.")
    else:
        print("[FAIL] Dashboard section missing.")
        sys.exit(1)

    print("\n✅ IS-93 Verification Successful!")

def run_dashboard_generator():
    print("Running Dashboard Generator...")
    result = subprocess.run(
        [sys.executable, "-m", "src.dashboard.dashboard_generator"],
        capture_output=True,
        text=True
    )
    print(result.stdout)
    if result.returncode != 0:
        print(f"Dashboard Generator failed: {result.stderr}")
        sys.exit(1)

if __name__ == "__main__":
    run_pipeline()
    run_dashboard_generator()
    verify()
    print("\n✅ IS-93 Verification Successful!")
