import os
import json
import subprocess
import hashlib
from pathlib import Path
from src.topics.content_pack.content_pack_layer import ContentPackLayer

def get_hash(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()

def verify_is98_2():
    print("\n" + "="*60)
    print("📋 IS-98-2 CONTENT PACK VERIFICATION")
    print("="*60)

    layer = ContentPackLayer()

    # 1. SETUP MOCK DATA
    print("\n[1/9] Preparing Mock Data...")
    
    units = [
        {
            "interpretation_id": "T1_READY",
            "target_sector": "TECH",
            "interpretation_key": "엔비디아 영업이익 66% 증가 및 750억 달러 달성",
            "evidence_tags": ["KR_POLICY", "EARNINGS_VERIFY"]
        },
        {
            "interpretation_id": "T2_HOLD_UNVERIFIED",
            "target_sector": "BIO",
            "interpretation_key": "임상 관찰 결과 12% 개선",
            "evidence_tags": ["FLOW_ROTATION"]
        }
    ]

    realizations = [
        {"topic_id": "T1_READY", "speakability": "READY", "script": {"hook": "H1", "claim": "C1", "evidence_3": ["E1", "E2", "E3"], "checklist_3": ["L1"], "closing": "Cl1", "risk_note": "R1"}},
        {"topic_id": "T2_HOLD_UNVERIFIED", "speakability": "HOLD", "script": {"hook": "H2", "claim": "C2", "evidence_3": ["E2-1"], "checklist_3": ["L2"], "closing": "Cl2", "risk_note": "R2"}}
    ]

    guarded = [
        {"topic_id": "T2_HOLD_UNVERIFIED", "speakability": "HOLD", "script": {"hook": "H2 guard", "claim": "C2 guard", "evidence_3": ["E2-1 guard"], "checklist_3": ["L2"], "closing": "Cl2 guard", "risk_note": "R2"}}
    ]

    citations = [
        {
            "topic_id": "T1_READY",
            "citations": [
                {"evidence_tag": "KR_POLICY", "status": "VERIFIED", "sources": [{"title": "S1", "url": "U1", "date": "D1"}]},
                {"evidence_tag": "EARNINGS_VERIFY", "status": "PARTIAL", "sources": [{"title": "S2", "url": "U2", "date": "D2"}]}
            ]
        },
        {
            "topic_id": "T2_HOLD_UNVERIFIED",
            "citations": [
                {"evidence_tag": "FLOW_ROTATION", "status": "UNVERIFIED", "sources": []}
            ]
        }
    ]

    mentionables = [
        {
            "topic_id": "T1_READY",
            "mentionables": [
                {"name": "삼성전자", "ticker_or_code": "005930", "why_must_say": [{"claim": "W1"}]},
                {"name": "SK하이닉스", "ticker_or_code": "000660", "why_must_say": [{"claim": "W2"}]},
                {"name": "NVIDIA", "ticker_or_code": "NVDA", "why_must_say": [{"claim": "W3"}]}
            ]
        }
    ]

    bundle = {
        "interpretation_units": units,
        "script_realization": realizations,
        "script_with_citation_guard": guarded,
        "evidence_citations": citations,
        "mentionables": mentionables
    }

    # 2. RUN BUILDER
    print("[2/9] Running ContentPackLayer...")
    results = layer.run(bundle)
    res_map = {r["topic_id"]: r for r in results}

    # 3. CASE 1: READY + Sufficiency
    print("\n[3/9] Case 1: READY + Sufficient Evidence")
    c1 = res_map.get("T1_READY")
    if c1 and len(c1["assets"]["shorts_script"]["evidence_3"]) == 3:
        print("  ✅ Evidence count 3: PASS")
    else:
        print(f"  ❌ FAIL: {c1['assets']['shorts_script'] if c1 else 'None'}")

    # 4. CASE 3: UNVERIFIED Guard Tone
    print("\n[4/9] Case 3: Unverified Guard Tone in long script")
    c2 = res_map.get("T2_HOLD_UNVERIFIED")
    if c2 and "guard" in c2["assets"]["long_script"]["sections"][0]["text"]:
        print("  ✅ Guard tone used for T2: PASS")
    else:
        print(f"  ❌ FAIL: {c2['assets']['long_script']['sections'] if c2 else 'None'}")

    # 5. CASE 4: Mentionables count
    print("\n[5/9] Case 4: Mentionables inclusion")
    if c1 and len(c1["assets"]["mentionables"]) == 3:
        print("  ✅ 3 stocks included in T1: PASS")
    else:
        print(f"  ❌ FAIL: {len(c1['assets']['mentionables']) if c1 else 0}")

    # 6. CASE 5: Source Integrity
    print("\n[6/9] Case 5: Source metadata integrity")
    source = c1["assets"]["evidence_sources"][0]["sources"][0]
    if source.get("url") == "U1" and source.get("date") == "D1":
        print("  ✅ Source URL/Date present: PASS")
    else:
        print(f"  ❌ FAIL: {source}")

    # 7. CASE 7: Determinism check
    print("\n[7/9] Case 7: Determinism check (Hash comparison)")
    results_again = layer.run(bundle)
    if get_hash(results) == get_hash(results_again):
        print("  ✅ Deterministic output (same hash): PASS")
    else:
        print("  ❌ FAIL: Non-deterministic output")

    # 8. KEY NUMBERS EXTRACTION
    print("\n[8/9] Key Numbers Extraction check")
    if c1 and "66%" in c1["assets"]["decision_card"]["key_numbers"]:
        print("  ✅ '66%' extracted: PASS")
    else:
        print(f"  ❌ FAIL: {c1['assets']['decision_card']['key_numbers'] if c1 else 'None'}")

    # 9. INTEGRITY & SCHEMA
    print("\n[9/9] Schema & Integrity check")
    if c1 and "assets" in c1 and "governance" in c1:
        print("  ✅ Basic schema fields: PASS")
    else:
        print("  ❌ FAIL: Schema missing fields")

    # SAVE
    layer.save(results, "data/decision/content_pack_test.json")
    
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
    verify_is98_2()
