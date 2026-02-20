import pytest
from src.ops.production_format_router import ProductionFormatRouter, FormatEnum

@pytest.fixture
def router():
    return ProductionFormatRouter()

def test_route_short_only(router):
    topic = {
        "topic_id": "short1",
        "narration_level": 1,
        "impact_tag": "IMMEDIATE",
        "speak_pack": {"numbers": [1]},
        "evidence_refs": [{"label": "ref1"}],
        "risk_note": ""
    }
    res = router.route_topic(topic)
    assert res["format"] == FormatEnum.SHORT_ONLY
    assert "HIGH_PRIORITY_BRIEF" in res["routing_reason"]

def test_route_long_only_level(router):
    topic = {
        "topic_id": "long_lvl",
        "narration_level": 3,
        "impact_tag": "MID",
        "speak_pack": {"numbers": [1, 2]},
        "evidence_refs": [{"label": "ref1"}, {"label": "ref2"}],
        "risk_note": ""
    }
    res = router.route_topic(topic)
    assert res["format"] == FormatEnum.LONG_ONLY
    assert "LEVEL_3" in res["routing_reason"]

def test_route_long_only_density(router):
    topic = {
        "topic_id": "long_dense",
        "narration_level": 1,
        "impact_tag": "LONG",
        "speak_pack": {"numbers": [1, 2, 3]},
        "evidence_refs": [{"label": "ref1"}, {"label": "ref2"}],
        "risk_note": ""
    } # density = 5
    res = router.route_topic(topic)
    assert res["format"] == FormatEnum.LONG_ONLY
    assert "EVIDENCE_DENSE" in res["routing_reason"]

def test_route_both(router):
    topic = {
        "topic_id": "both1",
        "narration_level": 2,
        "impact_tag": "MID",
        "speak_pack": {"numbers": [1]},
        "evidence_refs": [{"label": "ref1"}],
        "risk_note": ""
    } # density = 2
    res = router.route_topic(topic)
    assert res["format"] == FormatEnum.BOTH
    assert "LEVEL_2_MID_IMPACT_DENSE" in res["routing_reason"]

def test_route_priority_long_over_both(router):
    # Matches BOTH (lvl 2, impact MID) but also LONG (density 4)
    topic = {
        "topic_id": "prio1",
        "narration_level": 2,
        "impact_tag": "MID",
        "speak_pack": {"numbers": [1, 2, 3]},
        "evidence_refs": [{"label": "ref1"}],
        "risk_note": ""
    }
    res = router.route_topic(topic)
    assert res["format"] == FormatEnum.LONG_ONLY
    assert "EVIDENCE_DENSE" in res["routing_reason"]

def test_route_complex_risk(router):
    topic = {
        "topic_id": "risk1",
        "narration_level": 1,
        "impact_tag": "IMMEDIATE",
        "speak_pack": {"numbers": [1], "risk_note": "Significant TRADE-OFF between growth and inflation"},
        "evidence_refs": []
    }
    res = router.route_topic(topic)
    assert res["format"] == FormatEnum.LONG_ONLY
    assert "COMPLEX_RISK_CONTEXT" in res["routing_reason"]
