import json
import os
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from src.issuesignal.structural_bridge import StructuralBridge
from src.issuesignal.editorial_light_engine import EditorialLightEngine
from src.issuesignal.script_lock_engine import ScriptLockEngine

def test_structural_bridge_full_cycle():
    base_dir = Path("./test_env")
    if base_dir.exists(): shutil.rmtree(base_dir)
    base_dir.mkdir(parents=True)
    
    bridge_engine = StructuralBridge(base_dir)
    
    # 1. Simulate IS-70: Editorial Light Generation & Recording
    macro_actor = {"actor_name_ko": "미국 국채", "actor_tag": "상승", "actor_type": "자본"}
    light_data = EditorialLightEngine.generate(macro_actor, "BULL")
    
    # Record it (3 days ago simulation)
    struct_data = {
        "structure_id": light_data["structure_id"],
        "summary": light_data["summary"],
        "actor": light_data["actor"],
        "sector": "채권",
        "keywords": light_data["keywords"]
    }
    bridge_engine.record_structure(struct_data)
    
    # Manually adjust timestamp in memory to 3 days ago
    memory = bridge_engine._load_memory()
    memory[0]['timestamp'] = (datetime.now() - timedelta(days=3)).isoformat()
    bridge_engine._save_memory(memory)
    
    print(f"Step 1: Recorded structure {light_data['structure_id']} (3 days ago)")

    # 2. Simulate Now: HARD_FACT event arrives
    current_event = {
        "actor": "미국 국채",
        "fact_text": "[공식] 미 국채 금리 급등에 따른 자본 이동"
    }
    
    bridge_match = bridge_engine.find_bridge(current_event)
    assert bridge_match is not None
    assert bridge_match["days_ago"] >= 3
    print(f"Step 2: Bridge found! Days ago: {bridge_match['days_ago']}")

    # 3. Simulate Script Generation with Bridge
    protagonist = {
        "fact_text": "[공식] 미 국채 금리 급등",
        "details": {"actor_name_ko": "미국 국채", "actor_reason_ko": "금리 상승 압력"}
    }
    script = ScriptLockEngine.generate(
        protagonist, 
        "지금 금리 변화가 구조적 임계점에 도달했기 때문입니다.", 
        "채권", 
        [], 
        bridge_info=bridge_match
    )
    
    print("\nGenerated Script Head:")
    print(script["long_form"][:150])
    
    assert "이 변화는 3일 전에 구조 해설로 언급했던" in script["long_form"]
    
    # Cleanup
    shutil.rmtree(base_dir)
    print("\n[VERIFY] IS-71 Structural Continuity Bridge Integration Test Passed!")

if __name__ == "__main__":
    test_structural_bridge_full_cycle()
