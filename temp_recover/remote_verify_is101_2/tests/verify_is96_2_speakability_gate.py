import os
import json
import subprocess
from pathlib import Path
from src.topics.gate.speakability_gate import SpeakabilityGate

def verify_is96_2():
    print("\n" + "="*60)
    print("📋 IS-96-2 SPEAKABILITY GATE VERIFICATION")
    print("="*60)

    base_dir = Path(".")
    gate = SpeakabilityGate()

    # 1. File & Module Existence
    print("\n[1/4] Checking Required Files & Modules...")
    files = [
        "docs/engine/IS-96-2_SPEAKABILITY_GATE.md",
        "src/topics/gate/speakability_gate.py"
    ]
    for f in files:
        if (base_dir / f).exists():
            print(f"  ✅ {f}: FOUND")
        else:
            print(f"  ❌ {f}: MISSING")

    # 2. Synthetic Test Cases
    print("\n[2/4] Running 5 Synthetic Test Cases...")
    
    test_cases = [
        {
            "name": "READY: High Pretext + Earnings Verified",
            "unit": {
                "interpretation_key": "FUNDAMENTAL_RE-RATING",
                "why_now_type": "Schedule-driven",
                "confidence_score": 0.85,
                "evidence_tags": ["PRETEXT_VALIDATION", "EARNINGS_VERIFY"],
                "derived_metrics_snapshot": {"pretext_score": 0.90}
            },
            "expected_flag": "READY"
        },
        {
            "name": "HOLD: Medium Pretext + Earnings Pending",
            "unit": {
                "interpretation_key": "NARRATIVE_TESTING",
                "why_now_type": "State-driven",
                "confidence_score": 0.75,
                "evidence_tags": ["PRETEXT_VALIDATION", "FLOW_ROTATION"],
                "derived_metrics_snapshot": {"pretext_score": 0.78}
            },
            "expected_flag": "HOLD"
        },
        {
            "name": "DROP: Low Pretext + Rotation Only",
            "unit": {
                "interpretation_key": "NARRATIVE_TESTING",
                "why_now_type": "State-driven",
                "confidence_score": 0.50,
                "evidence_tags": ["FLOW_ROTATION"],
                "derived_metrics_snapshot": {"pretext_score": 0.65}
            },
            "expected_flag": "DROP"
        },
        {
            "name": "DROP: Policy Announced but High Execution Gap",
            "unit": {
                "interpretation_key": "STRUCTURAL_ROUTE_FIXATION",
                "why_now_type": "Hybrid",
                "confidence_score": 0.90,
                "evidence_tags": ["KR_POLICY"],
                "derived_metrics_snapshot": {"pretext_score": 0.95, "policy_execution_gap": 0.60}
            },
            "expected_flag": "DROP"
        },
        {
            "name": "READY: Passive Flow Activation + Earnings Verified",
            "unit": {
                "interpretation_key": "PASSIVE_FRONT_RUNNING",
                "why_now_type": "Schedule-driven",
                "confidence_score": 0.82,
                "evidence_tags": ["GLOBAL_INDEX", "EARNINGS_VERIFY"],
                "derived_metrics_snapshot": {"pretext_score": 0.88}
            },
            "expected_flag": "READY"
        }
    ]

    for tc in test_cases:
        result = gate.evaluate(tc["unit"])
        flag = result["speakability_flag"]
        reasons = result["speakability_reasons"]
        
        if flag == tc["expected_flag"]:
            print(f"  ✅ Test '{tc['name']}': PASS (Flag={flag})")
        else:
            print(f"  ❌ Test '{tc['name']}': FAIL (Expected {tc['expected_flag']}, got {flag})")
            print(f"     Reasons: {reasons}")

    # 3. Read-only Evaluator Integration (Simulation)
    # This simulation verifies the gate can be called standalone.
    print("\n[3/4] Read-only Evaluator Pattern Test...")
    try:
        from src.topics.gate.speakability_gate import run_gate
        test_unit = {"derived_metrics_snapshot": {"pretext_score": 0.5}}
        res = run_gate(test_unit)
        if res.get("speakability_flag") == "DROP":
            print("  ✅ standalone run_gate() pattern: PASS")
    except Exception as e:
        print(f"  ❌ standalone run_gate() pattern: FAIL ({e})")

    # 4. Constitutional Integrity Check
    print("\n[4/4] Constitutional Integrity Check (Add-only)...")
    forbidden = [
        "docs/DATA_COLLECTION_MASTER.md",
        "docs/BASELINE_SIGNALS.md",
        "docs/ANOMALY_DETECTION_LOGIC.md"
    ]
    BASELINE = "d17bb99dc"
    for doc in forbidden:
        try:
            # Check for WORKING TREE changes
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
    verify_is96_2()
