import pytest
from src.ops.shadow_aging import ShadowAgingCalculator, AGING_ENUM

def test_shadow_aging_buckets():
    calc = ShadowAgingCalculator()
    run_date = "2026-01-26"
    
    # FRESH: 0-7 days
    res = calc.calculate_aging("2026-01-26", run_date)
    assert res["aging_state"] == AGING_ENUM.FRESH
    assert res["days_in_shadow"] == 0
    
    res = calc.calculate_aging("2026-01-19", run_date)
    assert res["aging_state"] == AGING_ENUM.FRESH
    assert res["days_in_shadow"] == 7
    
    # STALE: 8-21 days
    res = calc.calculate_aging("2026-01-18", run_date)
    assert res["aging_state"] == AGING_ENUM.STALE
    assert res["days_in_shadow"] == 8
    
    res = calc.calculate_aging("2026-01-05", run_date)
    assert res["aging_state"] == AGING_ENUM.STALE
    assert res["days_in_shadow"] == 21
    
    # DECAYING: 22-45 days
    res = calc.calculate_aging("2026-01-04", run_date)
    assert res["aging_state"] == AGING_ENUM.DECAYING
    assert res["days_in_shadow"] == 22
    
    res = calc.calculate_aging("2025-12-12", run_date)
    assert res["aging_state"] == AGING_ENUM.DECAYING
    assert res["days_in_shadow"] == 45
    
    # EXPIRED: > 45 days
    res = calc.calculate_aging("2025-12-11", run_date)
    assert res["aging_state"] == AGING_ENUM.EXPIRED
    assert res["days_in_shadow"] == 46
