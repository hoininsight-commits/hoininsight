import json
import logging
from pathlib import Path
from datetime import datetime
from src.ops.economic_hunter_snapshot_generator import EconomicHunterSnapshotGenerator

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VerifyStep79Snapshot")

def setup_mock_top1(base_dir: Path, lock: bool):
    ops_dir = base_dir / "data/ops"
    ops_dir.mkdir(parents=True, exist_ok=True)
    top1_path = ops_dir / "structural_top1_today.json"
    
    top1_data = {
        "top1_topics": [{
            "topic_lock": lock,
            "whynow_trigger": {"type": "TEST_TRIGGER"},
            "video_intensity": {"level": "FLASH", "reason": "Test Reason"},
            "video_rhythm": {"rhythm_profile": "SHOCK_DRIVE"},
            "original_card": {
                "dataset_id": "test_ds",
                "structure_type": "TEST_STRUCT",
                "pre_structural_signal": {
                    "temporal_anchor": "D-3",
                    "trigger_actor": "Test Actor",
                    "rationale": "Test Rationale",
                    "unresolved_question": "Test Question",
                    "escalation_path": {"condition_to_upgrade_to_WHY_NOW": "Test Condition"}
                }
            }
        }]
    }
    
    top1_path.write_text(json.dumps(top1_data, indent=2, ensure_ascii=False))

def test_snapshot_generation():
    base_dir = Path(".")
    gen = EconomicHunterSnapshotGenerator(base_dir)

    print("\n=== Step 79-Snapshot: ECONOMIC_HUNTER_TOP1_SNAPSHOT_LAYER Verification ===\n")

    # Test 1: Lock == True -> Generated
    setup_mock_top1(base_dir, True)
    res_path = gen.generate_snapshot()
    if res_path and res_path.exists():
        print(f"✅ Test 1 (Snapshot Generated) Passed: {res_path.name}")
        # Verify Format (basic check)
        content = res_path.read_text(encoding='utf-8')
        if "[ECONOMIC_HUNTER_TOP1_SNAPSHOT]" in content and "[1. WHY NOW — 시간 강제성]" in content:
            print("✅ Test 1 (Format Check) Passed")
        else:
            print("❌ Test 1 (Format Check) Failed")
    else:
        print("❌ Test 1 (Snapshot Generated) Failed")

    # Test 2: Lock == False -> Not Generated
    setup_mock_top1(base_dir, False)
    res_path_fail = gen.generate_snapshot()
    if res_path_fail is None:
        print("✅ Test 2 (Snapshot Skipped on Unlock) Passed")
    else:
        print("❌ Test 2 (Snapshot Skipped on Unlock) Failed")

    # Test 3: Daily Accumulation Check (Simulate tomorrow)
    # Since we use datetime.now(), we can't easily mock time without a library,
    # but we can check if the file name contains today's date.
    ymd = datetime.now().strftime("%Y-%m-%d")
    if res_path and ymd in res_path.name:
        print(f"✅ Test 3 (Daily Naming) Passed: {res_path.name}")
    else:
        print(f"❌ Test 3 (Daily Naming) Failed")

if __name__ == "__main__":
    test_snapshot_generation()
