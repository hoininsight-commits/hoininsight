import json
import logging
from pathlib import Path
from src.ops.economic_hunter_title_thumbnail_intensity import EconomicHunterTitleThumbnailIntensityLayer

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VerifyStep79")

def setup_mock_data(base_dir: Path, v_level: str):
    ops_dir = base_dir / "data/ops"
    ops_dir.mkdir(parents=True, exist_ok=True)
    
    top1_path = ops_dir / "structural_top1_today.json"
    narrative_path = ops_dir / "issue_signal_narrative_today.json"
    
    top1_data = {
        "top1_topics": [{
            "topic_lock": True,
            "video_intensity": {"level": v_level},
            "video_rhythm": {"rhythm_profile": "TEST_RHYTHM"}
        }]
    }
    narrative_data = {
        "narrative": {
            "title": "Test Title Intensity Topic"
        }
    }
    
    top1_path.write_text(json.dumps(top1_data, indent=2, ensure_ascii=False))
    narrative_path.write_text(json.dumps(narrative_data, indent=2, ensure_ascii=False))

def test_step79():
    base_dir = Path(".")
    layer = EconomicHunterTitleThumbnailIntensityLayer(base_dir)

    print("\n=== Step 79: ECONOMIC_HUNTER_TITLE_THUMBNAIL_INTENSITY_LAYER Verification ===\n")

    # Test 1: FLASH -> TITLE_INTENSITY_FLASH
    setup_mock_data(base_dir, "FLASH")
    res = layer.assign_intensity()
    if res.get("title_intensity") == "TITLE_INTENSITY_FLASH":
        print("✅ Test 1 (FLASH) Passed")
    else:
        print(f"❌ Test 1 (FLASH) Failed: {res}")

    # Test 2: STRIKE -> TITLE_INTENSITY_STRIKE
    setup_mock_data(base_dir, "STRIKE")
    res = layer.assign_intensity()
    if res.get("title_intensity") == "TITLE_INTENSITY_STRIKE":
        print("✅ Test 2 (STRIKE) Passed")
    else:
        print(f"❌ Test 2 (STRIKE) Failed: {res}")

    # Test 3: DEEP_HUNT -> TITLE_INTENSITY_DEEP
    setup_mock_data(base_dir, "DEEP_HUNT")
    res = layer.assign_intensity()
    if res.get("title_intensity") == "TITLE_INTENSITY_DEEP":
        print("✅ Test 3 (DEEP) Passed")
    else:
        print(f"❌ Test 3 (DEEP) Failed: {res}")

    # Test 4: REJECT (Unknown Level)
    setup_mock_data(base_dir, "UNKNOWN")
    res = layer.assign_intensity()
    if res.get("status") == "rejected":
        print("✅ Test 4 (REJECT) Passed")
    else:
        print(f"❌ Test 4 (REJECT) Failed: {res}")

if __name__ == "__main__":
    test_step79()
