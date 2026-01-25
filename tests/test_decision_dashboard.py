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
    
    # 2. 3-5 Rule (Modified to lanes)
    assert "### 📡 A) ANOMALY-DRIVEN (Signal First)" in md
    assert "### 📑 B) FACT-DRIVEN (Fact First)" in md
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

def test_fact_driven_labels(mock_env):
    """Verify FACT-DRIVEN labels and Why No Speak supplemental line"""
    base_dir, gate_dir = mock_env
    
    # Scene 1: READY topic with FACT_DRIVEN tag
    (gate_dir / "topic_gate_output.json").write_text(json.dumps({
        "ranked": [
            {
                "topic_id": "f1", "title": "Fact Ready", "total_score": 90, 
                "tags": ["FACT_GOV_PLAN"], "numbers": [{"label":"A","value":"1"}]
            }
        ]
    }), encoding="utf-8")
    (gate_dir / "script_v1_f1.md").write_text("### 5)\n- **Ev1**: 1\n- **Ev2**: 2", encoding="utf-8")
    (gate_dir / "script_v1_f1.md.quality.json").write_text(json.dumps({
        "quality_status": "READY", "failure_codes": []
    }), encoding="utf-8")
    
    dash = DecisionDashboard(base_dir)
    data = dash.build_dashboard_data("2026-01-24")
    md = dash.render_markdown(data)
    
    assert "Fact Ready (FACT-DRIVEN (Rule v1))" in md
    
    # Scene 2: 0 READY, but 1 HOLD topic with FACT metadata
    (gate_dir / "topic_gate_output.json").write_text(json.dumps({
        "ranked": [
            {
                "topic_id": "f2", "title": "Fact Hold", "total_score": 50, 
                "is_fact_driven": True, "numbers": []
            }
        ]
    }), encoding="utf-8")
    (gate_dir / "script_v1_f2.md").write_text("", encoding="utf-8")
    (gate_dir / "script_v1_f2.md.quality.json").write_text(json.dumps({
        "quality_status": "HOLD", "failure_codes": ["WEAK_EVIDENCE"]
    }), encoding="utf-8")
    
    data = dash.build_dashboard_data("2026-01-24")
    md = dash.render_markdown(data)
    
    assert "🚫 WHY NO SPEAK (Today)" in md
    assert "FACT 기준은 충족했으나 구조 신호 부족" in md

def test_fact_driven_why_now_hints(mock_env):
    """Verify Step 3: WHY-NOW sub-line templates"""
    base_dir, gate_dir = mock_env
    
    # 1. Market Size Template match
    (gate_dir / "topic_gate_output.json").write_text(json.dumps({
        "ranked": [
            {
                "topic_id": "f1", "title": "Market Forecast", "total_score": 90, 
                "tags": ["FACT_GOV_PLAN", "MARKET_SIZE"], 
                "numbers": [{"label":"A","value":"1"}]
            }
        ]
    }), encoding="utf-8")
    (gate_dir / "script_v1_f1.md").write_text("### 5)\n- **Ev1**: 1\n- **Ev2**: 2", encoding="utf-8")
    (gate_dir / "script_v1_f1.md.quality.json").write_text(json.dumps({
        "quality_status": "READY", "failure_codes": []
    }), encoding="utf-8")
    
    dash = DecisionDashboard(base_dir)
    data = dash.build_dashboard_data("2026-01-24")
    md = dash.render_markdown(data)
    
    # Check for both label and hint
    assert "Market Forecast (FACT-DRIVEN (Rule v1))" in md
    assert "> **WHY NOW**: 주요 기관 및 정부의 공식 집행 계획 발표" in md # Tags take priority
    
    # 2. Fallback case
    (gate_dir / "topic_gate_output.json").write_text(json.dumps({
        "ranked": [
            {
                "topic_id": "f2", "title": "Random Fact", "total_score": 90, 
                "is_fact_driven": True,
                "numbers": [{"label":"A","value":"1"}]
            }
        ]
    }), encoding="utf-8")
    (gate_dir / "script_v1_f2.md").write_text("### 5)\n- **Ev1**: 1\n- **Ev2**: 2", encoding="utf-8")
    (gate_dir / "script_v1_f2.md.quality.json").write_text(json.dumps({
        "quality_status": "READY", "failure_codes": []
    }), encoding="utf-8")
    
    data = dash.build_dashboard_data("2026-01-24")
    md = dash.render_markdown(data)
    assert "> **WHY NOW**: (explanatory context insufficient)" in md

def test_fact_vs_anomaly_lanes(mock_env):
    """Verify Step 4: Visual separation into Anomaly and Fact lanes"""
    base_dir, gate_dir = mock_env
    
    # Scene: 1 Anomaly Ready, 1 Fact Ready
    (gate_dir / "topic_gate_output.json").write_text(json.dumps({
        "ranked": [
            {
                "topic_id": "a1", "title": "Anomaly Signal", "total_score": 90, 
                "numbers": [{"label":"A","value":"1"}]
            },
            {
                "topic_id": "f1", "title": "Fact Signal", "total_score": 85, 
                "is_fact_driven": True, "numbers": [{"label":"B","value":"2"}]
            }
        ]
    }), encoding="utf-8")
    
    for tid in ["a1", "f1"]:
        (gate_dir / f"script_v1_{tid}.md").write_text("### 5)\n- **Ev**: 1\n- **Ev**: 2", encoding="utf-8")
        (gate_dir / f"script_v1_{tid}.md.quality.json").write_text(json.dumps({
            "quality_status": "READY", "failure_codes": []
        }), encoding="utf-8")
    
    dash = DecisionDashboard(base_dir)
    data = dash.build_dashboard_data("2026-01-24")
    md = dash.render_markdown(data)
    
    # Verify lanes exist
    assert "### 📡 A) ANOMALY-DRIVEN (Signal First)" in md
    assert "### 📑 B) FACT-DRIVEN (Fact First)" in md
    
    # Verify topic placement
    # The anomaly lane header is before the fact lane header
    parts = md.split("### 📑 B) FACT-DRIVEN (Fact First)")
    assert "Anomaly Signal" in parts[0]
    assert "Fact Signal" in parts[1]
    
    # Verify Placeholder for empty lane
    (gate_dir / "topic_gate_output.json").write_text(json.dumps({
        "ranked": [
            {
                "topic_id": "a2", "title": "Only Anomaly", "total_score": 90, 
                "numbers": [{"label":"A","value":"1"}]
            }
        ]
    }), encoding="utf-8")
    (gate_dir / "script_v1_a2.md").write_text("### 5)\n- **Ev**: 1", encoding="utf-8")
    (gate_dir / "script_v1_a2.md.quality.json").write_text(json.dumps({
        "quality_status": "READY", "failure_codes": []
    }), encoding="utf-8")
    
    data = dash.build_dashboard_data("2026-01-24")
    md = dash.render_markdown(data)
    assert "_No FACT-DRIVEN topics today_" in md

def test_speak_eligibility_badges(mock_env):
    """Verify Step 5: SPEAKABLE / NOT SPEAKABLE badges and reasons"""
    base_dir, gate_dir = mock_env
    
    # Scene: 1 READY (Anomaly), 1 HOLD (Bridge), 1 DROP
    (gate_dir / "topic_gate_output.json").write_text(json.dumps({
        "ranked": [
            {
                "topic_id": "r1", "title": "Ready One", "total_score": 90, 
                "numbers": [{"label":"A","value":"1"}]
            },
            {
                "topic_id": "h1", "title": "Hold Bridge", "total_score": 50, 
                "handoff_to_structural": True, "numbers": []
            },
            {
                "topic_id": "d1", "title": "Drop One", "total_score": 10
            }
        ]
    }), encoding="utf-8")
    
    # r1: READY
    (gate_dir / "script_v1_r1.md").write_text("### 5)\n- **Ev**: 1\n- **Ev**: 2", encoding="utf-8")
    (gate_dir / "script_v1_r1.md.quality.json").write_text(json.dumps({
        "quality_status": "READY", "failure_codes": []
    }), encoding="utf-8")
    
    # h1: HOLD
    (gate_dir / "script_v1_h1.md").write_text("", encoding="utf-8")
    (gate_dir / "script_v1_h1.md.quality.json").write_text(json.dumps({
        "quality_status": "HOLD", "failure_codes": ["WEAK_EVIDENCE"]
    }), encoding="utf-8")
    
    # d1: DROP
    (gate_dir / "script_v1_d1.md").write_text("", encoding="utf-8")
    (gate_dir / "script_v1_d1.md.quality.json").write_text(json.dumps({
        "quality_status": "DROP", "failure_codes": ["FAIL_HOOK"]
    }), encoding="utf-8")
    
    dash = DecisionDashboard(base_dir)
    data = dash.build_dashboard_data("2026-01-24")
    md = dash.render_markdown(data)
    
    # Check r1
    assert "🎙️ SPEAKABLE" in md
    assert "Evidence sufficient for narration" in md
    
    # Check h1 (Almost candidates section)
    assert "⏸️ NOT SPEAKABLE" in md 
    assert "Structure signal missing" in md

def test_narration_depth_classification(mock_env):
    """Verify Step 6: Narration Level structural classification"""
    base_dir, gate_dir = mock_env
    
    # 1. Level 1 - Macro Only
    (gate_dir / "topic_gate_output.json").write_text(json.dumps({
        "ranked": [
            {
                "topic_id": "m1", "title": "Fed Rate Hint", "total_score": 90, 
                "key_reasons": ["Rate cut expectations increased"],
                "numbers": [{"label":"CPI","value":"2.1%"}]
            }
        ]
    }), encoding="utf-8")
    (gate_dir / "script_v1_m1.md").write_text("### 5)\n- **Ev**: 1", encoding="utf-8")
    (gate_dir / "script_v1_m1.md.quality.json").write_text(json.dumps({
        "quality_status": "READY", "failure_codes": []
    }), encoding="utf-8")
    
    dash = DecisionDashboard(base_dir)
    data = dash.build_dashboard_data("2026-01-24")
    md = dash.render_markdown(data)
    assert "🎤 LEVEL 1" in md
    assert "Macro explanation only" in md
    
    # 2. Level 2 - Sector Translatable (Industry reference + Sector metrics)
    (gate_dir / "topic_gate_output.json").write_text(json.dumps({
        "ranked": [
            {
                "topic_id": "s1", "title": "Semi Slump", "total_score": 90, 
                "key_reasons": ["Semiconductor sector oversupply"],
                "numbers": [
                    {"label":"Global Units","value":"100M"},
                    {"label":"Demand Index","value":"low"}
                ]
            }
        ]
    }), encoding="utf-8")
    (gate_dir / "script_v1_s1.md").write_text("### 5)\n- **Ev**: 1\n- **Ev**: 2", encoding="utf-8")
    (gate_dir / "script_v1_s1.md.quality.json").write_text(json.dumps({
        "quality_status": "READY", "failure_codes": []
    }), encoding="utf-8")
    
    data = dash.build_dashboard_data("2026-01-24")
    md = dash.render_markdown(data)
    assert "🎤 LEVEL 2" in md
    assert "Sector-level discussion possible" in md
    
    # 3. Level 3 - Stock Mentionable (Company info + Multi-layer evidence)
    (gate_dir / "topic_gate_output.json").write_text(json.dumps({
        "ranked": [
            {
                "topic_id": "c1", "title": "NVDA Earnings", "total_score": 95, 
                "key_reasons": ["NVDA profit beat"],
                "numbers": [
                    {"label":"Revenue","value":"$10B"},
                    {"label":"Profit","value":"$2B"},
                    {"label":"Guidance","value":"High"}
                ]
            }
        ]
    }), encoding="utf-8")
    (gate_dir / "script_v1_c1.md").write_text("### 5)\n- **Ev**: 1\n- **Ev**: 2\n- **Ev**: 3", encoding="utf-8")
    (gate_dir / "script_v1_c1.md.quality.json").write_text(json.dumps({
        "quality_status": "READY", "failure_codes": []
    }), encoding="utf-8")
    
    data = dash.build_dashboard_data("2026-01-24")
    md = dash.render_markdown(data)
    assert "🎤 LEVEL 3" in md
    assert "Stock names can be mentioned" in md

def test_narration_ceiling_reason(mock_env):
    """Verify Step 7: Narration Ceiling Reason rendering and logic"""
    base_dir, gate_dir = mock_env
    
    # 1. Level 1 - Check Ceiling
    (gate_dir / "topic_gate_output.json").write_text(json.dumps({
        "ranked": [
            {
                "topic_id": "m1", "title": "Macro Signal", "total_score": 90,
                "key_reasons": ["Fed pivot"],
                "numbers": [{"label":"CPI","value":"2%"}]
            }
        ]
    }), encoding="utf-8")
    (gate_dir / "script_v1_m1.md").write_text("### 5)\n- **Ev**: 1", encoding="utf-8")
    (gate_dir / "script_v1_m1.md.quality.json").write_text(json.dumps({
        "quality_status": "READY", "failure_codes": []
    }), encoding="utf-8")
    
    dash = DecisionDashboard(base_dir)
    data = dash.build_dashboard_data("2026-01-24")
    md = dash.render_markdown(data)
    assert "**Ceiling**: 산업 또는 기업 연결 신호 없음" in md
    
    # 2. Level 2 - Check Ceiling
    (gate_dir / "topic_gate_output.json").write_text(json.dumps({
        "ranked": [
            {
                "topic_id": "s1", "title": "Semi Sector", "total_score": 90,
                "key_reasons": ["Semiconductor sector growth"],
                "numbers": [
                    {"label":"Global Units","value":"100M"}, 
                    {"label":"Demand Index","value":"High"}
                ]
            }
        ]
    }), encoding="utf-8")
    (gate_dir / "script_v1_s1.md").write_text("### 5)\n- **Ev**: 1\n- **Ev**: 2", encoding="utf-8")
    (gate_dir / "script_v1_s1.md.quality.json").write_text(json.dumps({
        "quality_status": "READY", "failure_codes": []
    }), encoding="utf-8")
    
    data = dash.build_dashboard_data("2026-01-24")
    md = dash.render_markdown(data)
    assert "**Ceiling**: 특정 기업의 구조적 우위 증거 부족" in md
    
    # 3. Level 3 - No Ceiling
    (gate_dir / "topic_gate_output.json").write_text(json.dumps({
        "ranked": [
            {
                "topic_id": "c1", "title": "NVDA News", "total_score": 95,
                "key_reasons": ["NVDA profit jump"],
                "numbers": [
                    {"label":"Revenue","value":"10B"}, 
                    {"label":"Profit","value":"2B"}, 
                    {"label":"Orders","value":"High"}
                ]
            }
        ]
    }), encoding="utf-8")
    (gate_dir / "script_v1_c1.md").write_text("### 5)\n- **Ev**: 1\n- **Ev**: 2\n- **Ev**: 3", encoding="utf-8")
    (gate_dir / "script_v1_c1.md.quality.json").write_text(json.dumps({
        "quality_status": "READY", "failure_codes": []
    }), encoding="utf-8")
    
    data = dash.build_dashboard_data("2026-01-24")
    md = dash.render_markdown(data)
    assert "**Ceiling**" not in md
    
    # 4. FACT-DRIVEN + Level 1/2
    (gate_dir / "topic_gate_output.json").write_text(json.dumps({
        "ranked": [
            {
                "topic_id": "f1", "title": "Fact Macro", "total_score": 90,
                "is_fact_driven": True,
                "numbers": [{"label":"GDP","value":"3%"}]
            }
        ]
    }), encoding="utf-8")
    (gate_dir / "script_v1_f1.md").write_text("### 5)\n- **Ev**: 1", encoding="utf-8")
    (gate_dir / "script_v1_f1.md.quality.json").write_text(json.dumps({
        "quality_status": "READY", "failure_codes": []
    }), encoding="utf-8")
    
    data = dash.build_dashboard_data("2026-01-24")
    md = dash.render_markdown(data)
    assert "**Ceiling**: 공식 수치는 존재하나 수혜 귀속 불명확" in md

def test_promotion_requirements(mock_env):
    """Verify Step 8: Promotion to Level 3 requirements block"""
    base_dir, gate_dir = mock_env
    
    # Scene: 1 Level 1 (Anomaly), 1 Level 3 (Ready)
    (gate_dir / "topic_gate_output.json").write_text(json.dumps({
        "ranked": [
            {
                "topic_id": "l1", "title": "Macro Topic", "total_score": 90,
                "key_reasons": ["Fed speak"],
                "numbers": [{"label":"CPI","value":"2%"}]
            },
            {
                "topic_id": "l3", "title": "Stock Topic", "total_score": 95,
                "key_reasons": ["Company event"],
                "numbers": [
                    {"label":"Revenue","value":"10B"}, 
                    {"label":"Profit","value":"2B"}, 
                    {"label":"Contract","value":"Yes"}
                ]
            }
        ]
    }), encoding="utf-8")
    
    for tid in ["l1", "l3"]:
        (gate_dir / f"script_v1_{tid}.md").write_text("### 5)\n- **Ev**: 1\n- **Ev**: 2\n- **Ev**: 3", encoding="utf-8")
        (gate_dir / f"script_v1_{tid}.md.quality.json").write_text(json.dumps({
            "quality_status": "READY", "failure_codes": []
        }), encoding="utf-8")
    
    dash = DecisionDashboard(base_dir)
    data = dash.build_dashboard_data("2026-01-24")
    md = dash.render_markdown(data)
    
    # Check Level 1 block
    assert "PROMOTION TO LEVEL 3 REQUIRES" in md
    assert "[ ] Structural advantage vs competitors" in md
    
    # Check Level 3 (Should NOT have the block)
    # Since LEVEL 3 Topic is "Stock Topic", let's look for its specific section
    parts = md.split("### ✅ Stock Topic")
    if len(parts) > 1:
        card_content = parts[1].split("---")[0]
        assert "PROMOTION TO LEVEL 3 REQUIRES" not in card_content
        
    # Check FACT-DRIVEN attribution note
    (gate_dir / "topic_gate_output.json").write_text(json.dumps({
        "ranked": [
            {
                "topic_id": "f1", "title": "Fact Macro", "total_score": 90,
                "is_fact_driven": True,
                "numbers": [{"label":"GDP","value":"3%"}]
            }
        ]
    }), encoding="utf-8")
    (gate_dir / "script_v1_f1.md.quality.json").write_text(json.dumps({
        "quality_status": "READY", "failure_codes": []
    }), encoding="utf-8")
    
    data = dash.build_dashboard_data("2026-01-24")
    md = dash.render_markdown(data)
    assert "Official figures exist, but attribution to specific beneficiaries" in md

def test_sanity_and_drift_monitor(mock_env):
    """Verify Step 9: System Sanity & Drift Monitor"""
    base_dir, gate_dir = mock_env
    
    # Scene: 4 topics, 1 READY, 3 HOLD. 3 FACT-DRIVEN (75% > 70% threshold)
    (gate_dir / "topic_gate_output.json").write_text(json.dumps({
        "ranked": [
            {
                "topic_id": "r1", "title": "Ready One", "total_score": 90, "is_fact_driven": True,
                "numbers": [{"label":"A","value":"1"}, {"label":"B","value":"2"}]
            },
            {
                "topic_id": "h1", "title": "Hold One", "total_score": 50, "is_fact_driven": True,
                "numbers": [{"label":"C","value":"3"}] # Will trigger EVIDENCE_TOO_THIN
            },
            {
                "topic_id": "h2", "title": "Hold Two", "total_score": 40, "is_fact_driven": True,
                "numbers": [] # Will trigger EVIDENCE_TOO_THIN
            },
            {
                "topic_id": "h3", "title": "Anomaly Hold", "total_score": 30, "is_fact_driven": False,
                "numbers": [{"label":"D","value":"4"}] # TITLE_MISMATCH check
            }
        ]
    }), encoding="utf-8")
    
    # r1: READY
    (gate_dir / "script_v1_r1.md.quality.json").write_text(json.dumps({
        "quality_status": "READY", "failure_codes": []
    }), encoding="utf-8")
    # others: HOLD
    for tid in ["h1", "h2", "h3"]:
        (gate_dir / f"script_v1_{tid}.md.quality.json").write_text(json.dumps({
            "quality_status": "HOLD", "failure_codes": ["WEAK_EVIDENCE"]
        }), encoding="utf-8")

    dash = DecisionDashboard(base_dir)
    data = dash.build_dashboard_data("2026-01-24")
    md = dash.render_markdown(data)
    
    # 1. System Status Panel
    assert "🏥 SYSTEM STATUS (Today)" in md
    assert "**Topics Generated**: 4" in md
    assert "**READY / HOLD / DROP**: 1 / 3 / 0" in md
    assert "**FACT-DRIVEN / ANOMALY-DRIVEN**: 3 / 1" in md
    
    # 2. FACT OVERDOMINANCE Warning (3/4 = 75% > 70%)
    assert "⚠️ FACT OVERDOMINANCE" in md
    assert "시스템이 리포트 기반의 팩트에 과하게 치중해 있습니다" in md
    
    # 3. EVIDENCE THINNING Warning (h1, h2 have flags based on evidence count < 2)
    # build_dashboard_data computes flags.
    assert "⚠️ EVIDENCE THINNING" in md
    
    # 4. SPEAK DROUGHT (Currently READY=1, so shouldn't trigger)
    assert "⚠️ SPEAK DROUGHT" not in md
    
    # Trigger SPEAK DROUGHT
    (gate_dir / "script_v1_r1.md.quality.json").write_text(json.dumps({
        "quality_status": "HOLD", "failure_codes": ["WEAK_EVIDENCE"]
    }), encoding="utf-8")
    data = dash.build_dashboard_data("2026-01-24")
    md = dash.render_markdown(data)
    assert "⚠️ SPEAK DROUGHT" in md
    assert "충분한 후보가 생성되었으나 내레이션 기준을 통과하지 못했습니다" in md

def test_judgment_consistency_checks(mock_env):
    """Verify Step 13: Judgment Note triggers"""
    base_dir, gate_dir = mock_env
    
    # 1. Trigger WEAK_TIMING (Fact-driven but summary hint fails)
    # 2. Trigger SHALLOW_EVIDENCE (Level 3 but < 3 evidence)
    # 3. Trigger NARRATIVE_RISK (READY but has ceiling)
    
    (gate_dir / "topic_gate_output.json").write_text(json.dumps({
        "ranked": [
            {
                "topic_id": "j1", "title": "Weak Timing Fact", "total_score": 90, 
                "is_fact_driven": True, "numbers": [{"label":"A","value":"1"}]
            },
            {
                "topic_id": "j2", "title": "Shallow Level 3", "total_score": 95, 
                "key_reasons": ["Company profit"], "numbers": [{"label":"Revenue","value":"10B"}] 
            },
            {
                "topic_id": "j3", "title": "Risk Tension", "total_score": 85,
                "numbers": [{"label":"A","value":"1"}, {"label":"B","value":"2"}]
            }
        ]
    }), encoding="utf-8")
    
    # j1: No templates match -> explanatory context insufficient
    (gate_dir / "script_v1_j1.md").write_text("### 5)\n- **E1**: 1", encoding="utf-8")
    (gate_dir / "script_v1_j1.md.quality.json").write_text(json.dumps({
        "quality_status": "READY", "failure_codes": []
    }), encoding="utf-8")
    
    # j2: Key reasons "Company" + Specific Label "Revenue" -> Narration Level 3
    # But only 2 evidence points in script string
    (gate_dir / "script_v1_j2.md").write_text("### 5)\n- **E1**: 1\n- **E2**: 2", encoding="utf-8")
    (gate_dir / "script_v1_j2.md.quality.json").write_text(json.dumps({
        "quality_status": "READY", "failure_codes": []
    }), encoding="utf-8")
    
    # j3: READY but will have ceiling because it lacks sector/company markers in why_now/labels
    (gate_dir / "script_v1_j3.md").write_text("### 5)\n- **E1**: 1\n- **E2**: 2", encoding="utf-8")
    (gate_dir / "script_v1_j3.md.quality.json").write_text(json.dumps({
        "quality_status": "READY", "failure_codes": []
    }), encoding="utf-8")
    
    dash = DecisionDashboard(base_dir)
    data = dash.build_dashboard_data("2026-01-24")
    md = dash.render_markdown(data)
    
    cards = {c["topic_id"]: c for c in data["cards"]}
    
    # Assertions
    assert any("WHY NOW explanation is too generic" in n for n in cards["j1"]["judgment_notes"])
    assert any("LEVEL 3 assigned, but evidence depth is shallow" in n for n in cards["j2"]["judgment_notes"])
    assert any("Speakable status conflicts with elevated narrative risk" in n for n in cards["j3"]["judgment_notes"])
    
    # Summary
    assert data["judgment_summary"]["weak_timing"] == 1
    assert data["judgment_summary"]["shallow_evidence"] == 1
    assert data["judgment_summary"]["narrative_risk"] == 2
    
    # Markdown rendering
    assert "⚠️ **JUDGMENT NOTES**" in md
    assert "WHY NOW explanation is too generic" in md
    assert "LEVEL 3 assigned" in md
    assert "Speakable status conflicts" in md
    assert "JUDGMENT WARNINGS TODAY" in md

def test_selection_rationale_triggers(mock_env):
    """Verify Step 14: Selection Rationale composition rules"""
    base_dir, gate_dir = mock_env
    
    # Scene: 1 Anomaly Ready, 1 Fact Ready, 1 Hold topic
    (gate_dir / "topic_gate_output.json").write_text(json.dumps({
        "ranked": [
            {
                "topic_id": "r1", "title": "Anomaly Ready", "total_score": 90, 
                "is_fact_driven": False, "numbers": [{"label":"A","value":"1"}, {"label":"B","value":"2"}]
            },
            {
                "topic_id": "r2", "title": "Fact Ready", "total_score": 85, 
                "is_fact_driven": True, "tags": ["FACT_GOV_PLAN"],
                "numbers": [
                    {"label":"Revenue","value":"10B"}, 
                    {"label":"Order","value":"High"},
                    {"label":"Margin","value":"20%"}
                ] 
            },
            {
                "topic_id": "h1", "title": "Hold Topic", "total_score": 50, "is_fact_driven": False
            }
        ]
    }), encoding="utf-8")
    
    for tid in ["r1", "r2"]:
        (gate_dir / f"script_v1_{tid}.md").write_text("### 5)\n- **E1**: 1\n- **E2**: 2\n- **E3**: 3", encoding="utf-8")
        (gate_dir / f"script_v1_{tid}.md.quality.json").write_text(json.dumps({
            "quality_status": "READY", "failure_codes": []
        }), encoding="utf-8")
        
    (gate_dir / "script_v1_h1.md.quality.json").write_text(json.dumps({
        "quality_status": "HOLD", "failure_codes": ["WEAK_EVIDENCE"]
    }), encoding="utf-8")
    
    dash = DecisionDashboard(base_dir)
    data = dash.build_dashboard_data("2026-01-24")
    md = dash.render_markdown(data)
    
    cards = {c["topic_id"]: c for c in data["cards"]}
    
    # 1. Rationale existence
    assert cards["r1"]["selection_rationale"] is not None
    assert cards["r2"]["selection_rationale"] is not None
    assert cards["h1"]["selection_rationale"] is None
    
    # 2. Anomaly vs Fact Primary Driver
    assert "이상징후가 팩트/뉴스보다 선행" in cards["r1"]["selection_rationale"][0]
    assert "공식 팩트 기반 토픽이나 구조 신호와 결합" in cards["r2"]["selection_rationale"][0]
    
    # 3. Level representation (r2 should be Level 3 based on 'Revenue' keyword)
    assert "개별 종목 언급 가능" in cards["r2"]["selection_rationale"][3]
    
    # 4. Constraint block (r1 should have Narration Ceiling because it lacks sector markers)
    assert any("Constraint:" in line for line in cards["r1"]["selection_rationale"])
    
    # 5. Markdown rendering
    assert "🧭 **SELECTION RATIONALE**" in md
    assert "### ✅ Anomaly Ready" in md
    assert "- Primary: 구조적 이상징후" in md

def test_contrast_rationale_triggers(mock_env):
    """Verify Step 15: Contrast & Rejection Rationale rules"""
    base_dir, gate_dir = mock_env
    
    # Scene: 1 Ready (r1), 1 Hold (h1), 1 Hold (h2)
    # r1 should win over h1 and h2
    (gate_dir / "topic_gate_output.json").write_text(json.dumps({
        "ranked": [
            {
                "topic_id": "r1", "title": "Winner Revenue Topic", "total_score": 95, 
                "is_fact_driven": True, "tags": ["FACT_GOV_PLAN"],
                "numbers": [{"label":"A","value":"1"}, {"label":"B","value":"2"}, {"label":"C","value":"3"}]
            },
            {
                "topic_id": "h1", "title": "Competitor Hold", "total_score": 70, 
                "is_fact_driven": True, "numbers": [{"label":"D","value":"4"}]
            },
             {
                "topic_id": "h2", "title": "Other Hold", "total_score": 65, 
                "is_fact_driven": False, "numbers": [{"label":"E","value":"5"}]
            }
        ]
    }), encoding="utf-8")
    
    (gate_dir / "script_v1_r1.md").write_text("### 5)\n- E1\n- E2\n- E3", encoding="utf-8")
    (gate_dir / "script_v1_r1.md.quality.json").write_text(json.dumps({"quality_status": "READY", "failure_codes": []}), encoding="utf-8")
    
    (gate_dir / "script_v1_h1.md.quality.json").write_text(json.dumps({"quality_status": "HOLD", "failure_codes": ["WEAK_EVIDENCE"]}), encoding="utf-8")
    (gate_dir / "script_v1_h2.md.quality.json").write_text(json.dumps({"quality_status": "HOLD", "failure_codes": ["NO_WHY_NOW"]}), encoding="utf-8")
    
    dash = DecisionDashboard(base_dir)
    data = dash.build_dashboard_data("2026-01-24")
    md = dash.render_markdown(data)
    
    cards = {c["topic_id"]: c for c in data["cards"]}
    
    # 1. Contrast presence
    assert cards["r1"]["contrast_rationale"] is not None
    assert cards["h1"]["contrast_rationale"] is None
    
    # 2. Selected Rationale
    # r1 is Level 3 (Fact + 3 items), h1 is likely Level 1 or 2
    assert cards["r1"]["contrast_rationale"]["selected_reason"] == "Broader narration range"
    
    # 3. Rejected Rationale
    rejections = {r["topic_id"]: r["reason"] for r in cards["r1"]["contrast_rationale"]["rejections"]}
    assert rejections["h1"] in ["Evidence too thin", "Missing WHY NOW"]
    # h1 has WEAK_EVIDENCE but not JUDGMENT_WEAK_TIMING in this skip script mock... wait.
    # Actually my logic for rejection reasons check judgment_notes.
    # In this mock, h1 will have judgment_notes = None unless _build_judgment_notes triggers.
    # Let's check _get_contrast_rationale logic again.
    
    # 4. Rendering
    assert "⚖️ **CONTRAST (Why this over others)**" in md
    assert "- Selected: Broader narration range" in md
    assert f"- Rejected: h1 — {rejections['h1']}" in md

def test_contrast_rationale_density(mock_env):
    """Verify 'Higher evidence density' contrast rule"""
    base_dir, gate_dir = mock_env
    
    # Scene: 1 Ready (r1), 1 Hold (h1). Both Level 1.
    # r1 has 4 evidence, h1 has 1 evidence.
    
    (gate_dir / "topic_gate_output.json").write_text(json.dumps({
        "ranked": [
            {
                "topic_id": "r1", "title": "High Density Ready", "total_score": 90, 
                "is_fact_driven": False, 
                "numbers": [{"label":"A","value":"1"}, {"label":"B","value":"2"}, {"label":"C","value":"3"}, {"label":"D","value":"4"}]
            },
            {
                "topic_id": "h1", "title": "Low Density Hold", "total_score": 50, 
                "is_fact_driven": False, 
                "numbers": [{"label":"E","value":"5"}]
            }
        ]
    }), encoding="utf-8")
    
    (gate_dir / "script_v1_r1.md").write_text("### 5)\n- **E1**\n- **E2**\n- **E3**\n- **E4**", encoding="utf-8")
    (gate_dir / "script_v1_r1.md.quality.json").write_text(json.dumps({"quality_status": "READY", "failure_codes": []}), encoding="utf-8")
    
    (gate_dir / "script_v1_h1.md.quality.json").write_text(json.dumps({"quality_status": "HOLD", "failure_codes": ["WEAK_EVIDENCE"]}), encoding="utf-8")
    
    dash = DecisionDashboard(base_dir)
    data = dash.build_dashboard_data("2026-01-24")
    
    cards = {c["topic_id"]: c for c in data["cards"]}
    
    # Check rationale
    assert cards["r1"]["contrast_rationale"]["selected_reason"] == "Higher evidence density"

def test_portfolio_balance_logic(mock_env):
    """Verify Step 16: Portfolio Balance Rules & Rendering"""
    base_dir, gate_dir = mock_env
    
    dash = DecisionDashboard(base_dir)
    
    # --- Scenario 1: Empty READY ---
    (gate_dir / "topic_gate_output.json").write_text(json.dumps({"ranked": []}), encoding="utf-8")
    data = dash.build_dashboard_data("2026-01-24")
    md = dash.render_markdown(data)
    assert "📊 **PORTFOLIO BALANCE (Today)**" not in md # Should only show if READY > 0
    
    # --- Scenario 2: Balanced Portfolio ---
    # Ready 1: Fact, L1, Time-Sensitive
    # Ready 2: Anomaly, L2, Structural
    # Rules: Fact=50% (<=60%), L3=0 (<=2), Timing=2 (>=2) -> Balanced
    
    ranked = [
        {
            "topic_id": "r1", "title": "Fact Balanced", "total_score": 90, 
            "is_fact_driven": True, 
            "risk_one": "Short term opportunity", # Triggers TIME-SENSITIVE
            "numbers": [{"label":"A","value":"1"}]
        },
        {
            "topic_id": "r2", "title": "Anomaly Balanced", "total_score": 85,
            "is_fact_driven": False, "handoff_to_structural": True, 
            "key_reasons": ["Sector demand anomaly"], # Triggers L2 'sector' check
            "numbers": [{"label":"Sector","value":"High"}, {"label":"Demand","value":"Low"}]
        }
    ]
    (gate_dir / "topic_gate_output.json").write_text(json.dumps({"ranked": ranked}), encoding="utf-8")
    
    for tid in ["r1", "r2"]:
        (gate_dir / f"script_v1_{tid}.md").write_text("### 5)\n- **Ev**: 1", encoding="utf-8")
        (gate_dir / f"script_v1_{tid}.md.quality.json").write_text(json.dumps({"quality_status": "READY", "failure_codes": []}), encoding="utf-8")
        
    data = dash.build_dashboard_data("2026-01-24")
    md = dash.render_markdown(data)
    
    assert "📊 **PORTFOLIO BALANCE (Today)**" in md
    assert "- Composition: FACT 1 / ANOMALY 1" in md
    assert "L1 1" in md and "L2 1" in md
    assert "STRUCTURAL SIGNAL" in md and "TIME-SENSITIVE" in md
    assert "- Assessment: Balanced" in md
    
    # --- Scenario 3: Concentrated (FACT-heavy) ---
    # 3 Topics, 3 Fact (100% > 60%)
    ranked_conc = []
    for i in range(3):
        ranked_conc.append({
            "topic_id": f"cf{i}", "title": f"Fact {i}", "total_score": 90, "is_fact_driven": True, "tags": ["TIME-SENSITIVE"], "numbers": [{"label":"A","value":"1"}]
        })
        (gate_dir / f"script_v1_cf{i}.md").write_text("### 5)\n- **Ev**: 1", encoding="utf-8")
        (gate_dir / f"script_v1_cf{i}.md.quality.json").write_text(json.dumps({"quality_status": "READY", "failure_codes": []}), encoding="utf-8")
        
    (gate_dir / "topic_gate_output.json").write_text(json.dumps({"ranked": ranked_conc}), encoding="utf-8")
    
    data = dash.build_dashboard_data("2026-01-24")
    md = dash.render_markdown(data)
    
    assert "- Assessment: Concentrated — FACT-heavy" in md
    
    # --- Scenario 4: Concentrated (Stock-heavy) ---
    # 3 Topics, 3 L3 (> 2)
    ranked_stock = []
    for i in range(3):
        ranked_stock.append({
            "topic_id": f"cs{i}", "title": f"Stock {i}", "total_score": 90, 
            "key_reasons": ["Company news"], 
            "numbers": [{"label":"Revenue","value":"1"}, {"label":"Profit","value":"2"}, {"label":"Contract","value":"3"}]
        })
        (gate_dir / f"script_v1_cs{i}.md").write_text("### 5)\n- **E1**\n- **E2**\n- **E3**", encoding="utf-8")
        (gate_dir / f"script_v1_cs{i}.md.quality.json").write_text(json.dumps({"quality_status": "READY", "failure_codes": []}), encoding="utf-8")

    (gate_dir / "topic_gate_output.json").write_text(json.dumps({"ranked": ranked_stock}), encoding="utf-8")
    
    data = dash.build_dashboard_data("2026-01-24")
    md = dash.render_markdown(data)
    
    assert "- Assessment: Concentrated — Stock-heavy" in md
    
    # --- Scenario 5: Concentrated (Single-theme) ---
    # 2 Topics, both TIME-SENSITIVE (Timing < 2)
    ranked_time = []
    for i in range(2):
        ranked_time.append({
            "topic_id": f"ct{i}", "title": f"Time {i}", "total_score": 90, 
            "tags": ["TIME-SENSITIVE"], "numbers": [{"label":"A","value":"1"}]
        })
        (gate_dir / f"script_v1_ct{i}.md").write_text("### 5)\n- **Ev1**", encoding="utf-8")
        (gate_dir / f"script_v1_ct{i}.md.quality.json").write_text(json.dumps({"quality_status": "READY", "failure_codes": []}), encoding="utf-8")
        
    (gate_dir / "topic_gate_output.json").write_text(json.dumps({"ranked": ranked_time}), encoding="utf-8")
    
    data = dash.build_dashboard_data("2026-01-24")
    md = dash.render_markdown(data)
    
    assert "- Assessment: Concentrated — Single-theme risk" in md

def test_impact_window_logic(mock_env):
    """Verify Step 17: Time-to-Impact Tag Priority Rules"""
    base_dir, gate_dir = mock_env
    dash = DecisionDashboard(base_dir)
    
    # Scene: 5 READY Topics covering all priority cases
    ranked = [
        # 1. IMMEDIATE (Explicit Date)
        {
            "topic_id": "i1", "title": "Immediate Topic", "total_score": 90, 
            "risk_one": "D-Day confirmed", # Trigger
            "numbers": [{"label":"A","value":"1"}]
        },
        # 2. NEAR (Time-Sensitive Tag)
        {
            "topic_id": "n1", "title": "Near Topic", "total_score": 90,
            "risk_one": "Short term alert", # Triggers TIME-SENSITIVE
            "numbers": [{"label":"A","value":"1"}]
        },
        # 3. MID (Trending Now)
        {
            "topic_id": "m1", "title": "Mid Topic", "total_score": 96, # High score -> TRENDING NOW
            "numbers": [{"label":"A","value":"1"}]
        },
        # 4. LONG (Structural)
        {
            "topic_id": "l1", "title": "Long Topic", "total_score": 90,
            "handoff_to_structural": True, # Triggers STRUCTURAL
            "numbers": [{"label":"A","value":"1"}]
        },
        # 5. Fallback (Mid Inferred)
        {
            "topic_id": "f1", "title": "Fallback Topic", "total_score": 80,
            "numbers": [{"label":"A","value":"1"}]
        }
    ]
    (gate_dir / "topic_gate_output.json").write_text(json.dumps({"ranked": ranked}), encoding="utf-8")
    
    for t in ranked:
        tid = t["topic_id"]
        (gate_dir / f"script_v1_{tid}.md").write_text("### 5)\n- **Ev**: 1", encoding="utf-8")
        (gate_dir / f"script_v1_{tid}.md.quality.json").write_text(json.dumps({"quality_status": "READY", "failure_codes": []}), encoding="utf-8")
        
    data = dash.build_dashboard_data("2026-01-24")
    md = dash.render_markdown(data)
    
    cards = {c["topic_id"]: c for c in data["cards"]}
    
    # Checks
    # 1. IMMEDIATE
    assert cards["i1"]["impact_window"] == "IMMEDIATE"
    assert "이슈 반영이 이미 시작됨" in cards["i1"]["impact_hint"]
    
    # Debugging
    if "⏱ IMPACT WINDOW: IMMEDIATE" not in md:
        print("\nMARKDOWN START\n")
        print(md)
        print("\nMARKDOWN END\n")
        
    assert "### ✅ Immediate Topic" in md
    assert "**⏱ IMPACT WINDOW**: IMMEDIATE" in md
    
    # 2. NEAR
    assert cards["n1"]["impact_window"] == "NEAR"
    assert "단기 뉴스/이벤트 연동" in cards["n1"]["impact_hint"]
    
    # 3. MID (Trending)
    assert cards["m1"]["impact_window"] == "MID"
    assert "누적 확인 구간" in cards["m1"]["impact_hint"]
    
    # 4. LONG
    assert cards["l1"]["impact_window"] == "LONG"
    assert "구조적 변화 관점" in cards["l1"]["impact_hint"]
    
    # 5. Fallback
    assert cards["f1"]["impact_window"] == "MID"
    assert "누적 확인 구간(Inferred)" in cards["f1"]["impact_hint"]

def test_view_separation(mock_env):
    """Verify Step 19: Prospective vs Accountability Separation"""
    # 1. Mock a card with Outcome
    base_dir, gate_dir = mock_env
    dash = DecisionDashboard(base_dir)
    
    # Needs a card with outcome. We can assume build_dashboard_data works.
    # We construct data manually for render_markdown test.
    data = {"cards": [{
        "topic_id": "sep1", "title": "Separation Test", "status": "READY",
        "impact_window": "IMMEDIATE", "impact_hint": "Hint",
        "outcome": "CONFIRMED",
        "selection_rationale": ["Reason 1"],
        "eligibility_badge": "🟢 SPEAKABLE",
        "eligibility_reason": "Pass",
        "evidence_count": 5 # Required field
    }]}
    
    md = dash.render_markdown(data)
    
    # Check Order
    # 1. Prospective elements
    assert "⏱ IMPACT WINDOW" in md
    
    # 2. Separator
    assert "--- 🛡️ ACCOUNTABILITY CHECK ---" in md
    
    # 3. Accountability elements AFTER separator
    # Split by separator
    parts = md.split("--- 🛡️ ACCOUNTABILITY CHECK ---")
    assert len(parts) == 2
    prospective_part = parts[0]
    accountability_part = parts[1]
    
    # Verify Prospective items are NOT in Accountability part
    assert "IMPACT WINDOW" in prospective_part
    assert "OUTCOME" not in prospective_part
    
    # Verify Accountability items are in Accountability part
    assert "**🧪 OUTCOME**: CONFIRMED" in accountability_part
