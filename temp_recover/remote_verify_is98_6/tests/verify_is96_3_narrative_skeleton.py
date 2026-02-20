import os
import json
import subprocess
from pathlib import Path
from src.topics.narrator.narrative_skeleton import build_narrative_skeleton

def verify_is96_3():
    print("\n" + "="*60)
    print("📋 IS-96-3 NARRATIVE SKELETON VERIFICATION")
    print("="*60)

    base_dir = Path(".")
    
    # 1. File Existence Check
    print("\n[1/3] Checking Required Files & Modules...")
    files = [
        "docs/engine/IS-96-3_NARRATIVE_SKELETON.md",
        "src/topics/narrator/narrative_skeleton.py"
    ]
    for f in files:
        if (base_dir / f).exists():
            print(f"  ✅ {f}: FOUND")
        else:
            print(f"  ❌ {f}: MISSING")

    # 2. Synthetic Test Cases
    print("\n[2/3] Running 3 Synthetic Test Cases...")
    
    # Common Interpretation Unit Fragment
    unit_base = {
        "target_sector": "SEMICONDUCTOR_INFRA",
        "interpretation_key": "STRUCTURAL_ROUTE_FIXATION",
        "structural_narrative": "정책 집행과 연동된 인프라 수급 병목 해소 구간 진입",
        "evidence_tags": ["KR_POLICY", "FLOW_ROTATION", "PRETEXT_VALIDATION"],
        "derived_metrics_snapshot": {"pretext_score": 0.92}
    }

    test_cases = [
        {
            "name": "READY Case",
            "speakability": {
                "speakability_flag": "READY",
                "speakability_reasons": ["High pretext score", "Policy execution verified"]
            },
            "expect_fields": ["hook", "claim", "evidence_3", "checklist_3", "what_to_avoid"],
            "avoid_fields": ["hold_trigger", "drop_note"]
        },
        {
            "name": "HOLD Case",
            "speakability": {
                "speakability_flag": "HOLD",
                "speakability_reasons": ["Pretext strength moderate", "Earnings pending"]
            },
            "expect_fields": ["hook", "claim", "evidence_3", "checklist_3", "hold_trigger"],
            "avoid_fields": ["drop_note"]
        },
        {
            "name": "DROP Case",
            "speakability": {
                "speakability_flag": "DROP",
                "speakability_reasons": ["Low pretext score"]
            },
            "expect_fields": ["drop_note"],
            "avoid_fields": ["hook", "claim", "evidence_3", "checklist_3", "hold_trigger"]
        }
    ]

    for tc in test_cases:
        result = build_narrative_skeleton(unit_base, tc["speakability"])
        
        pass_tc = True
        for field in tc["expect_fields"]:
            if field not in result:
                print(f"  ❌ {tc['name']}: Missing expected field '{field}'")
                pass_tc = False
        
        for field in tc["avoid_fields"]:
            if field in result:
                print(f"  ❌ {tc['name']}: Found forbidden field '{field}'")
                pass_tc = False
        
        if pass_tc:
            print(f"  ✅ {tc['name']}: PASS (Flag={result['speakability_flag']})")
            if tc["name"] == "READY Case":
                print(f"     [Sample Hook] {result['hook']}")
            if tc["name"] == "HOLD Case":
                print(f"     [Hold Trigger] {result['hold_trigger']}")

    # 3. Constitutional Integrity Check
    print("\n[3/3] Constitutional Integrity Check (Add-only)...")
    forbidden = [
        "docs/DATA_COLLECTION_MASTER.md",
        "docs/BASELINE_SIGNALS.md",
        "docs/ANOMALY_DETECTION_LOGIC.md"
    ]
    BASELINE = "d17bb99dc"
    for doc in forbidden:
        try:
            diff = subprocess.check_output(["git", "diff", "HEAD", "--", doc]).decode("utf-8")
            if diff:
                print(f"  ❌ {doc}: UNSAVED MODIFICATIONS found!")
            else:
                print(f"  ✅ {doc}: No modifications.")
        except:
             print(f"  ⚠️ {doc}: Git check failed.")

    print("\n" + "="*60)
    print("VERIFICATION COMPLETE")
    print("="*60 + "\n")

if __name__ == "__main__":
    verify_is96_3()
