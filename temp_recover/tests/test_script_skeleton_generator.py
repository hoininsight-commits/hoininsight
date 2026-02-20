import pytest
import json
from pathlib import Path
from src.ops.script_skeleton_generator import ScriptSkeletonGenerator

@pytest.fixture
def generator(tmp_path):
    return ScriptSkeletonGenerator(tmp_path)

def test_skeleton_generation_both(generator, tmp_path):
    ymd = "2026-01-26"
    bundle_data = {
        "topics": [
            {
                "topic_id": "t1",
                "title": "Topic 1",
                "production_format": "BOTH",
                "impact_tag": "IMMEDIATE",
                "speak_pack": {
                    "one_liner": "Test Hook",
                    "numbers": ["100%"],
                    "risk_note": "A risk note",
                    "watch_next": ["Video A"]
                },
                "evidence_refs": [{"publisher": "P1", "url": "U1"}]
            }
        ]
    }
    
    index = generator.run(ymd, bundle_data)
    assert index["count_short"] == 1
    assert index["count_long"] == 1
    
    sk_dir = tmp_path / "data/ops/bundles/2026/01/26/skeletons"
    assert (sk_dir / "topic_t1_short.md").exists()
    assert (sk_dir / "topic_t1_long.md").exists()
    
    short_content = (sk_dir / "topic_t1_short.md").read_text(encoding="utf-8")
    assert "# TITLE\nTopic 1" in short_content
    assert "Test Hook" in short_content
    assert "- 100%" in short_content
    assert "- P1 — U1" in short_content
    
    long_content = (sk_dir / "topic_t1_long.md").read_text(encoding="utf-8")
    assert "# TITLE\nTopic 1" in long_content
    assert "Hook: Test Hook" in long_content
    assert "Video A" in long_content
    assert "A risk note" in long_content

def test_no_numeric_evidence_fallback(generator, tmp_path):
    ymd = "2026-01-26"
    bundle_data = {
        "topics": [
            {
                "topic_id": "t2",
                "title": "Topic 2",
                "production_format": "SHORT_ONLY",
                "speak_pack": {"one_liner": "No nums", "numbers": []}
            }
        ]
    }
    generator.run(ymd, bundle_data)
    sk_path = tmp_path / "data/ops/bundles/2026/01/26/skeletons/topic_t2_short.md"
    content = sk_path.read_text(encoding="utf-8")
    assert "(no numeric evidence)" in content

def test_missing_refs_fallback(generator, tmp_path):
    ymd = "2026-01-26"
    bundle_data = {
        "topics": [
            {
                "topic_id": "t3",
                "title": "Topic 3",
                "production_format": "SHORT_ONLY",
                "evidence_refs": []
            }
        ]
    }
    generator.run(ymd, bundle_data)
    sk_path = tmp_path / "data/ops/bundles/2026/01/26/skeletons/topic_t3_short.md"
    content = sk_path.read_text(encoding="utf-8")
    assert "No verifiable evidence available" in content
