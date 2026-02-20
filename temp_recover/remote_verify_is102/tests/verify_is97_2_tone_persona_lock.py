import os
import json
import subprocess
from pathlib import Path
from src.topics.narrator.tone_persona_lock import TonePersonaLock

def verify_is97_2():
    print("\n" + "="*60)
    print("📋 IS-97-2 TONE & PERSONA LOCK VERIFICATION")
    print("="*60)

    locker = TonePersonaLock()

    # 1. READY + SHORT + POLICY -> ASSERTIVE / POLICY_ANALYST
    print("\n[1/5] Case 1: READY + SHORT + POLICY")
    u1 = {
        "evidence_tags": ["KR_POLICY"],
        "derived_metrics_snapshot": {"pretext_score": 0.9, "policy_execution_gap": 0.1}
    }
    d1 = {"speakability_flag": "READY"}
    c1 = {"content_mode": "SHORT"}
    res1 = locker.build("T1", d1, c1, u1)
    if res1["tone"] == "ASSERTIVE" and res1["persona"] == "POLICY_ANALYST" and res1["authority_level"] == "HIGH":
        print("  ✅ Tone: ASSERTIVE, Persona: POLICY_ANALYST: PASS")
    else:
        print(f"  ❌ FAIL: {res1}")

    # 2. READY + LONG + FLOW -> EXPLANATORY / ECONOMIC_HUNTER
    print("\n[2/5] Case 2: READY + LONG + FLOW")
    u2 = {
        "evidence_tags": ["FLOW_ROTATION"],
        "derived_metrics_snapshot": {"pretext_score": 0.88, "policy_execution_gap": 0.0}
    }
    d2 = {"speakability_flag": "READY"}
    c2 = {"content_mode": "LONG"}
    res2 = locker.build("T2", d2, c2, u2)
    if res2["tone"] == "EXPLANATORY" and res2["persona"] == "ECONOMIC_HUNTER":
        print("  ✅ Tone: EXPLANATORY, Persona: ECONOMIC_HUNTER: PASS")
    else:
        print(f"  ❌ FAIL: {res2}")

    # 3. HOLD 상태 -> OBSERVATIONAL / EXPLICIT RISK
    print("\n[3/5] Case 3: HOLD status")
    u3 = {"evidence_tags": ["EARNINGS_VERIFY"], "derived_metrics_snapshot": {}}
    d3 = {"speakability_flag": "HOLD"}
    c3 = {"content_mode": "HOLD"}
    res3 = locker.build("T3", d3, c3, u3)
    if res3["tone"] == "OBSERVATIONAL" and res3["risk_disclaimer_mode"] == "EXPLICIT" and res3["confidence_level"] == "LOW":
        print("  ✅ Tone: OBSERVATIONAL, Confidence: LOW, Risk: EXPLICIT: PASS")
    else:
        print(f"  ❌ FAIL: {res3}")

    # 4. EXECUTION_GAP 큰 경우 -> confidence downshift
    print("\n[4/5] Case 4: High Execution Gap")
    u4 = {
        "evidence_tags": ["KR_POLICY"],
        "derived_metrics_snapshot": {"pretext_score": 0.9, "policy_execution_gap": 0.6}
    }
    d4 = {"speakability_flag": "READY"}
    c4 = {"content_mode": "SHORT"}
    res4 = locker.build("T4", d4, c4, u4)
    if res4["confidence_level"] == "MEDIUM" and res4["risk_disclaimer_mode"] == "EXPLICIT":
        print("  ✅ Confidence: MEDIUM, Risk: EXPLICIT: PASS")
    else:
        print(f"  ❌ FAIL: {res4}")

    # 5. DROP 상태 -> 출력 없음
    print("\n[5/5] Case 5: DROP status")
    u5 = {"evidence_tags": []}
    d5 = {"speakability_flag": "DROP"}
    c5 = {"content_mode": "HOLD"}
    res5 = locker.build("T5", d5, c5, u5)
    if res5 is None:
        print("  ✅ Result is None: PASS")
    else:
        print(f"  ❌ FAIL: {res5}")

    # Integrity Check
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
    verify_is97_2()
