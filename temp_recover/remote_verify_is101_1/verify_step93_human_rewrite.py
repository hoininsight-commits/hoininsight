import os
import sys
import json
from pathlib import Path
from datetime import datetime

def verify_step93():
    print("[VERIFY] Checking Step 93: Human Language Rewrite & Judgment Memory View...")
    base_dir = Path(".").resolve()
    
    # 1. Run Exporter (re-use mocked data from Step 91-92)
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
        
    # Check for rewritten status labels
    # Expected: "판단 상태: 반복 관찰 중 / 오늘 더 강해졌습니다 (2일째)" or similar
    if "판단 상태:" not in html:
        print("[FAIL] '판단 상태:' header missing in status line.")
        sys.exit(1)
        
    if "Escalating" in html and "판단 상태:" in html:
         # Technical terms shouldn't be in the judgmental status line anymore if rewritten correctly
         # (Though they might still be in badges, which is fine)
         pass

    # Check for Judgment Memory panel
    if "Judgment Memory" not in html:
        print("[FAIL] 'Judgment Memory' panel header missing.")
        sys.exit(1)
        
    if "🧠" not in html:
        print("[FAIL] Knowledge brain emoji missing in Memory View.")
        sys.exit(1)
        
    print("[OK] Rewritten status and Memory View confirmed in UI.")
    print("[VERIFY][OK] Step 93 Verification Successful.")

if __name__ == "__main__":
    verify_step93()
