import os
import json
import subprocess
import hashlib
from pathlib import Path
from src.topics.content_pack.content_pack_multipack_layer import ContentPackMultiPackLayer

def get_hash(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()

def verify_is98_2a():
    print("\n" + "="*60)
    print("📋 IS-98-2a MULTI-PACK VERIFICATION")
    print("="*60)

    layer = ContentPackMultiPackLayer()

    # 1. SETUP MOCK DATA (READY 5+ case)
    print("\n[Case 1] READY 5+ units -> 1 Long + 4 Shorts")
    packs_ready5 = []
    for i in range(6):
        packs_ready5.append({
            "topic_id": f"T{i}",
            "status": {"speakability": "READY"},
            "assets": {
                "title": f"Title {i}",
                "shorts_script": {"text": "Short"},
                "long_script": {"text": "Long"},
                "decision_card": {"why_now": "Now"},
                "evidence_sources": [{"status": "VERIFIED"}] * (i+1), # Different scores
                "mentionables": [{"name": "M"}]
            }
        })
    
    res1 = layer.run(packs_ready5)
    if res1["summary"]["long_count"] == 1 and res1["summary"]["short_count"] == 4:
        print(f"  ✅ 1 Long + 4 Shorts selected: PASS (Packs: {len(res1['packs'])})")
    else:
        print(f"  ❌ FAIL: {res1['summary']}")

    # 2. SETUP MOCK DATA (READY 4 case)
    print("\n[Case 2] READY 4 units -> 1 Long + 3 Shorts")
    res2 = layer.run(packs_ready5[:4])
    if res2["summary"]["long_count"] == 1 and res2["summary"]["short_count"] == 3:
        print("  ✅ 1 Long + 3 Shorts selected: PASS")
    else:
        print(f"  ❌ FAIL: {res2['summary']}")

    # 3. PROMOTION CASE
    print("\n[Case 3] 2 READY + 3 clear-trigger HOLD -> Promotion")
    packs_promote = [
        {"topic_id": "R1", "status": {"speakability": "READY"}, "assets": {"title": "R1", "shorts_script": {}, "long_script": {}, "decision_card": {"why_now": "N"}, "evidence_sources": [{"status":"VERIFIED"}], "mentionables":[]}},
        {"topic_id": "R2", "status": {"speakability": "READY"}, "assets": {"title": "R2", "shorts_script": {}, "long_script": {}, "decision_card": {"why_now": "N"}, "evidence_sources": [{"status":"VERIFIED"}], "mentionables":[]}},
        {"topic_id": "H1", "status": {"speakability": "HOLD"}, "assets": {"title": "중요 발표 예정", "shorts_script": {}, "long_script": {}, "decision_card": {"why_now": "N"}, "evidence_sources": [{"status":"PARTIAL"}], "mentionables":[]}},
        {"topic_id": "H2", "status": {"speakability": "HOLD"}, "assets": {"title": "신제품 출시 확정", "shorts_script": {}, "long_script": {}, "decision_card": {"why_now": "N"}, "evidence_sources": [{"status":"VERIFIED"}], "mentionables":[]}},
        {"topic_id": "H3", "status": {"speakability": "HOLD"}, "assets": {"title": "아무런 특징 없음", "shorts_script": {}, "long_script": {}, "decision_card": {"why_now": "N"}, "evidence_sources": [], "mentionables":[]}}
    ]
    res3 = layer.run(packs_promote)
    if res3["summary"]["short_count"] == 3 and res3["summary"]["hold_included"] == 2:
        print(f"  ✅ 2 READY + 2 promoted HOLD selected: PASS (Shorts: {res3['summary']['short_count']})")
    else:
        print(f"  ❌ FAIL: {res3['summary']}")

    # 4. EMPTY CASE
    print("\n[Case 4] All DROP -> Empty packs")
    res4 = layer.run([{"topic_id": "D1", "status": {"speakability": "DROP"}, "assets": {}}])
    if len(res4["packs"]) == 0:
        print("  ✅ Empty packs for all DROP: PASS")
    else:
        print(f"  ❌ FAIL: {len(res4['packs'])}")

    # 5. DETERMINISTIC CASE
    print("\n[Case 8] Deterministic Output")
    res1_again = layer.run(packs_ready5)
    if get_hash(res1) == get_hash(res1_again):
        print("  ✅ Deterministic hash check: PASS")
    else:
        print("  ❌ FAIL: Non-deterministic")

    # SCHEMA CHECK
    print("\n[Integrity] Schema Field Check...")
    if "date" in res1 and "packs" in res1 and "summary" in res1:
        print("  ✅ Mandatory fields present: PASS")
    else:
        print("  ❌ FAIL: Missing mandatory fields")

    # SAVE TEST
    layer.save(res1, "content_pack_multipack_test.json")

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
    verify_is98_2a()
