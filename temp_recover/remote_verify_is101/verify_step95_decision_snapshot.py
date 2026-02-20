import os
import sys
import json
from pathlib import Path

def verify_step95():
    print("[VERIFY] Checking Step 95: Decision Speed Layer (10-second Snapshot)...")
    base_dir = Path(".").resolve()
    
    # 1. Run Exporter (reuse mocked data from previous steps or rely on existing mocks)
    # We assume data/ops/structural_top1_today.json is present from Step 91-92 verification
    print("[RUN] Running TopicExporter...")
    os.system("python3 -m src.dashboard.topic_exporter")
    
    # 2. Run Dashboard Generator
    print("[RUN] Regenerating dashboard...")
    os.system("python3 -m src.dashboard.dashboard_generator")
    
    # 3. Inspect index.html
    index_path = base_dir / "docs" / "index.html"
    if not index_path.exists():
        print("[FAIL] index.html missing.")
        sys.exit(1)
        
    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()
        
    # Check for Decision Snapshot Block
    if "decision-snapshot-block" not in html:
        print("[FAIL] 'decision-snapshot-block' class missing in HTML.")
        sys.exit(1)
        
    if "⚡" not in html:
        print("[FAIL] Snapshot icon (⚡) missing in UI.")
        sys.exit(1)
        
    # Check for content keywords (based on mocked engine state "ESCALATING" or "NEW")
    if "구조적" not in html:
        print("[FAIL] Expected keyword '구조적' missing in snapshot summary.")
        sys.exit(1)
        
    print("[OK] Decision Snapshot block found with correct icon and text.")
    print("[VERIFY][OK] Step 95 Verification Successful.")

if __name__ == "__main__":
    verify_step95()
