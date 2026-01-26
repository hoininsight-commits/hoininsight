import pytest
import json
from pathlib import Path
from src.ops.auto_prioritizer import AutoPrioritizer

@pytest.fixture
def prioritizer(tmp_path):
    return AutoPrioritizer(tmp_path)

def test_scoring_logic(prioritizer):
    # Topic 1: High priority factors
    topic = {
        "topic_id": "t1",
        "title": "Critical Policy Update",
        "impact_window": "IMMEDIATE", # +3
        "level": 3, # +2
        "is_fact_driven": True, # +2
        "numbers": [123], # +1
        "selection_rationale": ["FED policy shift"], # +1
        "readiness": {"readiness_bucket": "READY_TO_PROMOTE"}, # +1
        # Total: 10
    }
    
    eval_res = prioritizer._evaluate_topic(topic, "READY")
    assert eval_res["priority_score"] == 10
    assert "TIME-SENSITIVE" in eval_res["reason_factors"]
    assert "READY_TO_PROMOTE" in eval_res["reason_factors"]

def test_penalties(prioritizer):
    topic = {
        "topic_id": "t2",
        "title": "Saturated Topic",
        "saturation_level": "SATURATED", # -1
        "failure_codes": ["CEILING_REACHED"] # -2
    }
    eval_res = prioritizer._evaluate_topic(topic, "READY")
    assert eval_res["priority_score"] == -3
    assert "SATURATED_PENALTY" in eval_res["reason_factors"]
    assert "CEILING_PENALTY" in eval_res["reason_factors"]

def test_candidate_pool_fill(prioritizer):
    ready = [{"topic_id": "r1", "title": "Ready 1"}]
    shadow = [
        {"topic_id": "s1", "title": "Nearly 1", "readiness": {"readiness_bucket": "NEARLY_READY"}},
        {"topic_id": "s2", "title": "Promote 1", "readiness": {"readiness_bucket": "READY_TO_PROMOTE"}}
    ]
    
    res = prioritizer.run("2026-01-26", ready, shadow)
    # Should include all 3 since len(ready) < 3
    assert len(res["candidates"]) == 3
    assert any(c["pool_type"] == "NEARLY_READY" for c in res["candidates"])
    assert any(c["pool_type"] == "READY_TO_PROMOTE" for c in res["candidates"])

def test_stable_tie_break(prioritizer):
    ready = [
        {"topic_id": "a", "title": "Topic B", "priority_score": 5},
        {"topic_id": "b", "title": "Topic A", "priority_score": 5}
    ]
    # We mock _evaluate_topic return for run or just use simple inputs if run allows
    # Actually run() calls _evaluate_topic which recalculates it. 
    # Let's provide topics that will result in same score.
    ready = [
        {"topic_id": "t1", "title": "Zebra", "is_fact_driven": True}, # score 2
        {"topic_id": "t2", "title": "Apple", "is_fact_driven": True}  # score 2
    ]
    res = prioritizer.run("2026-01-26", ready, [])
    # Apple should come before Zebra despite same score (stable title sort)
    titles = [c["title"] for c in res["top_candidates"]]
    assert titles == ["Apple", "Zebra"]
