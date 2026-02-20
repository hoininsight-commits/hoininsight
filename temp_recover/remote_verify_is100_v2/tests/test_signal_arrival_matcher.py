import json
import pytest
from pathlib import Path
from src.ops.signal_arrival_matcher import SignalArrivalMatcher
from src.ops.signal_watchlist import WATCH_SIGNAL_ENUM

@pytest.fixture
def mock_artifacts(tmp_path):
    # Today's path
    ymd = "2026-01-26"
    ymd_path = ymd.replace("-", "/")
    
    # 1. Macro alert (satisfies MACRO_THRESHOLD_CROSSED)
    macro_p = tmp_path / "data" / "reports" / ymd_path / "macro_alerts.json"
    macro_p.parent.mkdir(parents=True, exist_ok=True)
    macro_p.write_text("{}", encoding="utf-8")
    
    # 2. Events.json with earnings (satisfies EARNINGS_RELEASE and POLICY_EVENT_TRIGGERED)
    events_p = tmp_path / "data" / "events" / ymd_path / "events.json"
    events_p.parent.mkdir(parents=True, exist_ok=True)
    events_p.write_text(json.dumps([{"type": "earnings", "content": "Apple Q1"}]), encoding="utf-8")
    
    return tmp_path

def test_signal_arrival_detection(mock_artifacts):
    matcher = SignalArrivalMatcher(mock_artifacts)
    res = matcher.detect_arrivals("2026-01-26")
    
    arrived = res["arrived_signals"]
    assert WATCH_SIGNAL_ENUM.MACRO_THRESHOLD_CROSSED in arrived
    assert WATCH_SIGNAL_ENUM.EARNINGS_RELEASE in arrived
    assert WATCH_SIGNAL_ENUM.POLICY_EVENT_TRIGGERED in arrived
    assert WATCH_SIGNAL_ENUM.NUMERIC_EVIDENCE_APPEAR not in arrived

def test_shadow_matching_logic():
    matcher = SignalArrivalMatcher(Path("."))
    shadow_pool = [
        {
            "topic_id": "t1",
            "watch_signals": [WATCH_SIGNAL_ENUM.EARNINGS_RELEASE, WATCH_SIGNAL_ENUM.NUMERIC_EVIDENCE_APPEAR]
        }
    ]
    arrived = [WATCH_SIGNAL_ENUM.EARNINGS_RELEASE]
    
    res = matcher.match_to_shadows(shadow_pool, arrived)
    s_status = res[0]["signal_status"]
    
    assert WATCH_SIGNAL_ENUM.EARNINGS_RELEASE in s_status["matched_signals"]
    assert WATCH_SIGNAL_ENUM.NUMERIC_EVIDENCE_APPEAR in s_status["unmatched_signals"]

def test_no_arrival_empty_result(tmp_path):
    matcher = SignalArrivalMatcher(tmp_path)
    res = matcher.detect_arrivals("2026-01-26")
    assert res["arrived_signals"] == []
