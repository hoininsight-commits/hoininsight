import pytest
from src.ops.signal_watchlist import SignalWatchlistBuilder, WATCH_SIGNAL_ENUM

def test_signal_mapping_earnings():
    builder = SignalWatchlistBuilder()
    shadow_cand = {
        "topic_id": "test_1",
        "trigger_map": {
            "missing_triggers": ["TIME_WINDOW_OPENED"],
            "source_hint": ["earnings release"]
        },
        "impact_window": "NEAR",
        "aging": {"aging_state": "FRESH"}
    }
    res = builder.build_watchlist(shadow_cand)
    assert WATCH_SIGNAL_ENUM.EARNINGS_RELEASE in res["watch_signals"]
    assert res["recheck_window"] == "NEAR"

def test_signal_mapping_onchain():
    builder = SignalWatchlistBuilder()
    shadow_cand = {
        "topic_id": "test_2",
        "trigger_map": {
            "missing_triggers": ["NUMERIC_EVIDENCE_APPEAR"],
            "source_hint": ["on-chain metric"]
        }
    }
    res = builder.build_watchlist(shadow_cand)
    assert WATCH_SIGNAL_ENUM.NUMERIC_EVIDENCE_APPEAR in res["watch_signals"]
    assert WATCH_SIGNAL_ENUM.ONCHAIN_CONFIRMATION in res["watch_signals"]

def test_mapping_macro():
    builder = SignalWatchlistBuilder()
    shadow_cand = {
        "topic_id": "test_3",
        "trigger_map": {
            "missing_triggers": ["FACT_CONFIRMATION_PUBLISHED", "NUMERIC_EVIDENCE_APPEAR"],
            "source_hint": ["macro data"]
        }
    }
    res = builder.build_watchlist(shadow_cand)
    assert WATCH_SIGNAL_ENUM.MACRO_THRESHOLD_CROSSED in res["watch_signals"]
    assert WATCH_SIGNAL_ENUM.NUMERIC_EVIDENCE_APPEAR in res["watch_signals"]

def test_aging_preservation():
    builder = SignalWatchlistBuilder()
    shadow_cand = {
        "topic_id": "test_age",
        "aging": {"aging_state": "STALE"},
        "trigger_map": {}
    }
    res = builder.build_watchlist(shadow_cand)
    assert res["aging_state"] == "STALE"
