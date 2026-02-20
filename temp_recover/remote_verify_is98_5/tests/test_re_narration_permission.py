import pytest
from pathlib import Path
from src.reporters.decision_dashboard import DecisionDashboard

@pytest.fixture
def mock_dash(tmp_path):
    # Minimal mock
    base_dir = tmp_path / "mock_project"
    base_dir.mkdir()
    (base_dir / "data/topics/gate").mkdir(parents=True)
    return DecisionDashboard(base_dir)

def test_permission_new_topic(mock_dash):
    # NEW_TOPIC -> None
    s, r = mock_dash._determine_renarration_permission(
        memory_status="NEW_TOPIC",
        impact_window="MID",
        outcome=None
    )
    assert s is None
    assert r is None

def test_permission_regime_update(mock_dash):
    # REGIME_UPDATE -> PERMITTED
    s, r = mock_dash._determine_renarration_permission(
        memory_status="REGIME_UPDATE",
        impact_window="MID",
        outcome=None
    )
    assert s == "PERMITTED"
    assert "국면 변화" in r

def test_permission_revisit_immediate(mock_dash):
    # REVISIT + IMMEDIATE -> PERMITTED
    s, r = mock_dash._determine_renarration_permission(
        memory_status="REVISIT",
        impact_window="IMMEDIATE",
        outcome=None
    )
    assert s == "PERMITTED"
    assert "시급한 영향력" in r

def test_permission_revisit_failed(mock_dash):
    # REVISIT + FAILED -> PERMITTED
    s, r = mock_dash._determine_renarration_permission(
        memory_status="REVISIT",
        impact_window="LONG",
        outcome="FAILED"
    )
    assert s == "PERMITTED"
    assert "사후 분석" in r

def test_permission_discouraged(mock_dash):
    # REVISIT + MID + NORMAL -> DISCOURAGED
    s, r = mock_dash._determine_renarration_permission(
        memory_status="REVISIT",
        impact_window="MID",
        outcome="CONFIRMED"
    )
    assert s == "DISCOURAGED"
    assert "신규 정보 없음" in r
