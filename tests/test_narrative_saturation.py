import pytest
import json
from pathlib import Path
from src.ops.narrative_saturation import NarrativeSaturation

@pytest.fixture
def sat_env(tmp_path):
    base_dir = tmp_path / "mock_project"
    base_dir.mkdir()
    (base_dir / "data/topics/gate").mkdir(parents=True)
    return base_dir

def save_snapshot(tracker, ymd, cards):
    path = tracker._get_lock_path(ymd)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"cards": cards}), encoding="utf-8")

def test_axis_derivation():
    # Helper without env
    # Mock class wrapper
    ns = NarrativeSaturation(Path("/tmp"))
    
    # Check deterministic sorting
    t1 = {"tags": ["B", "A"], "is_fact_driven": True}
    assert ns._derive_axis_key(t1) == "A/B | FACT:True"
    
    t2 = {"tags": ["A", "B"], "is_fact_driven": True}
    assert ns._derive_axis_key(t2) == "A/B | FACT:True"
    
    # Check fact false
    t3 = {"tags": ["A"], "is_fact_driven": False}
    assert ns._derive_axis_key(t3) == "A | FACT:False"

def test_compute_saturation(sat_env):
    ns = NarrativeSaturation(sat_env)
    
    # Setup history
    # 2 occurrences of "A | FACT:True"
    save_snapshot(ns, "2026-01-01", [{"status": "READY", "tags": ["A"], "is_fact_driven": True}])
    save_snapshot(ns, "2026-01-02", [{"status": "READY", "tags": ["A"], "is_fact_driven": True}])
    
    # 2 occurrences of "B | FACT:False"
    save_snapshot(ns, "2026-01-03", [{"status": "READY", "tags": ["B"], "is_fact_driven": False}])
    save_snapshot(ns, "2026-01-04", [{"status": "READY", "tags": ["B"], "is_fact_driven": False}])
    
    # Load 14 days from Jan 10
    counts = ns.load_history("2026-01-10", days=14)
    
    # Topic A: 2 prev + 1 current -> Total 2 prev. 
    # Logic: count prev occurrences.
    # Level: 2 -> NORMAL
    t_a = {"tags": ["A"], "is_fact_driven": True}
    res_a = ns.compute_saturation(t_a, counts)
    assert res_a["level"] == "NORMAL"
    assert res_a["count"] == 2
    
    # Setup DENSE scenario (3 prev)
    save_snapshot(ns, "2026-01-05", [{"status": "READY", "tags": ["A"], "is_fact_driven": True}])
    counts = ns.load_history("2026-01-10", days=14)
    
    res_a_dense = ns.compute_saturation(t_a, counts)
    # Count = 3 (Jan 1, 2, 5) -> DENSE
    assert res_a_dense["level"] == "DENSE"
    assert res_a_dense["count"] == 3
    
    # Setup SATURATED scenario (5 prev)
    save_snapshot(ns, "2026-01-06", [{"status": "READY", "tags": ["A"], "is_fact_driven": True}])
    save_snapshot(ns, "2026-01-07", [{"status": "READY", "tags": ["A"], "is_fact_driven": True}])
    counts = ns.load_history("2026-01-10", days=14)
    
    res_a_sat = ns.compute_saturation(t_a, counts)
    # Count = 5 -> SATURATED
    assert res_a_sat["level"] == "SATURATED"
    assert res_a_sat["count"] == 5
    
