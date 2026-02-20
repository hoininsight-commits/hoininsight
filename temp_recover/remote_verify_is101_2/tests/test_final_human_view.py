import pytest
import os
from pathlib import Path
from src.reporters.decision_dashboard import DecisionDashboard

@pytest.fixture
def dash_env(tmp_path):
    base_dir = tmp_path / "mock_project"
    base_dir.mkdir()
    (base_dir / "data/topics/gate").mkdir(parents=True)
    return DecisionDashboard(base_dir)

def test_final_view_toggle(dash_env):
    # Default is full view
    data = {"cards": []}
    md_default = dash_env.render_markdown(data)
    assert "# 🎙️ DAILY EDITORIAL DECISION (FINAL VIEW)" not in md_default
    
    # Toggle via arg
    md_forced = dash_env.render_markdown(data, force_final_view=True)
    assert "# 🎙️ DAILY EDITORIAL DECISION (FINAL VIEW)" in md_forced
    
    # Toggle via env
    os.environ["ENABLE_FINAL_VIEW"] = "ON"
    md_env = dash_env.render_markdown(data)
    assert "# 🎙️ DAILY EDITORIAL DECISION (FINAL VIEW)" in md_env
    del os.environ["ENABLE_FINAL_VIEW"]

def test_final_view_sorting(dash_env):
    cards = [
        # Group 3: Not Speakable
        {"status": "HOLD", "title": "C", "impact_window": "IMMEDIATE"},
        # Group 2: Discouraged
        {"status": "READY", "title": "B", "renarration_status": "DISCOURAGED", "impact_window": "NEAR"},
        # Group 1: New (Implicit Permitted)
        {"status": "READY", "title": "A", "renarration_status": None, "impact_window": "IMMEDIATE", "narration_level": 2},
        # Group 1: Permitted
        {"status": "READY", "title": "D", "renarration_status": "PERMITTED", "impact_window": "NEAR", "narration_level": 1},
    ]
    
    sorted_cards = dash_env._sort_for_final_view(cards)
    titles = [c['title'] for c in sorted_cards]
    
    # Expected:
    # 1. A (Group 1, New, Level 2)
    # 2. D (Group 1, Permitted, Level 1)
    # 3. B (Group 2, Discouraged)
    # 4. C (Group 3, Hold)
    
    assert titles == ["A", "D", "B", "C"]

def test_final_view_content(dash_env):
    data = {"cards": [{
        "status": "READY", "title": "Top Story", "why_today": "Because", 
        "selection_rationale": ["Reason 1", "Reason 2"], "speak_pack": {"one_liner": "Line", "risk_note": "Risk"}
    }]}
    
    md = dash_env.render_markdown(data, force_final_view=True)
    
    # Check diagnostics hidden
    assert "NARRATIVE SATURATION SUMMARY" not in md
    assert "System diagnostics hidden" in md
    
    # Check simplified card content
    assert "### ✅ Top Story" in md
    assert "> **WHY**: Because" in md
    assert "- 🧭 Reason 1 (and 1 more..)" in md
    assert "<details><summary>🎙️ Speak Pack (Script)</summary>" in md
