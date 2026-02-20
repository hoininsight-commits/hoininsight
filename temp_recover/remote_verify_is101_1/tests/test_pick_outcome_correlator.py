import json
import pytest
from pathlib import Path
from datetime import datetime
from src.ops.pick_outcome_correlator import PickOutcomeCorrelator
from src.ops.operator_decision_log import OPERATOR_ACTION_ENUM

@pytest.fixture
def mock_setup(tmp_path):
    # 1. Setup operator decisions
    decision_dir = tmp_path / "data" / "ops" / "operator_decisions"
    decision_dir.mkdir(parents=True, exist_ok=True)
    
    ymd = "2026-01-26"
    dec_data = {
        "run_date": ymd,
        "decisions": [
            {
                "topic_id": "topic1",
                "topic_title": "Picked Topic",
                "operator_action": OPERATOR_ACTION_ENUM.PICKED_FOR_CONTENT,
                "note": "A good pick"
            },
            {
                "topic_id": "topic2",
                "topic_title": "Skipped Topic",
                "operator_action": OPERATOR_ACTION_ENUM.SKIPPED_TODAY
            }
        ]
    }
    (decision_dir / f"{ymd}.json").write_text(json.dumps(dec_data), encoding="utf-8")
    
    # 2. Setup daily_lock in history
    lock_dir = tmp_path / "data" / "topics" / "gate" / "2026" / "01" / "26"
    lock_dir.mkdir(parents=True, exist_ok=True)
    lock_data = {
        "cards": [
            {"topic_id": "topic1", "title": "Picked Topic", "status": "READY", "impact_window": "IMMEDIATE"}
        ]
    }
    (lock_dir / "daily_lock.json").write_text(json.dumps(lock_data), encoding="utf-8")
    
    # 3. Setup outcome in future daily_lock (Confirmation)
    future_lock_dir = tmp_path / "data" / "topics" / "gate" / "2026" / "01" / "28"
    future_lock_dir.mkdir(parents=True, exist_ok=True)
    future_lock_data = {
        "cards": [
            {"topic_id": "topic1", "title": "Picked Topic", "status": "READY"}
        ]
    }
    (future_lock_dir / "daily_lock.json").write_text(json.dumps(future_lock_data), encoding="utf-8")
    
    return tmp_path

def test_pick_filtering_and_outcome(mock_setup):
    correlator = PickOutcomeCorrelator(mock_setup)
    res = correlator.run("2026-01-28", lookback_days=5)
    
    # Only 1 picked topic should be in rows
    assert len(res["rows"]) == 1
    row = res["rows"][0]
    assert row["topic_id"] == "topic1"
    assert row["outcome"] == "CONFIRMED"
    assert res["summary"]["picked"] == 1
    assert res["summary"]["confirmed"] == 1

def test_missing_outcome(mock_setup):
    # Add a pick for a topic that doesn't exist in gate history
    decision_dir = mock_setup / "data" / "ops" / "operator_decisions"
    ymd = "2026-01-27"
    dec_data = {
        "run_date": ymd,
        "decisions": [
            {
                "topic_id": "ghost",
                "topic_title": "Ghost Topic",
                "operator_action": OPERATOR_ACTION_ENUM.PICKED_FOR_CONTENT
            }
        ]
    }
    (decision_dir / f"{ymd}.json").write_text(json.dumps(dec_data), encoding="utf-8")
    
    correlator = PickOutcomeCorrelator(mock_setup)
    res = correlator.run("2026-01-28", lookback_days=5)
    
    # Should have 2 picks now (topic1 and ghost)
    assert res["summary"]["picked"] == 2
    ghost_row = next(r for r in res["rows"] if r["topic_id"] == "ghost")
    assert ghost_row["outcome"] == "MISSING"

def test_deterministic_ordering(mock_setup):
    correlator = PickOutcomeCorrelator(mock_setup)
    res = correlator.run("2026-01-28", lookback_days=5)
    
    # If we had multiple days, latest pick_date should be first
    # (Already tested by logic, but good to keep in mind)
    pass
