import json
import pytest
from pathlib import Path
from src.ops.event_coverage import EventCoverageBuilder

def test_coverage_builder_no_events(tmp_path):
    data_dir = tmp_path / "data"
    events_dir = data_dir / "events" / "2026" / "01" / "26"
    events_dir.mkdir(parents=True)
    events_file = events_dir / "events.json"
    events_file.write_text(json.dumps({"events": []}))
    builder = EventCoverageBuilder(tmp_path)
    report = builder.build("2026-01-26", history_days=1)
    assert report["run_date"] == "2026-01-26"
    assert "NO_EVENTS_ALL" in report["global_flags"]

def test_coverage_builder_partial_events(tmp_path):
    data_dir = tmp_path / "data"
    events_dir = data_dir / "events" / "2026" / "01" / "26"
    events_dir.mkdir(parents=True)
    events = [
        {"event_type": "earnings", "source": {"publisher": "Nasdaq"}},
        {"event_type": "policy", "source": {"publisher": "Fed"}},
    ]
    events_file = events_dir / "events.json"
    events_file.write_text(json.dumps({"events": events}))
    builder = EventCoverageBuilder(tmp_path)
    report = builder.build("2026-01-26", history_days=1)
    assert report["by_gate_family"]["S1"]["events"] == 1
    assert report["by_gate_family"]["S2"]["events"] == 1

def test_coverage_last_seen(tmp_path):
    data_dir = tmp_path / "data"
    d1_dir = data_dir / "events" / "2026" / "01" / "24"
    d1_dir.mkdir(parents=True)
    (d1_dir / "events.json").write_text(json.dumps({"events": [{"event_type": "earnings", "source": {"publisher": "Nasdaq"}}] }))
    d2_dir = data_dir / "events" / "2026" / "01" / "26"
    d2_dir.mkdir(parents=True)
    (d2_dir / "events.json").write_text(json.dumps({"events": []}))
    builder = EventCoverageBuilder(tmp_path)
    report = builder.build("2026-01-26", history_days=3)
    nasdaq = next(s for s in report["by_source"] if s["source_id"] == "Nasdaq")
    assert nasdaq["last_seen_date"] == "2026-01-24"
    assert nasdaq["events_today"] == 0
