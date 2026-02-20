import pytest
import json
from pathlib import Path
from src.ops.speak_bundle_exporter import SpeakBundleExporter

@pytest.fixture
def exporter(tmp_path):
    return SpeakBundleExporter(tmp_path)

def test_bundle_generation(exporter, tmp_path):
    ymd = "2026-01-26"
    cards = [
        {
            "topic_id": "t1",
            "title": "Topic 1",
            "is_fact_driven": True,
            "impact_window": "IMMEDIATE",
            "level": 3,
            "speak_pack": {
                "one_liner": "This is a test",
                "numbers": [10, 20],
                "watch_next": ["Video A"],
                "risk_note": "No risk"
            },
            "evidence_nodes": [
                {"publisher": "Source 1", "url": "http://example.com/1", "title": "Evidence 1"}
            ],
            "status": "READY"
        },
        {
            "topic_id": "t2",
            "title": "Topic 2",
            "status": "READY"
        }
    ]
    auto_approved_data = {
        "auto_approved": [
            {"topic_id": "t1", "approval_reason": ["REASON_A"]}
        ]
    }
    
    res = exporter.run(ymd, cards, auto_approved_data)
    
    # Check JSON
    json_path = tmp_path / res["json_path"]
    assert json_path.exists()
    data = json.loads(json_path.read_text(encoding="utf-8"))
    assert data["count"] == 1
    assert data["topics"][0]["topic_id"] == "t1"
    assert data["topics"][0]["speak_pack"]["one_liner"] == "This is a test"
    
    # Check Markdown
    md_path = tmp_path / res["md_path"]
    assert md_path.exists()
    content = md_path.read_text(encoding="utf-8")
    assert "Topic 1" in content
    assert "This is a test" in content
    assert "[Source 1]" in content
    assert "2026-01-26" in content

def test_missing_assets_reporting(exporter, tmp_path):
    ymd = "2026-01-26"
    cards = [
        {
            "topic_id": "t_missing",
            "title": "Missing Topic",
            "speak_pack": {}, # Missing one_liner
            "evidence_nodes": [], # Missing evidence
            "status": "READY"
        }
    ]
    auto_approved_data = {
        "auto_approved": [{"topic_id": "t_missing", "approval_reason": []}]
    }
    
    res = exporter.run(ymd, cards, auto_approved_data)
    data = json.loads((tmp_path / res["json_path"]).read_text(encoding="utf-8"))
    
    missing = data["topics"][0]["missing_assets"]
    assert "ONE_LINER" in missing
    assert "EVIDENCE_REFS" in missing
    
    content = (tmp_path / res["md_path"]).read_text(encoding="utf-8")
    assert "Missing Assets" in content
    assert "(no numeric evidence)" in content

def test_empty_bundle(exporter, tmp_path):
    ymd = "2026-01-26"
    res = exporter.run(ymd, [], {"auto_approved": []})
    assert res["count"] == 0
    assert Path(tmp_path / res["json_path"]).exists()
    assert "No topics met" in Path(tmp_path / res["md_path"]).read_text(encoding="utf-8")
