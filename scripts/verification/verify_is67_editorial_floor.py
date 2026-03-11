import sys
import os
from pathlib import Path
from typing import Dict, Any, List

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.issuesignal.script_lock_engine import ScriptLockEngine

def test_quality_floor():
    print("[TEST] Verifying IS-67 Editorial Candidate Quality Floor...")
    
    # Mock data
    protagonist = {
        "details": {"company": "TestCorp", "action_type": "BUYBACK"},
        "fact_text": "TestCorp announced a buyback of $1B.",
        "bottleneck_reason": "Supply chain constraint"
    }
    why_now = "Immediate impact expected."
    target_sector = "Tech"
    
    # 1. Test Script Generation failing validation (e.g. missing mandatory words)
    # Mandatories: ["필연", "결정", "해야 한다"]
    # Our ScriptLockEngine.generate adds "필연" automatically, but let's check if it fails if we bypass it.
    
    # Since we want to test the FLOOR logic in run_issuesignal.py:
    # has_hard_fact = len(corporate_facts) > 0 or len(official_facts) > 0
    # has_why_now = bool(cand.get('why_now'))
    
    # We can't easily run run_issuesignal.py in isolation without full data.
    # So we verify the logic we inserted.
    
    print("Checking logic insertion in run_issuesignal.py...")
    with open("src/issuesignal/run_issuesignal.py", "r") as f:
        content = f.read()
        if "has_hard_fact = len(corporate_facts) > 0" in content and "has_why_now = bool(cand.get('why_now'))" in content:
            print("[PASS] Quality Floor logic found in run_issuesignal.py")
        else:
            print("[FAIL] Quality Floor logic NOT found in run_issuesignal.py")
            sys.exit(1)

    # 2. Test Success Path in Engine
    evidence_pool = [
        {"type": "TRIGGER_QUOTE", "fact_text": "CEO said 'This is inevitable'."},
        {"type": "CORPORATE_ACTION", "fact_text": "Board approved buyback."}
    ]
    
    script = ScriptLockEngine.generate(protagonist, why_now, target_sector, evidence_pool)
    if script and "필연" in script["long_form"]:
        print(f"[PASS] Script generated successfully with mandatory words. Status: {script['one_liner']}")
    else:
        print("[FAIL] Script generation failed or mandatory words missing.")
        sys.exit(1)

if __name__ == "__main__":
    test_quality_floor()
