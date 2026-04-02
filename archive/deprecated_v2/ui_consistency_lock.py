import json
import requests
import os
import time
from pathlib import Path
from datetime import datetime

# SSOT Configuration
UI_URL = "https://hoininsight-commits.github.io/hoininsight/ui/index.html"
JSON_URL = "https://hoininsight-commits.github.io/hoininsight/data/ui/ui_operator_view.json"
JSON_PATH = Path("docs/data/ui/ui_operator_view.json")
REPORT_PATH = Path("data/ops/ui_consistency_report.json")

def check_consistency(project_root: Path):
    """
    STEP-L-2: UI ↔ SSOT Consistency Lock
    Ensures that the server data exactly matches the local JSON contract.
    If they mismatch, it means the deployment is stale or failed.
    """
    json_local_path = project_root / JSON_PATH
    report_path = project_root / REPORT_PATH
    
    print(f"\n[CONSISTENCY] >>> VERIFYING UI ↔ SSOT consistency (Deployment Audit)...")
    
    # 1. Load Local JSON (The Target Truth)
    if not json_local_path.exists():
        print(f"[CONSISTENCY] ❌ Local JSON missing at {json_local_path}")
        return ["LOCAL_JSON_MISSING"]
        
    with open(json_local_path, "r", encoding="utf-8") as f:
        local_data = json.load(f)
        
    # 2. Fetch Server JSON (The Published Truth)
    try:
        # Cache buster is CRITICAL for GitHub Pages
        buster = int(time.time())
        fetch_url = f"{JSON_URL}?v={buster}"
        print(f"[CONSISTENCY] Fetching [GET] {fetch_url}...")
        response = requests.get(fetch_url, timeout=10)
        response.raise_for_status()
        server_data = response.json()
    except Exception as e:
        print(f"[CONSISTENCY] ❌ Failed to fetch server JSON: {e}")
        return [f"FETCH_FAILED:{e}"]

    failures = []

    # 3. Deep Comparison of Core Values
    keys_to_check = ["today_topic", "action", "why_now", "timing", "confidence", "risk", "allocation"]
    
    for key in keys_to_check:
        local_val = local_data.get(key)
        server_val = server_data.get(key)
        
        # Rounding for float comparison (confidence, allocation)
        if isinstance(local_val, float):
            if abs(local_val - server_val) > 0.001:
                print(f"[CONSISTENCY] ⚠️ Mismatch in {key}: Local={local_val}, Server={server_val}")
                failures.append(key)
            else:
                print(f"[CONSISTENCY] ✅ {key} aligned.")
        else:
            if local_val != server_val:
                print(f"[CONSISTENCY] ⚠️ Mismatch in {key}: Local='{local_val}', Server='{server_val}'")
                failures.append(key)
            else:
                print(f"[CONSISTENCY] ✅ {key} aligned.")

    # 4. Check Stocks
    local_stocks = [s.get("name") for s in local_data.get("top_stocks", [])]
    server_stocks = [s.get("name") for s in server_data.get("top_stocks", [])]
    
    if set(local_stocks) != set(server_stocks):
        print(f"[CONSISTENCY] ⚠️ Stock list mismatch: Local={local_stocks}, Server={server_stocks}")
        failures.append("top_stocks")
    else:
        print(f"[CONSISTENCY] ✅ Stock list aligned.")

    # 5. Generate Report
    status = "PASS" if not failures else "FAIL"
    report = {
        "status": status,
        "failures": failures,
        "local_timestamp": local_data.get("last_updated"),
        "server_timestamp": server_data.get("last_updated"),
        "check_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
        
    print(f"[CONSISTENCY] <<< VERIFICATION COMPLETED. Status: {status}")
    return failures

if __name__ == "__main__":
    p_root = Path(__file__).parent.parent.parent
    check_consistency(p_root)
