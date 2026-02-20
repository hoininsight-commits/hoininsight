"""
Verify IS-101 Natural Language Mapper logic
"""
import json
import os
from pathlib import Path
from src.ui.natural_language_mapper import NaturalLanguageMapper

def test_mapper_logic():
    test_input = Path("data/verify_is101")
    test_input.mkdir(parents=True, exist_ok=True)
    
    # Mock interpretation unit
    unit = [{
        "interpretation_id": "test_unit",
        "target_sector": "TECH_INFRA_KOREA",
        "interpretation_key": "STRUCTURAL_ROUTE_FIXATION",
        "confidence_score": 0.95,
        "evidence_tags": ["KR_POLICY", "EARNINGS_VERIFY"],
        "derived_metrics_snapshot": {
            "policy_commitment_score": 0.88,
            "pretext_score": 0.92
        }
    }]
    
    with open(test_input / "interpretation_units.json", "w") as f:
        json.dump(unit, f)
    with open(test_input / "speakability_decision.json", "w") as f:
        json.dump({"test_unit": {"speakability_flag": "READY"}}, f)
    with open(test_input / "narrative_skeleton.json", "w") as f:
        json.dump({"test_unit": {"checklist_3": ["Check A", "Check B"]}}, f)

    mapper = NaturalLanguageMapper(input_dir=str(test_input))
    briefing = mapper.build_briefing()
    
    assert "test_unit" in briefing
    b = briefing["test_unit"]
    
    # Check Block 0: Hero
    assert "한국 테크 인프라" in b["hero"]["sentence"]
    assert "0.95" in b["hero"]["metric"]
    
    # Check Block 1: Decision
    assert "지금 이야기해도 됩니다" in b["decision"]["title"]
    
    # Check Block 2: Why Now
    assert any("88%" in item for item in b["why_now"]["items"])
    assert any("실적 발표" in item for item in b["why_now"]["items"])
    
    # Check Block 4: Trust
    assert "Sources: 2" in b["trust"]["items"][0]
    
    print("IS-101 Natural Language Mapper Test: PASSED")
    
    # Cleanup
    import shutil
    shutil.rmtree(test_input)

if __name__ == "__main__":
    test_mapper_logic()
