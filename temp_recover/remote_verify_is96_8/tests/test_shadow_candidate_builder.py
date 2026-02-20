import json
import pytest
from pathlib import Path
from src.ops.shadow_candidate_builder import ShadowCandidateBuilder

@pytest.fixture
def mock_setup(tmp_path):
    gate_dir = tmp_path / "data" / "topics" / "gate" / "2026" / "01" / "26"
    gate_dir.mkdir(parents=True)
    
    # 1. Topic: Eligible Shadow (HOLD, FACT-DRIVEN)
    t1 = {
        "topic_id": "t1",
        "title": "Fact Topic",
        "is_fact_driven": True,
        "tags": ["FACT_NEWS"],
        "total_score": 0.8
    }
    q1 = {
        "quality_status": "HOLD",
        "failure_codes": ["LOW_EVIDENCE"],
        "reason": "Needs more context"
    }
    
    # 2. Topic: Not Eligible (READY)
    t2 = {
        "topic_id": "t2",
        "title": "Ready Topic",
        "tags": ["IMMEDIATE"],
        "total_score": 0.9
    }
    q2 = {
        "quality_status": "READY",
        "failure_codes": []
    }
    
    # 3. Topic: Not Eligible (IMMEDIATE, not fact, not structural)
    t3 = {
        "topic_id": "t3",
        "title": "Boring News",
        "risk_one": "Today is the day",
        "tags": ["NEWS"],
        "total_score": 0.5
    }
    q3 = {
        "quality_status": "HOLD",
        "failure_codes": ["LOW_PRIORITY"]
    }

    # 4. Topic: Rejected for critical reason
    t4 = {
        "topic_id": "t4",
        "title": "Mismatch",
        "is_fact_driven": True,
        "tags": ["FACT_NEWS"]
    }
    q4 = {
        "quality_status": "DROP",
        "failure_codes": ["TITLE_MISMATCH"]
    }

    candidates = {"candidates": [t1, t2, t3, t4]}
    (gate_dir / "topic_gate_candidates.json").write_text(json.dumps(candidates))
    
    (gate_dir / "script_v1_t1.md.quality.json").write_text(json.dumps(q1))
    (gate_dir / "script_v1_t2.md.quality.json").write_text(json.dumps(q2))
    (gate_dir / "script_v1_t3.md.quality.json").write_text(json.dumps(q3))
    (gate_dir / "script_v1_t4.md.quality.json").write_text(json.dumps(q4))
    
    return tmp_path

def test_shadow_pool_filtering(mock_setup):
    builder = ShadowCandidateBuilder(mock_setup)
    result = builder.build("2026-01-26")
    
    assert result["count"] == 1
    assert result["candidates"][0]["topic_id"] == "t1"
    assert result["candidates"][0]["impact_window"] == "MID"

def test_no_ready_in_shadow(mock_setup):
    builder = ShadowCandidateBuilder(mock_setup)
    result = builder.build("2026-01-26")
    
    ids = [c["topic_id"] for c in result["candidates"]]
    assert "t2" not in ids

def test_rejected_reasons(mock_setup):
    builder = ShadowCandidateBuilder(mock_setup)
    result = builder.build("2026-01-26")
    
    ids = [c["topic_id"] for c in result["candidates"]]
    assert "t4" not in ids # TITLE_MISMATCH
