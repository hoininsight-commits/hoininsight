import sys
import json
from pathlib import Path

def verify_collection_status():
    status_file = Path("data/dashboard/collection_status.json")
    if not status_file.exists():
        print("[VERIFY][FAIL] collection_status.json not found")
        sys.exit(1)

    try:
        data = json.load(open(status_file))
        has_mock = False
        warmup_count = 0
        
        for ds_id, info in data.items():
            reason = info.get("reason", "").lower()
            status = info.get("status", "")
            
            # Check for mock
            if "mock" in reason:
                print(f"[VERIFY][FAIL] Dataset {ds_id} using mock data! Reason: {reason}")
                has_mock = True
                
            # Check for warmup
            if status == "WARMUP":
                warmup_count += 1
                
        if has_mock:
            print("[VERIFY][FAIL] System contains mock data substitutions.")
            sys.exit(1)
            
        print("[VERIFY][OK] No mock substitution in production pipeline")
        
        if warmup_count > 0:
            print(f"[VERIFY][OK] Warm-up states recorded for derived datasets (count={warmup_count})")
        else:
            print("[VERIFY][INFO] No WARMUP states found (maybe history passed?)")
            
    except Exception as e:
        print(f"[VERIFY][FAIL] Verification script error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    verify_collection_status()
