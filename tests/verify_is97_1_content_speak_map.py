import os
import json
import subprocess
from pathlib import Path
from src.engine.content.content_speak_map import ContentSpeakMapBuilder

def verify_is97_1():
    print("\n" + "="*60)
    print("📋 IS-97-1 CONTENT SPEAK MAP VERIFICATION")
    print("="*60)

    base_dir = Path(".")
    data_dir = base_dir / "data/decision"
    data_dir.mkdir(parents=True, exist_ok=True)

    # 1. Setup Mock Inputs
    print("\n[1/4] Setting up Mock Inputs (IS-96 outputs)...")
    
    interpretation_units = [
        {
            "interpretation_id": "READY_LONG",
            "target_sector": "TECH",
            "interpretation_key": "ROUTE_FIXATION",
            "why_now_type": "Schedule",
            "evidence_tags": ["KR_POLICY", "FLOW_ROTATION"],
            "derived_metrics_snapshot": {"pretext_score": 0.95, "policy_execution_gap": 0.1}
        },
        {
            "interpretation_id": "READY_SHORT",
            "target_sector": "BIO",
            "interpretation_key": "EVENT_DRIVEN",
            "why_now_type": "News",
            "evidence_tags": ["KR_POLICY"],
            "derived_metrics_snapshot": {"pretext_score": 0.85, "policy_execution_gap": 0.3}
        },
        {
            "interpretation_id": "HOLD_CASE",
            "target_sector": "FINANCE",
            "why_now_type": "State",
            "evidence_tags": ["FLOW_ROTATION"],
            "derived_metrics_snapshot": {"pretext_score": 0.75}
        },
        {
            "interpretation_id": "DROP_CASE",
            "target_sector": "GAME",
            "derived_metrics_snapshot": {"pretext_score": 0.50}
        }
    ]
    
    speakability_decision = {
        "READY_LONG": {"speakability_flag": "READY"},
        "READY_SHORT": {"speakability_flag": "READY"},
        "HOLD_CASE": {"speakability_flag": "HOLD"},
        "DROP_CASE": {"speakability_flag": "DROP"}
    }
    
    narrative_skeleton = {
        "READY_LONG": {"evidence_3": ["E1", "E2", "E3"]},
        "READY_SHORT": {"evidence_3": ["E-Bio"]},
        "HOLD_CASE": {"hold_trigger": "Wait for earnings"},
        "DROP_CASE": {"drop_note": "Insufficient pretext"}
    }

    with open(data_dir / "interpretation_units.json", "w") as f:
        json.dump(interpretation_units, f)
    with open(data_dir / "speakability_decision.json", "w") as f:
        json.dump(speakability_decision, f)
    with open(data_dir / "narrative_skeleton.json", "w") as f:
        json.dump(narrative_skeleton, f)

    print("  ✅ Mock data assets created.")

    # 2. Execute Builder
    print("\n[2/4] Executing ContentSpeakMapBuilder...")
    builder = ContentSpeakMapBuilder()
    results = builder.build()
    
    if os.path.exists(data_dir / "content_speak_map.json"):
        print("  ✅ content_speak_map.json: CREATED")
    else:
        print("  ❌ content_speak_map.json: MISSING")
        return

    # 3. Verify Deterministic Routing
    print("\n[3/4] Verifying Deterministic Routing...")
    
    test_results = {r["topic_id"]: r for r in results}
    
    # Case: READY_LONG
    r_long = test_results.get("READY_LONG")
    if r_long and r_long["content_mode"] == "LONG" and r_long["content_count"] == 2:
        print("  ✅ READY_LONG (Pretext 0.95) -> LONG/2: PASS")
    else:
        print(f"  ❌ READY_LONG: FAIL (Got {r_long['content_mode'] if r_long else 'None'})")

    # Case: READY_SHORT
    r_short = test_results.get("READY_SHORT")
    if r_short and r_short["content_mode"] == "SHORT" and r_short["content_count"] == 1:
        print("  ✅ READY_SHORT (Pretext 0.85) -> SHORT/1: PASS")
    else:
        print(f"  ❌ READY_SHORT: FAIL (Got {r_short['content_mode'] if r_short else 'None'})")

    # Case: HOLD_CASE
    r_hold = test_results.get("HOLD_CASE")
    if r_hold and r_hold["content_mode"] == "HOLD" and "Wait for earnings" in r_hold["supporting_angles"]:
        print("  ✅ HOLD_CASE -> HOLD + trigger: PASS")
    else:
        print(f"  ❌ HOLD_CASE: FAIL")

    # Case: DROP_CASE
    r_drop = test_results.get("DROP_CASE")
    if r_drop and r_drop["content_mode"] == "HOLD" and r_drop["content_count"] == 0:
        print("  ✅ DROP_CASE -> HOLD/0: PASS")
    else:
        print(f"  ❌ DROP_CASE: FAIL")

    # 4. Constitutional Integrity Check (Add-only)
    print("\n[4/4] Constitutional Integrity Check (Add-only)...")
    forbidden = [
        "docs/DATA_COLLECTION_MASTER.md",
        "docs/BASELINE_SIGNALS.md",
        "docs/ANOMALY_DETECTION_LOGIC.md"
    ]
    for doc in forbidden:
        try:
            diff = subprocess.check_output(["git", "diff", "HEAD", "--", doc]).decode("utf-8")
            if diff:
                print(f"  ❌ {doc}: MODIFIED! (Add-only breach)")
            else:
                print(f"  ✅ {doc}: No modifications.")
        except:
             print(f"  ⚠️ {doc}: Git check failed.")

    print("\n" + "="*60)
    print("VERIFICATION COMPLETE")
    print("="*60 + "\n")

if __name__ == "__main__":
    verify_is97_1()
