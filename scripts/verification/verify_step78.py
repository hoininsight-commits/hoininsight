import json
import logging
from pathlib import Path
from src.ops.economic_hunter_video_rhythm import EconomicHunterVideoRhythmLayer

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VerifyStep78")

def setup_mock_data(base_dir: Path, level: str):
    ops_dir = base_dir / "data/ops"
    ops_dir.mkdir(parents=True, exist_ok=True)
    
    top1_path = ops_dir / "structural_top1_today.json"
    narrative_path = ops_dir / "issue_signal_narrative_today.json"
    
    top1_data = {
        "top1_topics": [{
            "topic_lock": True,
            "video_intensity": {"level": level}
        }]
    }
    narrative_data = {
        "narrative": {
            "title": "Test Rhythm Topic"
        }
    }
    
    top1_path.write_text(json.dumps(top1_data, indent=2, ensure_ascii=False))
    narrative_path.write_text(json.dumps(narrative_data, indent=2, ensure_ascii=False))

def test_step78():
    base_dir = Path(".")
    layer = EconomicHunterVideoRhythmLayer(base_dir)

    print("\n=== Step 78: ECONOMIC_HUNTER_VIDEO_RHYTHM_LAYER Verification ===\n")

    # Test 1: FLASH -> SHOCK_DRIVE
    setup_mock_data(base_dir, "FLASH")
    res = layer.assign_rhythm()
    if res.get("rhythm_profile") == "SHOCK_DRIVE":
        print("✅ Test 1 (SHOCK_DRIVE) Passed")
    else:
        print(f"❌ Test 1 (SHOCK_DRIVE) Failed: {res}")

    # Test 2: STRIKE -> STRUCTURE_FLOW
    setup_mock_data(base_dir, "STRIKE")
    res = layer.assign_rhythm()
    if res.get("rhythm_profile") == "STRUCTURE_FLOW":
        print("✅ Test 2 (STRUCTURE_FLOW) Passed")
    else:
        print(f"❌ Test 2 (STRUCTURE_FLOW) Failed: {res}")

    # Test 3: DEEP_HUNT -> DEEP_TRACE
    setup_mock_data(base_dir, "DEEP_HUNT")
    res = layer.assign_rhythm()
    if res.get("rhythm_profile") == "DEEP_TRACE":
        print("✅ Test 3 (DEEP_TRACE) Passed")
    else:
        print(f"❌ Test 3 (DEEP_TRACE) Failed: {res}")

    # Test 4: REJECT (Unknown Level)
    setup_mock_data(base_dir, "UNKNOWN")
    res = layer.assign_rhythm()
    if res.get("status") == "rejected":
        print("✅ Test 4 (REJECT) Passed")
    else:
        print(f"❌ Test 4 (REJECT) Failed: {res}")

if __name__ == "__main__":
    test_step78()
