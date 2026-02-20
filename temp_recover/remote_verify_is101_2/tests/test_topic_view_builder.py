import pytest
import json
from pathlib import Path
from src.ops.topic_view_builder import TopicViewBuilder

def test_topic_view_builder_missing_inputs(tmp_path):
    builder = TopicViewBuilder(tmp_path)
    view = builder.build_view(target_date="2026-01-26")
    
    # Everything should be missing
    assert len(view["missing_inputs"]) >= 4
    assert view["counts"]["ready"] == 0
    assert view["counts"]["auto_approved"] == 0
    
    # Verify files created
    assert (tmp_path / "data" / "ops" / "topic_view_today.json").exists()
    md_content = (tmp_path / "data" / "ops" / "topic_view_today.md").read_text()
    assert "# 🧭 TODAY TOPIC VIEW" in md_content
    assert "## 🛡️ AUTO-APPROVED" in md_content
    assert "No AUTO-APPROVED topics today." in md_content

def test_topic_view_builder_with_mock_data(tmp_path):
    # Setup mock auto_approved
    ops_dir = tmp_path / "data" / "ops"
    ops_dir.mkdir(parents=True)
    aa_file = ops_dir / "auto_approved_today.json"
    aa_file.write_text(json.dumps({
        "run_date": "2026-01-26",
        "approved_topics": [
            {"id": "topic_1", "title": "Test Topic", "lane": "LANE_A", "level": 3, "why_now": "Urgent"}
        ]
    }))
    
    builder = TopicViewBuilder(tmp_path)
    view = builder.build_view(target_date="2026-01-26")
    
    assert view["counts"]["auto_approved"] == 1
    assert view["sections"]["auto_approved"][0]["topic_id"] == "topic_1"
    assert "Test Topic" in (ops_dir / "topic_view_today.md").read_text()

def test_topic_view_builder_deterministic(tmp_path):
    builder = TopicViewBuilder(tmp_path)
    view1 = builder.build_view(target_date="2026-01-26")
    view2 = builder.build_view(target_date="2026-01-26")
    
    assert view1 == view2
