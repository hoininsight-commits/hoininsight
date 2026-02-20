import pytest
import json
from pathlib import Path
from src.ops.topic_seed_builder import TopicSeedBuilder

def test_topic_seed_builder_clustering(tmp_path):
    builder = TopicSeedBuilder(tmp_path)
    
    facts = [
        {
            "fact_id": "f1",
            "fact_type": "TECH",
            "fact_text": "Nvidia AI chip delivery",
            "entities": ["Nvidia", "AI"],
            "published_at": "2026-01-26",
            "structural_frames": [{"frame": "TECH_INFLECTION", "reason": "..."}]
        },
        {
            "fact_id": "f2",
            "fact_type": "BUDGET",
            "fact_text": "US chip funding",
            "entities": ["AI", "Semiconductors"],
            "published_at": "2026-01-25",
            "structural_frames": [{"frame": "TECH_INFLECTION", "reason": "..."}]
        },
        {
            "fact_id": "f3",
            "fact_type": "POLICY",
            "fact_text": "Random regulation in unrelated field",
            "entities": ["Agriculture"],
            "published_at": "2026-01-26",
            "structural_frames": [{"frame": "POLICY_SHIFT", "reason": "..."}]
        }
    ]
    
    seeds = builder.build_seeds(facts)
    
    # f1 and f2 should cluster (shared frame "TECH_INFLECTION", shared entity "AI")
    # f3 should be a separate seed
    assert len(seeds) == 2
    
    # Check seed 1 properties
    s1 = next(s for s in seeds if "f1" in s["supporting_facts"])
    assert "f2" in s1["supporting_facts"]
    assert "TECH_INFLECTION" in s1["structural_frames"]
    assert s1["status"] == "SHADOW_ONLY"
    assert "Nvidia" in s1["seed_summary"]
    assert "Semiconductors" in s1["seed_summary"]

    # Verify file saved
    out_file = tmp_path / "data" / "ops" / "topic_seeds.json"
    assert out_file.exists()
    
def test_topic_seed_builder_time_window(tmp_path):
    builder = TopicSeedBuilder(tmp_path)
    
    facts = [
        {
            "fact_id": "f1",
            "fact_type": "TECH",
            "fact_text": "Fact today",
            "entities": ["Nvidia"],
            "published_at": "2026-01-26",
            "structural_frames": [{"frame": "TECH_INFLECTION", "reason": "..."}]
        },
        {
            "fact_id": "f2",
            "fact_type": "TECH",
            "fact_text": "Fact 20 days ago",
            "entities": ["Nvidia"],
            "published_at": "2026-01-01",
            "structural_frames": [{"frame": "TECH_INFLECTION", "reason": "..."}]
        }
    ]
    
    # Window is 14 days by default, so they should NOT cluster
    seeds = builder.build_seeds(facts)
    assert len(seeds) == 2
