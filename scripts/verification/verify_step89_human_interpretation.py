import os
import sys
import json
from pathlib import Path

def verify_step89():
    print("[VERIFY] Checking Step 89: Human Interpretation Layer...")
    
    # 1. Trigger Exporter to generate latest JSON
    print("[RUN] Running TopicExporter to capture latest interpretation...")
    os.system("python3 -m src.dashboard.topic_exporter")
    
    # 2. Check Static JSON for the human_interpretation field
    docs_dir = Path("docs/topics/items")
    json_files = list(docs_dir.glob("*__top1.json"))
    
    if not json_files:
        print("[FAIL] No Top-1 JSON files found in docs/topics/items")
        sys.exit(1)
        
    latest_json = sorted(json_files)[-1]
    print(f"[CHECK] Inspecting {latest_json.name}...")
    
    with open(latest_json, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    if "human_interpretation" not in data:
        print("[FAIL] 'human_interpretation' field missing in static JSON.")
        sys.exit(1)
        
    interpretation = data["human_interpretation"]
    print(f"[OK] Interpretation found: {interpretation[:50]}...")
    
    # 3. Safety Check: Prohibited words
    forbidden = ["매수", "수익", "투자", "추천", "가격"]
    for word in forbidden:
        if word in interpretation:
            print(f"[FAIL] Forbidden word '{word}' found in interpretation!")
            sys.exit(1)
    print("[OK] Safety check passed.")

    # 4. UI check: Ensure it's in index.html
    print("[RUN] Regenerating dashboard UI...")
    os.system("python3 -m src.dashboard.dashboard_generator")
    
    index_path = Path("docs/index.html")
    with open(index_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
        
    if "top1-interpretation" not in html_content:
        print("[FAIL] 'top1-interpretation' class missing in index.html.")
        sys.exit(1)
        
    if "어째서 지금 이 토픽인가" not in html_content:
        print("[FAIL] Interpretation header text missing in UI.")
        sys.exit(1)

    print("[VERIFY][OK] Step 89 Verification Successful.")

if __name__ == "__main__":
    verify_step89()
