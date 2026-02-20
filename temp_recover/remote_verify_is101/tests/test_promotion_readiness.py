import pytest
from src.ops.promotion_readiness import PromotionReadinessCalculator, READINESS_ENUM

def test_readiness_buckets():
    calc = PromotionReadinessCalculator()
    
    # READY_TO_PROMOTE: 2 required, 2 matched (0 missing)
    res = calc.calculate_readiness(["S1", "S2"], ["S1", "S2"])
    assert res["readiness_bucket"] == READINESS_ENUM.READY_TO_PROMOTE
    assert res["missing_count"] == 0
    assert res["matched_count"] == 2
    
    # NEARLY_READY: 2 required, 1 matched (1 missing)
    res = calc.calculate_readiness(["S1", "S2"], ["S1"])
    assert res["readiness_bucket"] == READINESS_ENUM.NEARLY_READY
    assert res["missing_count"] == 1
    
    # IN_PROGRESS: 4 required, 2 matched (2 missing)
    res = calc.calculate_readiness(["S1", "S2", "S3", "S4"], ["S1", "S2"])
    assert res["readiness_bucket"] == READINESS_ENUM.IN_PROGRESS
    assert res["missing_count"] == 2
    
    # FAR: 5 required, 1 matched (4 missing)
    res = calc.calculate_readiness(["S1", "S2", "S3", "S4", "S5"], ["S1"])
    assert res["readiness_bucket"] == READINESS_ENUM.FAR
    assert res["missing_count"] == 4

def test_operator_hints():
    calc = PromotionReadinessCalculator()
    
    hint_ready = calc.get_operator_hint(READINESS_ENUM.READY_TO_PROMOTE, [])
    assert "Re-run pipeline" in hint_ready
    
    hint_nearly = calc.get_operator_hint(READINESS_ENUM.NEARLY_READY, ["MACRO_THRESHOLD_CROSSED"])
    assert "Watch for MACRO_THRESHOLD_CROSSED" in hint_nearly
    
    hint_far = calc.get_operator_hint(READINESS_ENUM.FAR, ["S1", "S2", "S3", "S4"])
    assert hint_far == ""

def test_deterministic_output():
    calc = PromotionReadinessCalculator()
    req = ["A", "B", "C"]
    match = ["A"]
    
    res1 = calc.calculate_readiness(req, match)
    res2 = calc.calculate_readiness(req, match)
    
    assert res1 == res2
