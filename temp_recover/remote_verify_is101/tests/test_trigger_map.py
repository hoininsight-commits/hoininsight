import pytest
from src.ops.trigger_map import TriggerMapBuilder, TRIGGER_ENUM

def test_trigger_mapping_low_evidence_anomaly():
    builder = TriggerMapBuilder()
    shadow_ctx = {
        "lane": "ANOMALY",
        "impact_window": "MID",
        "failure_codes": ["LOW_EVIDENCE"]
    }
    tm = builder.build_trigger_map(shadow_ctx)
    
    assert TRIGGER_ENUM.NUMERIC_EVIDENCE_APPEAR in tm["missing_triggers"]
    assert "on-chain metric" in tm["source_hint"]
    assert tm["earliest_recheck"] == "AFTER_7D"

def test_trigger_mapping_fact_lane():
    builder = TriggerMapBuilder()
    shadow_ctx = {
        "lane": "FACT",
        "impact_window": "NEAR",
        "failure_codes": ["LOW_EVIDENCE"]
    }
    tm = builder.build_trigger_map(shadow_ctx)
    
    assert TRIGGER_ENUM.NUMERIC_EVIDENCE_APPEAR in tm["missing_triggers"]
    # For FACT lane, it might prioritize earnings release or macro data
    assert any(h in tm["source_hint"] for h in ["earnings release", "macro data"])
    assert tm["earliest_recheck"] == "WINDOW_OPEN"
    assert TRIGGER_ENUM.TIME_WINDOW_OPENED in tm["missing_triggers"]

def test_trigger_mapping_contradiction():
    builder = TriggerMapBuilder()
    shadow_ctx = {
        "lane": "ANOMALY",
        "impact_window": "MID",
        "failure_codes": ["CONTRADICTION"]
    }
    tm = builder.build_trigger_map(shadow_ctx)
    
    assert TRIGGER_ENUM.CONTRADICTION_CLEARED in tm["missing_triggers"]
    assert "policy announcement" in tm["source_hint"]

def test_trigger_mapping_deterministic():
    builder = TriggerMapBuilder()
    ctx1 = {"lane": "FACT", "impact_window": "MID", "failure_codes": ["LOW_EVIDENCE"]}
    ctx2 = {"lane": "FACT", "impact_window": "MID", "failure_codes": ["LOW_EVIDENCE"]}
    
    tm1 = builder.build_trigger_map(ctx1)
    tm2 = builder.build_trigger_map(ctx2)
    
    assert tm1 == tm2
