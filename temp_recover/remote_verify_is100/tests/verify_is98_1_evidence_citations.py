import os
import json
import subprocess
from pathlib import Path
from src.topics.citations.evidence_citation_layer import EvidenceCitationLayer

def verify_is98_1():
    print("\n" + "="*60)
    print("📋 IS-98-1 EVIDENCE CITATION VERIFICATION")
    print("="*60)

    # 1. FAIL FAST CHECK
    print("\n[1/7] Fail-fast Check (Missing Registry)")
    try:
        EvidenceCitationLayer(registry_path="non_existent.yml")
        print("  ❌ FAIL: Should have raised FileNotFoundError")
    except FileNotFoundError as e:
        print(f"  ✅ Caught expected error: {e}")

    layer = EvidenceCitationLayer()

    # 2. MATCHING TESTS
    print("\n[2/7] Matching Test: KR_POLICY (Verified)")
    u1 = {
        "interpretation_id": "T1",
        "interpretation_key": "정부 밸류업 가이드라인 발표",
        "evidence_tags": ["KR_POLICY"]
    }
    s1 = [{
        "topic_id": "T1",
        "script": {
            "hook": "이다.", 
            "claim": "다.", 
            "evidence_3": ["다."], 
            "checklist_3": [],
            "risk_note": "",
            "closing": "다."
        }
    }]
    bundle1 = {"interpretation_units": [u1], "script_realization": s1}
    res1 = layer.run(bundle1)
    cite1 = res1["evidence_citations"][0]["citations"][0]
    if cite1["status"] == "VERIFIED" and len(cite1["sources"]) > 0:
        print("  ✅ T1 (KR_POLICY): VERIFIED with sources: PASS")
    else:
        print(f"  ❌ FAIL: {cite1}")

    print("\n[3/7] Matching Test: GLOBAL_INDEX (Verified)")
    u2 = {
        "interpretation_id": "T2",
        "interpretation_key": "MSCI 편입 기대감",
        "evidence_tags": ["GLOBAL_INDEX"]
    }
    bundle2 = {"interpretation_units": [u2], "script_realization": []}
    res2 = layer.run(bundle2)
    cite2 = res2["evidence_citations"][0]["citations"][0]
    if cite2["status"] == "VERIFIED":
        print("  ✅ T2 (GLOBAL_INDEX): VERIFIED: PASS")
    else:
        print(f"  ❌ FAIL: {cite2}")

    print("\n[4/7] Matching Test: EARNINGS_VERIFY (Verified)")
    u3 = {
        "interpretation_id": "T3",
        "interpretation_key": "영업이익 서프라이즈",
        "evidence_tags": ["EARNINGS_VERIFY"]
    }
    bundle3 = {"interpretation_units": [u3], "script_realization": []}
    res3 = layer.run(bundle3)
    cite3 = res3["evidence_citations"][0]["citations"][0]
    if cite3["status"] == "VERIFIED":
        print("  ✅ T3 (EARNINGS_VERIFY): VERIFIED: PASS")
    else:
        print(f"  ❌ FAIL: {cite3}")

    print("\n[5/7] Match Failure (Unverified)")
    u4 = {
        "interpretation_id": "T4",
        "interpretation_key": "그냥 평범한 정보",
        "evidence_tags": ["FLOW_ROTATION"]
    }
    bundle4 = {"interpretation_units": [u4], "script_realization": []}
    res4 = layer.run(bundle4)
    cite4 = res4["evidence_citations"][0]["citations"][0]
    if cite4["status"] == "UNVERIFIED":
        print("  ✅ T4 (FLOW_ROTATION): UNVERIFIED as expected: PASS")
    else:
        print(f"  ❌ FAIL: {cite4}")

    # 3. TONE GUARD TEST
    print("\n[6/7] Tone Guard Test (Unverified -> Tone Down)")
    s5 = [{
        "topic_id": "T4",
        "script": {
            "hook": "님들 이슈이다.", 
            "claim": "구조 변화다.", 
            "evidence_3": ["지표가 확인됐다."], 
            "checklist_3": ["체크1"],
            "risk_note": "리스크",
            "closing": "따라오면 된다."
        }
    }]
    bundle5 = {"interpretation_units": [u4], "script_realization": s5}
    res5 = layer.run(bundle5)
    gs5 = res5["script_with_citation_guard"][0]
    if "확인 필요" in gs5["script"]["evidence_3"][0] or "해석된다" in gs5["script"]["hook"] or "관찰 중" in gs5["script"]["hook"]:
        print("  ✅ Unverified script tone downgraded: PASS")
        # print(f"  Debug: {gs5['script']}")
    else:
        print(f"  ❌ FAIL: Tone not downgraded: {gs5['script']}")

    # 4. SCHEMA CHECK
    print("\n[7/7] Schema Integrity Check")
    if "version" in res1["evidence_citations"][0] and "governance" in res1["evidence_citations"][0]:
        print("  ✅ Schema fields present: PASS")
    else:
        print("  ❌ Schema failure")

    layer.save(res5, "data/decision/verification_test_citations")

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
    verify_is98_1()
