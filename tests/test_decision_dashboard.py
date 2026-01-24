import pytest
import shutil
import json
from pathlib import Path
from src.reporters.decision_dashboard import DecisionDashboard

@pytest.fixture
def mock_env(tmp_path):
    # Setup mock registry and data
    reg_dir = tmp_path / "registry"
    reg_dir.mkdir()
    (reg_dir / "decision_reason_map_v1.yml").write_text("""
descriptions:
  READY:
    default: "GO"
  DROP:
    default: "STOP"
    codes:
      - code: "FAIL_HOOK"
        text: "Hook 미달"
""", encoding="utf-8")
    
    data_dir = tmp_path / "data/topics/gate/2026/01/24"
    data_dir.mkdir(parents=True)
    
    # Mock Candidates for Evidence Mapping
    (data_dir / "topic_gate_candidates.json").write_text(json.dumps({
        "candidates": [
            {
                "candidate_id": "c1", 
                "numbers": [{"label": "CPI", "value": "3.2"}],
                "source_event": {"publisher": "BLS", "url": "http://bls.gov/cpi", "title": "CPI Release"}
            }
        ]
    }), encoding="utf-8")

    return tmp_path, data_dir

def test_dashboard_build(mock_env):
    base_dir, gate_dir = mock_env
    
    # 1. Mock Gate Output
    # T4: Sanity Flagged (Title Mismatch + Placeholder + Thin)
    (gate_dir / "script_v1_t4.md").write_text("### 5)\n- **Ev1**: 0", encoding="utf-8")
    (gate_dir / "script_v1_t4.md.quality.json").write_text(json.dumps({
        "quality_status": "HOLD", "failure_codes": ["WEAK_EVIDENCE"]
    }), encoding="utf-8")
    
    # Update gate output mock to include T4 and data for flags
    (gate_dir / "topic_gate_output.json").write_text(json.dumps({
        "ranked": [
            {"topic_id": "t1", "title": "Topic 1", "total_score": 90, "numbers": [{"label":"CPI","value":"3.2"}], "key_reasons":["Logic related to Topic 1"], "source_candidates": ["c1"]},
            {"topic_id": "t4", "title": "Banana Surge", "total_score": 50, "numbers": [{"label":"EV","value":"Needs Data"}], "key_reasons":["Apple price is up"]} 
        ]
    }), encoding="utf-8")
    
    # 2. Mock Scripts & Sidecars
    # T1: READY
    (gate_dir / "script_v1_t1.md").write_text("### 5)\n- **Ev1**: 1\n- **Ev2**: 2", encoding="utf-8")
    (gate_dir / "script_v1_t1.md.quality.json").write_text(json.dumps({
        "quality_status": "READY", "failure_codes": []
    }), encoding="utf-8")
    
    # Run
    dash = DecisionDashboard(base_dir)
    data = dash.build_dashboard_data("2026-01-24")
    
    # Verify Cards
    cards = {c["topic_id"]: c for c in data["cards"]}
    
    # T1 Checks (READY)
    assert cards["t1"]["status"] == "READY"
    assert cards["t1"]["speak_pack"] is not None
    assert cards["t1"]["evidence_refs"] is not None
    
    sp = cards["t1"]["speak_pack"]
    assert "Topic 1" in sp["one_liner"]
    assert "CPI: 3.2" in sp["numbers"]
    
    # Check Evidence Refs
    refs = cards["t1"]["evidence_refs"]
    assert len(refs) > 0
    ref1 = refs[0]
    assert ref1["label"] == "CPI"
    assert ref1["value"] == "3.2"
    # Since we didn't mock candidates.json fully, it should fallback to unknown or defaults if I didn't add it yet.
    # I need to add candidates mock data to test mapping in the setup block first.
    
    # T4 Checks (HOLD)
    # Title "Banana" not in "Apple price is up" -> TITLE_MISMATCH
    assert "TITLE_MISMATCH" in cards["t4"]["flags"]
    assert cards["t4"]["speak_pack"] is None # HOLD should not have speak pack
    
    # Verify Flag Summary
    f_sum = data["flag_summary"]
    assert f_sum["TITLE_MISMATCH"] == 1
    assert f_sum["PLACEHOLDER_EVIDENCE"] == 1
    assert f_sum["EVIDENCE_TOO_THIN"] == 1

def test_dashboard_normalization(mock_env):
    """Verify 3-5 rule, section separation, and reason normalization"""
    base_dir, gate_dir = mock_env
    
    # Create 6 READY topics to test grouping
    ranked = []
    for i in range(1, 7):
        tid = f"r{i}"
        ranked.append({"topic_id": tid, "title": f"Ready {i}", "total_score": 90 - i, "numbers": [{"label": "A", "value": "1"}]})
        (gate_dir / f"script_v1_{tid}.md").write_text("### 5)\n- **Ev**: 1", encoding="utf-8")
        (gate_dir / f"script_v1_{tid}.md.quality.json").write_text(json.dumps({
            "quality_status": "READY", "failure_codes": []
        }), encoding="utf-8")
        
    # Create 1 HOLD topic (sanity flag for evidence thinness)
    # Ensure title "Hold" is in reasons to avoid TITLE_MISMATCH flag taking precedence
    ranked.append({"topic_id": "h1", "title": "Hold 1", "total_score": 50, "numbers": [], "key_reasons": ["Hold on to your hats"]})
    (gate_dir / "script_v1_h1.md").write_text("too thin", encoding="utf-8")
    (gate_dir / "script_v1_h1.md.quality.json").write_text(json.dumps({
        "quality_status": "HOLD", "failure_codes": ["WEAK_EVIDENCE"]
    }), encoding="utf-8")
    
    # Create 1 DROP topic
    ranked.append({"topic_id": "d1", "title": "Drop 1", "total_score": 10})
    (gate_dir / "script_v1_d1.md").write_text("", encoding="utf-8")
    (gate_dir / "script_v1_d1.md.quality.json").write_text(json.dumps({
        "quality_status": "DROP", "failure_codes": ["FAIL_HOOK"]
    }), encoding="utf-8")
    
    (gate_dir / "topic_gate_output.json").write_text(json.dumps({"ranked": ranked}), encoding="utf-8")
    
    # Render
    dash = DecisionDashboard(base_dir)
    data = dash.build_dashboard_data("2026-01-24")
    md = dash.render_markdown(data)
    
    # Assertions
    # 1. Section Separation
    assert "🎬 TODAY — SPEAKABLE TOPICS" in md
    assert "👀 WATCHLIST — NOT YET" in md
    assert "🗑️ ARCHIVE — DROP" in md
    
    # 2. 3-5 Rule
    assert "🎯 RECOMMENDED FOR TODAY" in md
    assert "Additional READY (Optional)" in md
    assert "Ready 1" in md # Primary
    assert "Ready 6" in md # Secondary
    
    # 3. Normalized Reasons
    assert "아직 말하지 않는 이유: 말할 수 있는 근거가 너무 적습니다" in md # h1 evidence thin flag
    assert "Hook 미달" in md # d1 simplified reason substitution
    
    # 4. No Internal Codes
    assert "FAIL_HOOK" not in md # Should be replaced
    assert "WEAK_EVIDENCE" not in md # Should be normalized

def test_recommender_logic(mock_env):
    """Verify tags, why today, and visual aids"""
    base_dir, gate_dir = mock_env
    
    # 1. High Score Ready Topic -> TRENDING NOW
    # 2. Key Reason 'Short term' -> TIME-SENSITIVE
    (gate_dir / "topic_gate_output.json").write_text(json.dumps({
        "ranked": [
            {
                "topic_id": "r1", "title": "Price Surge", "total_score": 95.0, 
                "numbers": [{"label":"A","value":"1"}],
                "key_reasons": ["Price Surge"],
                "risk_one": "Expires today! Short term risk." # Triggers TIME-SENSITIVE
            }
        ]
    }), encoding="utf-8")
    
    # Evidence > 1 to avoid TOO_THIN
    (gate_dir / "script_v1_r1.md").write_text("### 5)\n- **Ev1**: 1\n- **Ev2**: 2", encoding="utf-8")
    (gate_dir / "script_v1_r1.md.quality.json").write_text(json.dumps({
        "quality_status": "READY", "failure_codes": []
    }), encoding="utf-8")
    
    dash = DecisionDashboard(base_dir)
    data = dash.build_dashboard_data("2026-01-24")
    md = dash.render_markdown(data)
    
    # Assertions
    # 1. Disclaimer
    assert "※ 시스템은 선택하지 않습니다" in md
    
    # 2. Tags
    # Score 95 -> TRENDING NOW
    # 'today' in reasons -> TIME-SENSITIVE
    cards = {c["topic_id"]: c for c in data["cards"]}
    tags = cards["r1"]["tags"]
    assert "🔥 TRENDING NOW" in tags
    assert "⏳ TIME-SENSITIVE" in tags
    assert len(tags) <= 2
    
    # 3. Why Today
    # Check data directly
    why = cards["r1"]["why_today"]
    assert why is not None
    assert "Price Surge" in why
    
    # Check markdown
    assert f"**오늘 찍는 이유**: {why}" in md
    
    # Data Check
    assert "Price Surge" in md
    
    # 4. Visual Layout
    # Check that tags are rendered in markdown
    assert "🔥 TRENDING NOW" in md

def test_daily_lock_snapshot(mock_env):
    """Verify daily_lock.json creation"""
    base_dir, gate_dir = mock_env
    
    # Mock Data
    (gate_dir / "topic_gate_output.json").write_text(json.dumps({
        "ranked": [{"topic_id": "t1", "title": "LockTest", "total_score": 90}]
    }), encoding="utf-8")
    
    dash = DecisionDashboard(base_dir)
    data = dash.build_dashboard_data("2026-01-24")
    
    # Snapshot
    lock_path = dash.save_snapshot("2026-01-24", data)
    
    assert lock_path.exists()
    assert lock_path.name == "daily_lock.json"
    
    # Content Check
    saved = json.loads(lock_path.read_text(encoding="utf-8"))
    assert saved["cards"][0]["title"] == "LockTest"
    assert "summary" in saved

def test_dashboard_hardening(mock_env):
    """Verify Visibility Hardening features: No Speak Panel, Almost Candidates, Quality Counters"""
    base_dir, gate_dir = mock_env
    
    # Scenario: 0 READY, 1 HOLD, 1 DROP
    # This triggers "Why No Speak" and "Almost Candidates"
    ranked = []
    
    # HOLD Topic
    ranked.append({
        "topic_id": "h1", "title": "HoldOne", "total_score": 50, 
        "numbers": [], "handoff_to_structural": True # Check bridge eligible
    })
    (gate_dir / "script_v1_h1.md").write_text("", encoding="utf-8")
    (gate_dir / "script_v1_h1.md.quality.json").write_text(json.dumps({
        "quality_status": "HOLD", "failure_codes": ["WEAK_EVIDENCE"] # Normalized: 근거 수치 부족
    }), encoding="utf-8")
    
    # DROP Topic
    ranked.append({
        "topic_id": "d1", "title": "DropOne", "total_score": 10, "numbers": []
    })
    (gate_dir / "script_v1_d1.md").write_text("", encoding="utf-8")
    (gate_dir / "script_v1_d1.md.quality.json").write_text(json.dumps({
        "quality_status": "DROP", "failure_codes": ["FAIL_HOOK"]
    }), encoding="utf-8")
    
    (gate_dir / "topic_gate_output.json").write_text(json.dumps({"ranked": ranked}), encoding="utf-8")
    
    dash = DecisionDashboard(base_dir)
    data = dash.build_dashboard_data("2026-01-24")
    md = dash.render_markdown(data)
    
    # 1. WHY NO SPEAK Panel
    assert "🚫 WHY NO SPEAK (Today)" in md
    assert "오늘은 영상화 가능한 토픽이 없습니다" in md
    # Check normalized reason or code
    # WEAK_EVIDENCE normalization -> "근거 데이터가 부족합니다" or similar from mock yaml
    # Wait, my test mock YAML defines default texts.
    # In earlier tests I verified "WEAK_EVIDENCE" not in md, replaced by normalized.
    # But in 'Why No Speak' panel I used `no_speak_analysis` which uses `_get_code_desc`.
    # Let's check for the text defined in mock yaml for WEAK_EVIDENCE (which is default?)
    # I didn't define WEAK_EVIDENCE explicitly in earlier mock yaml, so it might use code or default?
    # Actually, in `_get_code_desc`, if code not found, returns code.
    # But `no_speak_analysis` logic: `_get_code_desc(status="DROP", code=code)`.
    # Let's check if WEAK_EVIDENCE appears (as it might fallback to code if not in map).
    
    # 2. TOP CANDIDATES (Almost)
    assert "🥈 TOP CANDIDATES (Almost)" in md
    assert "HoldOne" in md
    assert "DropOne" in md
    assert "Bridge Capable" in md # h1 has handoff_to_structural
    
    # 3. Script Quality Counters
    assert "**SCRIPT QUALITY**: 🟢 READY=0 | 🟡 HOLD=1 | 🔴 DROP=1" in md
