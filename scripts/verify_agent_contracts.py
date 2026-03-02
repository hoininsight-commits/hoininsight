#!/usr/bin/env python3
import json
import sys
from pathlib import Path
from datetime import datetime

def check_file(path: Path, required_fields: list = None):
    if not path.exists():
        print(f"❌ [FAIL] Missing: {path}")
        return False
    
    if required_fields:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            # Handle list or dict
            obj = data[0] if isinstance(data, list) and len(data) > 0 else data
            if not isinstance(obj, dict):
                print(f"❌ [FAIL] {path} is not a valid JSON object/list")
                return False
                
            for field in required_fields:
                if field not in obj:
                    print(f"❌ [FAIL] {path} missing required field: {field}")
                    return False
        except Exception as e:
            print(f"❌ [FAIL] {path} parse error: {e}")
            return False
            
    print(f"✅ [OK] {path}")
    return True

def verify():
    root = Path(".").resolve()
    now = datetime.now()
    ymd_path = now.strftime("%Y/%m/%d")
    ymd_dash = now.strftime("%Y-%m-%d")
    
    results = []
    
    print("--- Verifying Agent Contracts ---")
    
    # A1/A2 Outputs (Partial check as examples)
    results.append(check_file(root / f"data/topics/candidates/{ymd_path}/topic_candidates.json", ["dataset_id"]))
    
    # A3 Outputs
    results.append(check_file(root / "data/ops/narrative_intelligence_v2.json", ["narrative_score"]))
    results.append(check_file(root / f"data/ops/freshness/{ymd_path}/freshness_summary.json", ["overall_system_freshness_pct"]))
    
    # A4 Outputs
    results.append(check_file(root / f"data/decision/{ymd_path}/final_decision_card.json", ["card_version", "status"]))
    
    # A5 Outputs
    results.append(check_file(root / "data_outputs/ops/video_candidate_pool.json", ["video_ready"]))
    
    # A6 Outputs (Final Delivery)
    results.append(check_file(root / "docs/data/decision/today.json", ["picks"]))
    results.append(check_file(root / "docs/data/decision/manifest.json", ["files"]))
    
    if all(results):
        print("\n✅ All Agent Contracts Passed.")
        sys.exit(0)
    else:
        print("\n❌ Some Agent Contracts Failed.")
        sys.exit(1)

if __name__ == "__main__":
    verify()
