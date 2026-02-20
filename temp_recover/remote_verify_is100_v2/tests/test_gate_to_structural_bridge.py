from __future__ import annotations
import pytest
import json
from pathlib import Path
from src.bridge.gate_to_structural import GateToStructuralBridge

@pytest.fixture
def mappings_path(tmp_path):
    p = tmp_path / "mappings.yml"
    p.write_text("""
mappings:
  - event_type: "earnings"
    mapped_axes: ["Axis1", "Axis2"]
  - event_type: "capital"
    mapped_axes: ["Axis3"]
""", encoding="utf-8")
    return str(p)

@pytest.fixture
def rules_path(tmp_path):
    p = tmp_path / "rules.yml"
    p.write_text("""
parameters:
  repetition_min_count: 2
  min_trust_score: 0.8
  min_evidence_count: 1
""", encoding="utf-8")
    return str(p)

@pytest.fixture
def bridge(mappings_path, rules_path):
    return GateToStructuralBridge(mappings_path, rules_path)

def test_eligible_via_primary_path(bridge):
    topic = {
        "candidate_id": "topic_001",
        "category": "earnings",
        "evidence_refs": ["events:earnings:ev1"],
        "requires_confirmation": False,
        "numbers": [{"label": "Surprise", "value": 10, "unit": "%"}]
    }
    history = [
        {"category": "earnings"},
        {"category": "earnings"}
    ]
    anomalies = []
    events_index = {
        "ev1": {"trust_score": 0.9, "requires_confirmation": False}
    }
    
    result = bridge.process(topic, history, anomalies, events_index=events_index)
    assert result["eligibility"] == "ELIGIBLE"
    assert result["rule_path"] == "PRIMARY"
    assert "Axis1" in result["matched_axes"]
    assert "Surprise: 10 %" in result["evidence_summary"]

def test_eligible_via_boost_path(bridge):
    topic = {
        "candidate_id": "topic_002",
        "category": "capital",
        "evidence_refs": ["events:capital:ev2"],
        "requires_confirmation": False,
        "numbers": [{"label": "Size", "value": 500, "unit": "M"}]
    }
    history = [] # No repetition
    anomalies = [{"severity": "HIGH", "axis": "Axis3"}]
    events_index = {
        "ev2": {"trust_score": 0.85, "requires_confirmation": False}
    }
    
    result = bridge.process(topic, history, anomalies, events_index=events_index)
    assert result["eligibility"] == "ELIGIBLE"
    assert result["rule_path"] == "BOOST"
    assert "Axis3" in result["matched_axes"]

def test_not_eligible_low_trust(bridge):
    topic = {
        "candidate_id": "topic_003",
        "category": "earnings",
        "evidence_refs": ["events:earnings:ev3"],
        "requires_confirmation": False,
        "numbers": [{"label": "Value", "value": 1, "unit": "X"}]
    }
    history = [{"category": "earnings"}, {"category": "earnings"}] # Repetition ok
    anomalies = []
    events_index = {
        "ev3": {"trust_score": 0.5, "requires_confirmation": False}
    }
    
    result = bridge.process(topic, history, anomalies, events_index=events_index)
    assert result["eligibility"] == "NOT_ELIGIBLE"
    assert "LOW_TRUST" in result["eligibility_reason_codes"]

def test_not_eligible_no_signal(bridge):
    topic = {
        "candidate_id": "topic_004",
        "category": "earnings",
        "evidence_refs": ["events:earnings:ev4"],
        "requires_confirmation": False,
        "numbers": [{"label": "Value", "value": 1, "unit": "X"}]
    }
    history = [] # No history
    anomalies = [] # No anomaly
    events_index = {
        "ev4": {"trust_score": 0.9, "requires_confirmation": False}
    }
    
    result = bridge.process(topic, history, anomalies, events_index=events_index)
    assert result["eligibility"] == "NOT_ELIGIBLE"
    assert "NO_SYSTEMIC_SIGNAL" in result["eligibility_reason_codes"]
