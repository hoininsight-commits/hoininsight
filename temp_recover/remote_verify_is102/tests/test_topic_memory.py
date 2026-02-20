import pytest
import json
from pathlib import Path
from src.ops.topic_memory import TopicMemory

@pytest.fixture
def memory_env(tmp_path):
    base_dir = tmp_path / "mock_project"
    base_dir.mkdir()
    (base_dir / "data/topics/gate").mkdir(parents=True)
    return base_dir

def save_snapshot(tracker, ymd, cards):
    # Reusing logic similar to PostMortemTracker tests but for TopicMemory
    # TopicMemory uses same daily_lock.json
    path = tracker._get_lock_path(ymd)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"cards": cards}), encoding="utf-8")

def test_classify_new_topic(memory_env):
    mem = TopicMemory(memory_env)
    
    # History is empty
    index = mem.load_memory("2026-01-10")
    
    topic = {"title": "Fresh Topic", "why_today": "Foo"}
    res = mem.classify_topic(topic, index, "Foo")
    assert res["type"] == "NEW_TOPIC"

def test_classify_revisit(memory_env):
    mem = TopicMemory(memory_env)
    
    # History: "Old Topic" appeared 3 days ago
    save_snapshot(mem, "2026-01-07", [{"title": "Old Topic", "status": "READY", "why_today": "Foo"}])
    
    index = mem.load_memory("2026-01-10")
    
    # Current: Same title, Date = 2026-01-10 (3 days later)
    # 3 days <= 7 days -> REVISIT
    topic = {"title": "Old Topic"}
    res = mem.classify_topic(topic, index, "2026-01-10")
    
    assert res["type"] == "REVISIT"
    assert res["meta"]["last_date"] == "2026-01-07"

def test_classify_regime_update(memory_env):
    mem = TopicMemory(memory_env)
    
    # History: "Common Topic" appeared 30 days ago
    save_snapshot(mem, "2025-12-10", [{"title": "Common Topic", "status": "READY"}])
    
    index = mem.load_memory("2026-01-10")
    
    # Current: Date = 2026-01-10 (31 days later)
    # > 7 days -> REGIME_UPDATE
    topic = {"title": "Common Topic"}
    res = mem.classify_topic(topic, index, "2026-01-10")
    
    assert res["type"] == "REGIME_UPDATE"
    assert res["meta"]["last_date"] == "2025-12-10"
