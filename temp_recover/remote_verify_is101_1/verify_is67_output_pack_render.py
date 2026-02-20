import sys
import os
import json
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.issuesignal.script_lock_engine import ScriptLockEngine

def test_output_pack():
    print("[TEST] Verifying IS-67 Editorial Output Pack Rendering...")
    
    protagonist = {
        "details": {"company": "TestCorp", "action_type": "MERGER"},
        "fact_text": "Merging with FutureTech.",
        "bottleneck_reason": "Growth through M&A"
    }
    evidence_pool = [{"type": "TRIGGER_QUOTE", "fact_text": "Merger is inevitable."}]
    
    script = ScriptLockEngine.generate(protagonist, "Strategic alignment.", "IT", evidence_pool)
    
    if not script:
        print("[FAIL] Script generation failed.")
        sys.exit(1)
        
    required_keys = ["long_form", "shorts_15s", "shorts_30s", "shorts_45s", "text_card", "one_liner", "bindings"]
    missing = [k for k in required_keys if k not in script]
    
    if missing:
        print(f"[FAIL] Missing keys in output pack: {missing}")
        sys.exit(1)
    else:
        print("[PASS] All 7 keys present in script output pack.")
        
    print(f"Text Card Preview: {script['text_card']}")
    print(f"Shorts 15s: {script['shorts_15s']}")
    
    # Check if dashboard renderer logic is updated
    with open("src/issuesignal/dashboard/renderer.py", "r") as f:
        content = f.read()
        if "shorts_15s" in content and "text-card" in content:
             print("[PASS] Dashboard Renderer supports IS-67 fields.")
        else:
             print("[FAIL] Dashboard Renderer NOT updated for IS-67 fields.")
             sys.exit(1)

if __name__ == "__main__":
    test_output_pack()
