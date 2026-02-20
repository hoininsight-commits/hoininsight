import json
import pytest
from pathlib import Path
from src.ops.operator_decision_log import OperatorDecisionLog, OPERATOR_ACTION_ENUM

def test_log_decision_append(tmp_path):
    log = OperatorDecisionLog(tmp_path)
    ymd = "2026-01-26"
    
    dec1 = {
        "topic_id": "t1",
        "topic_title": "Title 1",
        "topic_type": "READY",
        "operator_action": OPERATOR_ACTION_ENUM.PICKED_FOR_CONTENT,
        "note": "Note 1"
    }
    log.log_decision(ymd, dec1)
    
    dec2 = {
        "topic_id": "t1",
        "topic_title": "Title 1",
        "topic_type": "READY",
        "operator_action": OPERATOR_ACTION_ENUM.SKIPPED_TODAY,
        "note": "Correction"
    }
    log.log_decision(ymd, dec2)
    
    # Verify both exist in log
    data = log.load_decisions(ymd)
    assert len(data["decisions"]) == 2
    
    # Verify latest map takes the last one
    dec_map = log.get_latest_decisions_map(ymd)
    assert dec_map["t1"]["operator_action"] == OPERATOR_ACTION_ENUM.SKIPPED_TODAY
    assert dec_map["t1"]["note"] == "Correction"

def test_multiple_topics(tmp_path):
    log = OperatorDecisionLog(tmp_path)
    ymd = "2026-01-26"
    
    log.log_decision(ymd, {"topic_id": "t1", "operator_action": "PICKED"})
    log.log_decision(ymd, {"topic_id": "t2", "operator_action": "REJECTED"})
    
    dec_map = log.get_latest_decisions_map(ymd)
    assert len(dec_map) == 2
    assert dec_map["t1"]["operator_action"] == "PICKED"
    assert dec_map["t2"]["operator_action"] == "REJECTED"

def test_load_non_existent(tmp_path):
    log = OperatorDecisionLog(tmp_path)
    res = log.load_decisions("1999-01-01")
    assert res["decisions"] == []
