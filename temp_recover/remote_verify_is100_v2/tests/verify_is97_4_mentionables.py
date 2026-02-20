import os
import json
import subprocess
from pathlib import Path
from src.topics.mentionables.mentionables_layer import MentionablesLayer

def verify_is97_4():
    print("\n" + "="*60)
    print("📋 IS-97-4 MENTIONABLES LAYER VERIFICATION")
    print("="*60)

    layer = MentionablesLayer()

    # MOCK DATA
    print("\n[1/8] Preparing Mock Data...")
    
    # 1. READY + Policy keywords -> Inclusion with 2+ evidence
    units = [
        {
            "interpretation_id": "T1_POLICY",
            "target_sector": "금융",
            "interpretation_key": "밸류업 가이드라인 발표 및 ISA 혜택",
            "evidence_tags": ["KR_POLICY", "FLOW_ROTATION"]
        },
        # 2. READY + AI Infra keywords -> Inclusion
        {
            "interpretation_id": "T2_INFRA",
            "target_sector": "전력",
            "interpretation_key": "데이터센터 전력망 송전 병목",
            "evidence_tags": ["PRETEXT_VALIDATION", "EARNINGS_VERIFY"]
        },
        # 4. 1 evidence only -> Exclusion
        {
            "interpretation_id": "T4_WEAK",
            "target_sector": "반도체",
            "interpretation_key": "HBM 수요 폭증",
            "evidence_tags": ["EARNINGS_VERIFY"]
        },
        # 5. Keyword mismatch -> Exclusion
        {
            "interpretation_id": "T5_MISMATCH",
            "target_sector": "엔터",
            "interpretation_key": "그냥 평범한 뉴스",
            "evidence_tags": ["KR_POLICY", "FLOW_ROTATION"]
        }
    ]
    
    realizations = [
        {"topic_id": "T1_POLICY", "speakability": "READY"},
        {"topic_id": "T2_INFRA", "speakability": "READY"},
        {"topic_id": "T4_WEAK", "speakability": "READY"},
        {"topic_id": "T5_MISMATCH", "speakability": "READY"}
    ]
    
    bundle = {
        "interpretation_units": units,
        "script_realization": realizations
    }

    print("[2/8] Running MentionablesLayer...")
    results = layer.run(bundle)
    res_map = {r["topic_id"]: r for r in results}

    # 3. CASE 1: READY + Policy keywords
    print("\n[3/8] Case 1: READY + Policy (2+ evidence)")
    c1 = res_map.get("T1_POLICY")
    if c1 and len(c1["mentionables"]) > 0:
        found = any(m["name"] == "KB금융" for m in c1["mentionables"])
        if found:
            print("  ✅ KB금융 included: PASS")
        else:
             print(f"  ❌ KB금융 missing: {c1['mentionables']}")
    else:
        print(f"  ❌ FAIL: {c1}")

    # 4. CASE 2: READY + AI Infra
    print("\n[4/8] Case 2: READY + AI Infra")
    c2 = res_map.get("T2_INFRA")
    if c2 and any(m["name"] == "LS ELECTRIC" for m in c2["mentionables"]):
        print("  ✅ LS ELECTRIC included: PASS")
    else:
        print(f"  ❌ FAIL: {c2}")

    # 5. CASE 4: 1 Evidence Only
    print("\n[5/8] Case 4: 1 Evidence Only (Weak)")
    c4 = res_map.get("T4_WEAK")
    if c4 and len(c4["mentionables"]) == 0:
        print("  ✅ Weak evidence excluded: PASS")
    else:
        print(f"  ❌ FAIL: {c4}")

    # 6. CASE 5: Keyword Mismatch
    print("\n[6/8] Case 5: Keyword Mismatch")
    c5 = res_map.get("T5_MISMATCH")
    if c5 and len(c5["mentionables"]) == 0:
        print("  ✅ No keyword match excluded: PASS")
    else:
        print(f"  ❌ FAIL: {c5}")

    # 7. CASE 6: Template Validation (No hype words)
    print("\n[7/8] Case 6: Template Hype Word Check")
    banned = ["폭등", "2배", "상한가", "추천", "급상승"]
    all_claims = ""
    for r in results:
        for m in r["mentionables"]:
            for w in m["why_must_say"]:
                all_claims += w["claim"]
    
    found_banned = [b for b in banned if b in all_claims]
    if not found_banned:
        print("  ✅ No hype words found: PASS")
    else:
        print(f"  ❌ Found hype words: {found_banned}")

    # 8. Schema Check
    print("\n[8/8] Schema Integrity Check")
    if results and "topic_id" in results[0] and "governance" in results[0]:
        print("  ✅ Schema fields present: PASS")
    else:
        print("  ❌ Schema failure")

    layer.save(results, "data/decision/mentionables_test.json")

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
    verify_is97_4()
