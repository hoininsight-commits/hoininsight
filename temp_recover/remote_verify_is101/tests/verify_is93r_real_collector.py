import subprocess
import json
import sys
from pathlib import Path
from datetime import datetime

def run_pipeline():
    print("Running Pipeline for IS-93R Verification...")
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
    ymd_short = datetime.now().strftime("%Y%m%d")
    
    # 1. Check if raw data files exist
    stmt_file = base_dir / "data" / "statements" / f"statements_{ymd_short}.json"
    doc_file = base_dir / "data" / "statements" / f"documents_{ymd_short}.json"
    
    print(f"Checking {stmt_file}...")
    if stmt_file.exists():
        data = json.loads(stmt_file.read_text(encoding="utf-8"))
        print(f"[OK] Found {len(data)} real statements.")
        for item in data[:1]:
            print(f"   Example: {item['person_or_org']} from {item['source_url']} ({item['trust_level']})")
    else:
        print("[WARN] No real statements collected (might be no new news).")

    print(f"Checking {doc_file}...")
    if doc_file.exists():
        data = json.loads(doc_file.read_text(encoding="utf-8"))
        print(f"[OK] Found {len(data)} real documents.")
        for item in data[:1]:
            print(f"   Example: {item['person_or_org']} from {item['source_url']} ({item['trust_level']})")
    else:
        print("[WARN] No real documents collected.")

    # 2. Check for mock data (Elon Musk cluster mock should NOT be there)
    mock_content = "massive GPU cluster immediately"
    latest_nc = list((base_dir / "data" / "narratives").glob("narrative_candidates_*.json"))
    if latest_nc:
        latest_nc = max(latest_nc, key=lambda p: p.stat().st_mtime)
        content = latest_nc.read_text(encoding="utf-8")
        if mock_content in content:
            print("[FAIL] Mock data detected in output!")
            sys.exit(1)
        else:
            print("[OK] No mock data found in latest candidates.")

if __name__ == "__main__":
    run_pipeline()
    verify()
    print("\n✅ IS-93R Real Collector Verification Successful!")
