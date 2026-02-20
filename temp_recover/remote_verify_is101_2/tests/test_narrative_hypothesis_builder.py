import pytest
import json
from pathlib import Path
from src.ops.narrative_hypothesis_builder import NarrativeHypothesisBuilder

def test_hypothesis_generation(tmp_path):
    builder = NarrativeHypothesisBuilder(tmp_path)
    
    seeds = [
        {
            "seed_id": "seed_1",
            "structural_frames": ["TECH_INFLECTION", "CAPITAL_REALLOCATION"],
            "supporting_facts": ["f1", "f2", "f3"],
            "seed_summary": "AI semiconductor investment shifts",
            "first_seen": "2026-01-26"
        },
        {
            "seed_id": "seed_2",
            "structural_frames": ["POLICY_SHIFT"],
            "supporting_facts": ["f4"],
            "seed_summary": "new energy regulations",
            "first_seen": "2026-01-25"
        }
    ]
    
    hypotheses = builder.build_hypotheses(seeds)
    
    assert len(hypotheses) == 2
    
    # Check hypothesis 1 (fact_count=3 -> MEDIUM)
    h1 = next(h for h in hypotheses if h["seed_id"] == "seed_1")
    assert h1["confidence_level"] == "MEDIUM"
    assert "TECH_INFLECTION" in h1["hypothesis_text"]
    assert h1["status"] == "PRE-NARRATIVE"
    
    # Check hypothesis 2 (fact_count=1 -> LOW)
    h2 = next(h for h in hypotheses if h["seed_id"] == "seed_2")
    assert h2["confidence_level"] == "LOW"
    assert "POLICY_SHIFT" in h2["hypothesis_text"]

    # Verify file saved
    out_file = tmp_path / "data" / "ops" / "narrative_hypotheses.json"
    assert out_file.exists()
    saved_data = json.loads(out_file.read_text(encoding="utf-8"))
    assert len(saved_data) == 2
