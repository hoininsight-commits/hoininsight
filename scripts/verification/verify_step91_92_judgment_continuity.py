import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

def verify_step91_92():
    print("[VERIFY] Checking Step 91-92: Judgment Continuity & Narrative Drift...")
    base_dir = Path(".").resolve()
    memory_dir = base_dir / "data" / "snapshots" / "memory"
    memory_dir.mkdir(parents=True, exist_ok=True)
    
    today_ymd = datetime.utcnow().strftime("%Y-%m-%d")
    prev_ymd = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    # 1. Mock Yesterday's Snapshot for Continuity Check
    # We use a known title from 2026-01-27 to match typical test cases
    test_title = "Global Semiconductor Alliance mandates new supply chain standard for 2026, forcing all member firms to comply with immediate effect."
    
    mock_prev_snap = {
        "date": prev_ymd,
        "top_signal": {
            "title": test_title,
            "trigger": "Mechanism Activation",
            "intensity": "FLASH",
            "rhythm": "STRUCTURE_FLOW"
        },
        "entities": []
    }
    prev_file = memory_dir / f"{prev_ymd}.json"
    prev_file.write_text(json.dumps(mock_prev_snap, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[RUN] Mocked yesterday's snapshot at {prev_file}")
    
    # 2. Run Exporter to generate today's JSON with Continuity Logic
    print(f"[RUN] Running TopicExporter to process {today_ymd}...")
    os.system(f"python3 -c \"from src.dashboard.topic_exporter import TopicExporter; from pathlib import Path; TopicExporter(Path('.').resolve()).run('{today_ymd}')\"")
    
    # 3. Verify JSON contents
    json_path = base_dir / "docs" / "topics" / "items" / f"{today_ymd}__top1.json"
        
    print(f"[CHECK] Inspecting {json_path.name}...")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    stack = data.get("judgment_stack", {})
    drift = data.get("narrative_drift", {})
    axis = data.get("interpretation_axis", "")
    
    if not stack or "state_label" not in stack:
        print("[FAIL] 'judgment_stack' missing or incomplete in JSON.")
        sys.exit(1)
    
    if not drift or "label" not in drift:
        print("[FAIL] 'narrative_drift' missing or incomplete in JSON.")
        sys.exit(1)
        
    if not axis:
        print("[FAIL] 'interpretation_axis' missing in JSON.")
        sys.exit(1)
        
    print(f"[OK] Judgment Status: {stack.get('state_label')}")
    print(f"[OK] Narrative Drift: {drift.get('label')}")
    print(f"[OK] Axis: {axis}")

    # 4. UI check: Ensure it's in index.html
    print("[RUN] Regenerating dashboard UI...")
    os.system("python3 -m src.dashboard.dashboard_generator")
    
    index_path = Path("docs/index.html")
    with open(index_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
        
    if "judgment-status-line" not in html_content:
        print("[FAIL] 'judgment-status-line' class missing in index.html.")
        sys.exit(1)
        
    if "narrative-drift-label" not in html_content:
        print("[FAIL] 'narrative-drift-label' class missing in index.html.")
        sys.exit(1)

    print("[VERIFY][OK] Step 91-92 Verification Successful.")

if __name__ == "__main__":
    verify_step91_92()
