"""
Verify IS-100 UI Decision Contract conversion
"""
import json
import os
import shutil
from pathlib import Path
from src.ui.ui_decision_contract import build_ui_decision_contract

def test_contract_conversion():
    test_input = Path("data/test_decision")
    test_output = Path("data/test_ui_decision")
    test_input.mkdir(parents=True, exist_ok=True)
    
    # 1. Create mock list-based engine outputs
    units = [{"interpretation_id": "unit_01", "val": 1}]
    mentions = [{"topic_id": "topic_01", "name": "MENTION_01"}]
    packs = [{"topic_id": "topic_01", "title": "PACK_01"}]
    evidence = [{"topic_id": "topic_01", "citations": []}]
    
    with open(test_input / "interpretation_units.json", "w") as f:
        json.dump(units, f)
    with open(test_input / "mentionables.json", "w") as f:
        json.dump(mentions, f)
    with open(test_input / "content_pack.json", "w") as f:
        json.dump(packs, f)
    with open(test_input / "evidence_citations.json", "w") as f:
        json.dump(evidence, f)

    # 2. Run Adapter
    print("[TEST] Running build_ui_decision_contract on mock data...")
    build_ui_decision_contract(input_dir=str(test_input), output_dir=str(test_output))

    # 3. Verify dict-shaped outputs
    print("[TEST] Verifying dict-shaped outputs...")
    with open(test_output / "interpretation_units.json", "r") as f:
        data = json.load(f)
        assert isinstance(data, dict), "interpretation_units should be dict"
        assert "unit_01" in data
        
    with open(test_output / "mentionables.json", "r") as f:
        data = json.load(f)
        assert isinstance(data, dict), "mentionables should be dict"
        assert "topic_01" in data

    with open(test_output / "content_pack.json", "r") as f:
        data = json.load(f)
        assert isinstance(data, dict), "content_pack should be dict"
        assert "topic_01" in data

    print("IS-100 UI Decision Contract Test: PASSED")

    # Cleanup
    shutil.rmtree(test_input)
    shutil.rmtree(test_output)

if __name__ == "__main__":
    test_contract_conversion()
