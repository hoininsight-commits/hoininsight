import pytest
import json
from pathlib import Path
from src.ops.auto_approval_gate import AutoApprovalGate

@pytest.fixture
def gate(tmp_path):
    return AutoApprovalGate(tmp_path)

def test_auto_approval_all_pass(gate):
    ready_topics = [
        {
            "topic_id": "t1",
            "title": "Critical Policy Topic",
            "status": "READY",
            "level": 3,
            "saturation_level": "MODERATE",
            "failure_codes": [],
            "judgment_notes": ["A solid topic"]
        }
    ]
    auto_priority_data = {
        "candidates": [
            {
                "topic_id": "t1",
                "priority_score": 9,
                "impact_tag": "IMMEDIATE"
            }
        ]
    }
    operator_decisions = {} # No conflict
    
    res = gate.run("2026-01-26", ready_topics, auto_priority_data, operator_decisions)
    assert res["count"] == 1
    assert res["auto_approved"][0]["topic_id"] == "t1"
    assert "TIME_SENSITIVE" in res["auto_approved"][0]["approval_reason"]

def test_auto_approval_fail_score(gate):
    ready_topics = [{"topic_id": "t1", "status": "READY", "level": 3, "saturation_level": "MODERATE", "failure_codes": [], "judgment_notes": []}]
    auto_priority_data = {"candidates": [{"topic_id": "t1", "priority_score": 7, "impact_tag": "IMMEDIATE"}]} # score < 8
    operator_decisions = {}
    
    res = gate.run("2026-01-26", ready_topics, auto_priority_data, operator_decisions)
    assert res["count"] == 0

def test_auto_approval_fail_impact(gate):
    ready_topics = [{"topic_id": "t1", "status": "READY", "level": 3, "saturation_level": "MODERATE", "failure_codes": [], "judgment_notes": []}]
    auto_priority_data = {"candidates": [{"topic_id": "t1", "priority_score": 9, "impact_tag": "MID"}]} # Not IMMEDIATE
    operator_decisions = {}
    
    res = gate.run("2026-01-26", ready_topics, auto_priority_data, operator_decisions)
    assert res["count"] == 0

def test_auto_approval_fail_risk(gate):
    ready_topics = [{"topic_id": "t1", "status": "READY", "level": 3, "saturation_level": "MODERATE", "failure_codes": [], "judgment_notes": ["HIGH RISK topic"]}]
    auto_priority_data = {"candidates": [{"topic_id": "t1", "priority_score": 9, "impact_tag": "IMMEDIATE"}]}
    operator_decisions = {}
    
    res = gate.run("2026-01-26", ready_topics, auto_priority_data, operator_decisions)
    assert res["count"] == 0

def test_auto_approval_fail_operator_conflict(gate):
    ready_topics = [{"topic_id": "t1", "status": "READY", "level": 3, "saturation_level": "MODERATE", "failure_codes": [], "judgment_notes": []}]
    auto_priority_data = {"candidates": [{"topic_id": "t1", "priority_score": 9, "impact_tag": "IMMEDIATE"}]}
    operator_decisions = {"t1": {"operator_action": "REJECTED"}} # Human already decided
    
    res = gate.run("2026-01-26", ready_topics, auto_priority_data, operator_decisions)
    assert res["count"] == 0
