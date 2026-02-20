import os
import json
import subprocess
from pathlib import Path
from src.topics.narrator.script_realization import ScriptRealizationBuilder

def verify_is97_3():
    print("\n" + "="*60)
    print("📋 IS-97-3 SCRIPT REALIZATION VERIFICATION")
    print("="*60)

    builder = ScriptRealizationBuilder()

    # 1. SETUP MOCK INPUTS
    print("\n[1/7] Preparing Mock Inputs...")
    
    units = [
        {
            "interpretation_id": "READY_SHORT_EXPLICIT",
            "target_sector": "TECH",
            "interpretation_key": "ROUTE_FIXATION",
            "derived_metrics_snapshot": {"pretext_score": 0.9},
            "evidence_tags": ["KR_POLICY", "EARNINGS_VERIFY"]
        },
        {
            "interpretation_id": "READY_LONG_IMPLICIT",
            "target_sector": "BIO",
            "interpretation_key": "STRUCTURAL_SHIFT",
            "derived_metrics_snapshot": {"pretext_score": 0.95},
            "evidence_tags": ["GLOBAL_INDEX"]
        },
        {
            "interpretation_id": "HOLD_MONITORING",
            "target_sector": "FINANCE",
            "interpretation_key": "WAIT_AND_SEE",
            "evidence_tags": ["FLOW_ROTATION"]
        },
        {
            "interpretation_id": "DROP_CASE",
            "interpretation_id": "DROP_CASE"
        }
    ]

    decisions = {
        "READY_SHORT_EXPLICIT": {"speakability_flag": "READY"},
        "READY_LONG_IMPLICIT": {"speakability_flag": "READY"},
        "HOLD_MONITORING": {"speakability_flag": "HOLD"},
        "DROP_CASE": {"speakability_flag": "DROP"}
    }

    skeletons = {
        "READY_SHORT_EXPLICIT": {"evidence_3": ["E1", "E2", "E3"], "hold_trigger": "정책 세부안"},
        "READY_LONG_IMPLICIT": {"evidence_3": ["LongE1"]},
        "HOLD_MONITORING": {"hold_trigger": "실적 발표"}
    }

    speak_maps = [
        {"topic_id": "READY_SHORT_EXPLICIT", "content_mode": "SHORT"},
        {"topic_id": "READY_LONG_IMPLICIT", "content_mode": "LONG"},
        {"topic_id": "HOLD_MONITORING", "content_mode": "MONITORING"}
    ]

    tone_locks = [
        {
            "topic_id": "READY_SHORT_EXPLICIT", 
            "persona": "POLICY_ANALYST", 
            "tone": "ASSERTIVE", 
            "risk_disclaimer_mode": "EXPLICIT"
        },
        {
            "topic_id": "READY_LONG_IMPLICIT", 
            "persona": "ECONOMIC_HUNTER", 
            "tone": "EXPLANATORY", 
            "risk_disclaimer_mode": "IMPLICIT"
        },
        {
            "topic_id": "HOLD_MONITORING", 
            "persona": "MARKET_OBSERVER", 
            "tone": "OBSERVATIONAL", 
            "risk_disclaimer_mode": "EXPLICIT"
        }
    ]

    inputs = {
        "interpretation_units": units,
        "speakability_decision": decisions,
        "narrative_skeleton": skeletons,
        "content_speak_map": speak_maps,
        "tone_persona_lock": tone_locks
    }

    # 2. RUN BUILDER
    print("[2/7] Running ScriptRealizationBuilder...")
    results = builder.build(inputs)
    res_map = {r["topic_id"]: r for r in results}

    # 3. CASE 1: READY + SHORT + EXPLICIT
    print("\n[3/7] Case 1: READY + SHORT + EXPLICIT")
    c1 = res_map.get("READY_SHORT_EXPLICIT")
    if c1 and "무서워하는 건" in c1["script"]["hook"] and "단, 정책 세부안 변동 시" in c1["script"]["risk_note"]:
        print("  ✅ Assertive hook + Explicit risk: PASS")
    else:
        print(f"  ❌ FAIL: {c1['script'] if c1 else 'None'}")

    # 4. CASE 2: READY + LONG + IMPLICIT
    print("\n[4/7] Case 2: READY + LONG + IMPLICIT")
    c2 = res_map.get("READY_LONG_IMPLICIT")
    if c2 and "데이터로만 정리할게" in c2["script"]["hook"] and "관찰 지속이 필요함" in c2["script"]["risk_note"]:
        print("  ✅ Explanatory hook + Implicit risk: PASS")
    else:
        print(f"  ❌ FAIL: {c2['script'] if c2 else 'None'}")

    # 5. CASE 3: HOLD + MONITORING
    print("\n[5/7] Case 3: HOLD + MONITORING")
    c3 = res_map.get("HOLD_MONITORING")
    if c3 and "'조건 대기' 구간이야" in c3["script"]["hook"] and "실적 발표만 기다리면 된다" in c3["script"]["closing"]:
        print("  ✅ Monitoring hook + Hold closing: PASS")
    else:
        print(f"  ❌ FAIL: {c3['script'] if c3 else 'None'}")

    # 6. CASE 4 & 5: Prioritization & Checklist
    print("\n[6/7] Case 4 & 5: Evidence & Checklist Format")
    if c1 and len(c1["script"]["evidence_3"]) == 3 and "지표 KR_POLICY:" in c1["script"]["checklist_3"][0]:
        print("  ✅ Evidence count + Checklist format: PASS")
    else:
        print(f"  ❌ FAIL: Evidence={len(c1['script']['evidence_3']) if c1 else '0'}, Checklist={c1['script']['checklist_3'][0] if c1 else ''}")

    # 7. CASE 6: DROP Exclusion
    print("\n[7/7] Case 6: DROP Exclusion")
    if "DROP_CASE" not in res_map:
        print("  ✅ DROP topic excluded: PASS")
    else:
        print("  ❌ FAIL: DROP topic present in output")

    # Final Save and Integrity
    builder.save(results, "data/decision/script_realization_test.json")
    
    print("\n[Integrity] Checking Constitutional Documents...")
    forbidden = ["docs/DATA_COLLECTION_MASTER.md", "docs/BASELINE_SIGNALS.md", "docs/ANOMALY_DETECTION_LOGIC.md"]
    for doc in forbidden:
        try:
            diff = subprocess.check_output(["git", "diff", "HEAD", "--", doc]).decode("utf-8")
            if diff:
                print(f"  ❌ {doc}: MODIFIED! (Integrity breach)")
            else:
                print(f"  ✅ {doc}: OK")
        except:
             print(f"  ⚠️ {doc}: Git check failed.")

    print("\nVERIFICATION COMPLETE")

if __name__ == "__main__":
    verify_is97_3()
