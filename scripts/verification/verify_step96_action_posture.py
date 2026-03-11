import os
import sys
import json
from pathlib import Path

def verify_step96():
    print("[VERIFY] Checking Step 96: Action Posture Layer...")
    base_dir = Path(".").resolve()
    
    # 1. Run Exporter (reuse mocked data or rely on existing mocks)
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
        
    # Check for Action Posture Block
    if "action-posture-block" not in html:
        print("[FAIL] 'action-posture-block' class missing in HTML.")
        sys.exit(1)
        
    # Check for Mandatory Safety Notice
    if "투자 조언이나 행동 지시가 아니며" not in html:
        print("[FAIL] Mandatory safety notice missing.")
        sys.exit(1)
    
    # Check for Posture Headline
    if "현재 시장에 대한 적절한 자세:" not in html:
        print("[FAIL] Posture headline missing.")
        sys.exit(1)
        
    print("[OK] Action Posture block found with safety notice.")
    print("[VERIFY][OK] Step 96 Verification Successful.")

if __name__ == "__main__":
    verify_step96()
