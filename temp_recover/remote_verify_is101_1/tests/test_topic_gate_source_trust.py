from __future__ import annotations
import pytest
from src.events.source_trust import score_event

def test_high_risk_event_requires_confirmation_without_cross_source():
    event = {
        "event_type": "regulation",
        "title": "test",
        "source": {"publisher": "unknown", "url": "https://blog.example.com"},
        "effective_window": {"start_date": "2026-01-01", "end_date": "2026-12-31"},
        "evidence": []
    }
    score, requires_confirmation, tier = score_event(event, as_of_date="2026-01-24")
    assert requires_confirmation is True
    assert tier in {"B","C"}  # should not be A
    assert score <= 0.7

def test_official_event_can_pass_without_extra_sources():
    event = {
        "event_type": "regulation",
        "title": "test official",
        "source": {"publisher": "EU Commission", "url": "https://ec.europa.eu/somepage"},
        "effective_window": {"start_date": "2026-01-01", "end_date": "2026-12-31"},
        "evidence": [{"label":"window","value":36,"unit":"months"}]
    }
    score, requires_confirmation, tier = score_event(event, as_of_date="2026-01-24")
    assert tier == "A"
    assert requires_confirmation is False
    assert score >= 0.85
