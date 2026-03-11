import json
import logging
from pathlib import Path
from src.ops.economic_hunter_video_intensity import EconomicHunterVideoIntensityLayer

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VerifyStep77")

def setup_mock_data(base_dir: Path, scenario: str):
    ops_dir = base_dir / "data/ops"
    ops_dir.mkdir(parents=True, exist_ok=True)
    
    top1_path = ops_dir / "structural_top1_today.json"
    narrative_path = ops_dir / "issue_signal_narrative_today.json"
    history_path = ops_dir / "ps_history.json"
    
    # Defaults
    top1_data = {
        "top1_topics": [{
            "topic_lock": True,
            "original_card": {
                "dataset_id": "test_ds",
                "structure_type": "STRUCTURAL_REDEFINITION",
                "pre_structural_signal": {
                    "temporal_anchor": "None",
                    "related_entities": []
                }
            }
        }]
    }
    narrative_data = {
        "narrative": {
            "title": "Test Topic",
            "whynow_trigger": {"id": 1}
        }
    }
    
    if scenario == "FLASH":
        top1_data["top1_topics"][0]["original_card"]["pre_structural_signal"]["temporal_anchor"] = "D-3 Deadline"
    elif scenario == "STRIKE":
        top1_data["top1_topics"][0]["original_card"]["structure_type"] = "STRUCTURAL_DAMAGE"
        top1_data["top1_topics"][0]["original_card"]["pre_structural_signal"]["related_entities"] = ["Entity1", "Entity2"]
    elif scenario == "DEEP_HUNT":
        # Add history
        history = [
            {"dataset_id": "test_ds", "detected_at": "2026-01-20"},
            {"dataset_id": "test_ds", "detected_at": "2026-01-21"},
            {"dataset_id": "test_ds", "detected_at": "2026-01-22"}
        ]
        history_path.write_text(json.dumps(history))
    elif scenario == "REJECT":
        narrative_data["narrative"]["whynow_trigger"]["id"] = 0 # No trigger

    top1_path.write_text(json.dumps(top1_data, indent=2, ensure_ascii=False), encoding='utf-8')
    narrative_path.write_text(json.dumps(narrative_data, indent=2, ensure_ascii=False), encoding='utf-8')

def test_step77():
    base_dir = Path(".")
    layer = EconomicHunterVideoIntensityLayer(base_dir)

    print("\n=== Step 77: ECONOMIC_HUNTER_VIDEO_INTENSITY_LAYER Verification ===\n")

    # Test 1: FLASH
    setup_mock_data(base_dir, "FLASH")
    res = layer.decide_intensity()
    if res.get("level") == "FLASH":
        print("✅ Test 1 (FLASH) Passed")
    else:
        print(f"❌ Test 1 (FLASH) Failed: {res}")

    # Test 2: STRIKE
    setup_mock_data(base_dir, "STRIKE")
    res = layer.decide_intensity()
    if res.get("level") == "STRIKE":
        print("✅ Test 2 (STRIKE) Passed")
    else:
        print(f"❌ Test 2 (STRIKE) Failed: {res}")

    # Test 3: DEEP_HUNT
    setup_mock_data(base_dir, "DEEP_HUNT")
    res = layer.decide_intensity()
    if res.get("level") == "DEEP_HUNT":
        print("✅ Test 3 (DEEP_HUNT) Passed")
    else:
        print(f"❌ Test 3 (DEEP_HUNT) Failed: {res}")

    # Test 4: REJECT
    setup_mock_data(base_dir, "REJECT")
    res = layer.decide_intensity()
    if res.get("status") == "rejected":
        print("✅ Test 4 (REJECT) Passed")
    else:
        print(f"❌ Test 4 (REJECT) Failed: {res}")

if __name__ == "__main__":
    test_step77()
