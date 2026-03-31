
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add src to path
root_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(root_dir))

from src.ops.pattern_memory_engine import PatternMemoryEngine

def setup_mock_data(base_dir: Path):
    # 1. Create a historical pattern (simulating past detection)
    memory_engine = PatternMemoryEngine(base_dir)
    
    past_date = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    past_pattern = {
        "pattern_type": "SYSTEM_TRUST_STRESS",
        "signals": ["Central Bank Narrative", "Safe Haven Interest", "Gold Demand"],
        "narrative": "중앙은행 신뢰 위기가 확산되고 있습니다."
    }
    
    memory_engine.save_pattern(
        pattern_id="SYSTEM_TRUST_STRESS",
        pattern_data=past_pattern,
        context={"date": past_date, "trigger": "POLICY_SHIFT"}
    )
    
    print(f"✅ Created historical pattern: {past_date}")
    
    # 2. Create current pattern (similar to past)
    current_pattern = {
        "pattern_type": "SYSTEM_TRUST_STRESS",
        "signals": ["Central Bank Narrative", "Safe Haven Interest"],  # 2 common features
        "narrative": "중앙은행 독립성에 대한 의구심이 커지고 있습니다."
    }
    
    return memory_engine, current_pattern

def verify_output(memory_engine: PatternMemoryEngine, current_pattern):
    # 1. Check pattern file exists
    pattern_file = memory_engine.memory_dir / "pattern_SYSTEM_TRUST_STRESS.json"
    if pattern_file.exists():
        print(f"✅ Pattern file created: {pattern_file.name}")
    else:
        print("❌ Pattern file not found")
        sys.exit(1)
    
    # 2. Check index
    index = memory_engine._load_index()
    if "SYSTEM_TRUST_STRESS" in index:
        print("✅ Pattern indexed correctly")
    else:
        print("❌ Pattern not in index")
        sys.exit(1)
    
    # 3. Test Replay
    replay_block = memory_engine.replay(current_pattern)
    
    if replay_block.get("replay_found"):
        print("✅ Replay found historical similar pattern")
    else:
        print("❌ Replay failed to find similar pattern")
        sys.exit(1)
    
    similar_cases = replay_block.get("similar_cases", [])
    if len(similar_cases) > 0:
        print(f"✅ Found {len(similar_cases)} similar case(s)")
        print(f"   Common features: {similar_cases[0].get('common_features')}")
    else:
        print("❌ No similar cases returned")
        sys.exit(1)
    
    print("\nSUCCESS: Step 88 Pattern Memory & Replay Verified.")

if __name__ == "__main__":
    try:
        memory_engine, current_pattern = setup_mock_data(root_dir)
        verify_output(memory_engine, current_pattern)
    except Exception as e:
        print(f"Runtime Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
