import os
import json
from pathlib import Path
from datetime import datetime
from src.collectors.policy_collector import run_collector as run_policy
from src.collectors.market_collectors import collect_is95_market_flow
from src.collectors.corporate_action_connector import collect_is95_pretext_layer

def verify_is95_1():
    print("\n" + "="*60)
    print("📋 IS-95-1 DATA SOURCE EXPANSION VERIFICATION")
    print("="*60)

    ymd = datetime.now().strftime("%Y-%m-%d")
    base_dir = Path(".")
    
    # 1. Documentation Check
    print("\n[1/3] Checking Constitutional Docs...")
    docs_to_check = [
        "docs/DATA_COLLECTION_MASTER.md",
        "docs/BASELINE_SIGNALS.md",
        "docs/ANOMALY_DETECTION_LOGIC.md",
        "docs/IS-95-1_METRICS_DEFINITION.md"
    ]
    
    for doc in docs_to_check:
        p = base_dir / doc
        if p.exists():
            content = p.read_text(encoding='utf-8')
            if doc != "docs/IS-95-1_METRICS_DEFINITION.md":
                if "IS-95-1 ADDON STATEMENT" in content:
                    print(f"  ✅ {doc}: Found IS-95-1 Add-on Statement")
                else:
                    print(f"  ❌ {doc}: Missing IS-95-1 Add-on Statement")
            
            if doc == "docs/DATA_COLLECTION_MASTER.md":
                if "IS-95-1 ADDON: ECONOMY HUNTER OBSERVATION LAYER" in content:
                    print(f"  ✅ {doc}: Found IS-95-1 Section")
                else:
                    print(f"  ❌ {doc}: Missing IS-95-1 Section")
        else:
            print(f"  ❌ {doc}: File not found")

    # 2. Collector Execution
    print("\n[2/3] Executing Observation Layer Collectors...")
    try:
        run_policy()
        collect_is95_market_flow()
        collect_is95_pretext_layer(base_dir, ymd)
        print("  ✅ All Observation Collectors Executed Successfully")
    except Exception as e:
        print(f"  ❌ Collector Execution Failed: {e}")

    # 3. Data Tag Verification
    print("\n[3/3] Verifying Data Grouping Tags...")
    
    # Check Policy Flow
    policy_path = base_dir / f"data/raw/policy/is95_policy_flow/{ymd}/observation_layer.csv"
    if policy_path.exists():
        content = policy_path.read_text(encoding='utf-8')
        if "KR_POLICY" in content and "US_POLICY" in content:
            print(f"  ✅ Policy Data: Found KR_POLICY and US_POLICY tags")
        else:
            print(f"  ❌ Policy Data: Missing expected tags")
    else:
        print(f"  ❌ Policy Data: File not found at {policy_path}")

    # Check Global Index / Rotation
    global_path = base_dir / f"data/raw/is95_global_index/{ymd}.jsonl"
    rotation_path = base_dir / f"data/raw/is95_flow_rotation/{ymd}.jsonl"
    
    if global_path.exists() and "GLOBAL_INDEX" in global_path.read_text():
        print(f"  ✅ Market Data: Found GLOBAL_INDEX tag")
    else:
        print(f"  ❌ Market Data: GLOBAL_INDEX tag not found")
        
    if rotation_path.exists() and "FLOW_ROTATION" in rotation_path.read_text():
        print(f"  ✅ Market Data: Found FLOW_ROTATION tag")
    else:
        print(f"  ❌ Market Data: FLOW_ROTATION tag not found")

    # Check Pretext / Earnings
    fact_path = base_dir / f"data/facts/is95_observation_layer_{ymd.replace('-', '')}.json"
    if fact_path.exists():
        facts = json.loads(fact_path.read_text())
        tags = [f.get("tag") for f in facts]
        if "PRETEXT_VALIDATION" in tags and "EARNINGS_VERIFY" in tags:
            print(f"  ✅ Fact Data: Found PRETEXT_VALIDATION and EARNINGS_VERIFY tags")
            for f in facts:
                if f.get("tag") == "PRETEXT_VALIDATION" and "pretext_score" in f:
                    print(f"    - Found pretext_score: {f['pretext_score']}")
                if f.get("tag") == "EARNINGS_VERIFY" and "earnings_shock_flag" in f:
                    print(f"    - Found earnings_shock_flag: {f['earnings_shock_flag']}")
        else:
            print(f"  ❌ Fact Data: Missing expected tags")
    else:
        print(f"  ❌ Fact Data: File not found at {fact_path}")

    print("\n" + "="*60)
    print("VERIFICATION COMPLETE")
    print("="*60 + "\n")

if __name__ == "__main__":
    verify_is95_1()
