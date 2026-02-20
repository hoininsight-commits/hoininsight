import pytest
import json
from pathlib import Path
from src.ops.fact_first_ingress import FactFirstIngress

def test_fact_first_ingress_rules(tmp_path):
    # Setup mock data structure
    raw_dir = tmp_path / "data" / "raw" / "policy" / "2026" / "01" / "26"
    raw_dir.mkdir(parents=True)
    
    mock_policy = {
        "id": "p1",
        "title": "New Green Energy Subsidy Policy",
        "impact_area": "Renewable Energy Sector",
        "trust_score": 0.9
    }
    (raw_dir / "policy_doc.json").write_text(json.dumps(mock_policy))
    
    ingress = FactFirstIngress(tmp_path)
    topics = ingress.run_ingress(target_date="2026-01-26")
    
    assert len(topics) == 1
    t = topics[0]
    assert t["topic_type"] == "FACT_FIRST"
    assert t["status"] == "SHADOW"
    assert "New Green Energy Subsidy Policy" in t["fact_anchor"]
    assert "Renewable Energy Sector" in t["structural_reason"]
    assert t["confidence"] == "MEDIUM"

def test_fact_first_ingress_output_file(tmp_path):
    ingress = FactFirstIngress(tmp_path)
    # Even with no data, let's see if finalized check works
    topics = ingress.run_ingress(target_date="2026-01-26")
    
    out_file = tmp_path / "data" / "topics" / "shadow_pool" / "2026" / "01" / "26" / "fact_first.json"
    if topics:
        assert out_file.exists()
    else:
        assert not out_file.exists()
