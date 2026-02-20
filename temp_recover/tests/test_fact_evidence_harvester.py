import pytest
import json
from pathlib import Path
from src.collectors.fact_evidence_harvester import FactEvidenceHarvester

def test_fact_harvester_output(tmp_path):
    harvester = FactEvidenceHarvester(tmp_path)
    ymd = "2026-01-26"
    facts = harvester.harvest(target_date=ymd)
    
    assert len(facts) > 0
    for f in facts:
        assert f["fact_id"].startswith("fact_")
        assert f["confidence"] == "RAW"
        assert f["published_at"] == ymd
        assert "fact_text" in f
        assert "source" in f

    # Verify file saved
    out_file = tmp_path / "data" / "facts" / "fact_anchors_20260126.json"
    assert out_file.exists()
    
    saved_data = json.loads(out_file.read_text(encoding="utf-8"))
    assert len(saved_data) == len(facts)

def test_fact_harvester_deduplication(tmp_path):
    harvester = FactEvidenceHarvester(tmp_path)
    ymd = "2026-01-26"
    
    # First harvest
    harvester.harvest(target_date=ymd)
    out_file = tmp_path / "data" / "facts" / "fact_anchors_20260126.json"
    initial_count = len(json.loads(out_file.read_text(encoding="utf-8")))
    
    # Second harvest (should deduplicate)
    harvester.harvest(target_date=ymd)
    final_count = len(json.loads(out_file.read_text(encoding="utf-8")))
    
    assert initial_count == final_count
