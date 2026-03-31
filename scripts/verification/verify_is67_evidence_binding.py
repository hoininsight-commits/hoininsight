import sys
import os
from pathlib import Path
from typing import Dict, Any, List

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.issuesignal.script_lock_engine import ScriptLockEngine

def test_evidence_binding():
    print("[TEST] Verifying IS-67 Evidence-to-Script Auto Binding...")
    
    protagonist = {
        "details": {"company": "TestCorp", "action_type": "EXPANSION"},
        "fact_text": "Expanding production in Korea.",
        "bottleneck_reason": "Structural demand growth"
    }
    evidence_pool = [
        {"type": "TRIGGER_QUOTE", "id": "ev1", "fact_text": "CEO Quote: We must expand now."},
        {"type": "CORPORATE_ACTION", "id": "ev2", "fact_text": "DART: Investment of 100B KRW announced."},
        {"type": "MACRO_FACT", "id": "ev3", "fact_text": "Global demand for tech up 20%."}
    ]
    
    script = ScriptLockEngine.generate(protagonist, "Now is time.", "Semicon", evidence_pool)
    
    if not script:
        print("[FAIL] Script generation failed.")
        sys.exit(1)
        
    long_form = script["long_form"]
    print(f"Generated Script Snippet:\n{long_form[:300]}...")
    
    # Check for binding markers
    if "근거: CEO Quote: We must expand now" in long_form:
        print("[PASS] Step 1 (Trigger Quote) bound correctly.")
    else:
        print("[FAIL] Step 1 binding missing or format mismatch.")
        print(f"DEBUG: {long_form}")
        
    if "근거: DART: Investment of 100B KRW announced" in long_form or "근거: Global demand for tech up 20%" in long_form:
        print("[PASS] Step 4 (Structural Fact) bound correctly.")
    else:
        print("[FAIL] Step 4 binding missing or format mismatch.")
        print(f"DEBUG: {long_form}")

    # Check for placeholder if missing
    incomplete_pool = []
    script_incomp = ScriptLockEngine.generate(protagonist, "Now is time.", "Semicon", incomplete_pool)
    if "[직접 근거 확인 중]" in script_incomp["long_form"]:
        print("[PASS] Placeholder rendered when evidence is missing.")
    else:
        print("[FAIL] Placeholder missing for empty pool.")

if __name__ == "__main__":
    test_evidence_binding()
