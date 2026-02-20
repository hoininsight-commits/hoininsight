from __future__ import annotations
import json
from pathlib import Path
from src.ops.human_preference_overlay import HumanPreferenceOverlay

def test_insufficient_history(tmp_path):
    # Setup
    base_dir = tmp_path
    overlay = HumanPreferenceOverlay(base_dir)
    
    # Run with no logs
    sig = overlay.build_signature()
    assert sig["status"] == "INSUFFICIENT_HISTORY"
    
    # Run with few logs
    log_file = base_dir / "data" / "ops" / "topic_quality_log.jsonl"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    with open(log_file, "w") as f:
        for i in range(5):
            f.write(json.dumps({"verdict": "STRONG", "timestamp": "2026-01-01T00:00:00"}) + "\n")
            
    sig = overlay.build_signature()
    assert sig["status"] == "INSUFFICIENT_HISTORY"

def test_signature_and_evaluation(tmp_path):
    base_dir = tmp_path
    overlay = HumanPreferenceOverlay(base_dir)
    
    # 1. Create 20+ logs (Mock history)
    log_file = base_dir / "data" / "ops" / "topic_quality_log.jsonl"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    with open(log_file, "w") as f:
        for i in range(25):
            f.write(json.dumps({
                "verdict": "STRONG", 
                "lane": "FACT",
                "narration_level": 3,
                "impact_tag": "LONG",
                "evidence_count": 5,
                "timestamp": "2026-01-26T00:00:00"
            }) + "\n")
            
    sig = overlay.build_signature()
    assert sig["status"] == "SUCCESS"
    assert sig["traits"]["lane"]["FACT"] == 1.0
    assert sig["traits"]["narration_level"]["3"] == 1.0

    # 2. Evaluate today's topic
    topic_view = {
        "run_date": "2026-01-26",
        "sections": {
            "ready": [
                {
                    "topic_id": "T1",
                    "lane": "FACT",
                    "level": 3,
                    "impact": "LONG",
                    "evidence_count": 4
                },
                {
                    "topic_id": "T2",
                    "lane": "ANOMALY",
                    "level": 1,
                    "impact": "NEAR",
                    "evidence_count": 0
                }
            ]
        }
    }
    
    results = overlay.evaluate_today(topic_view)
    assert results["status"] == "SUCCESS"
    
    # T1 should be STRONG (Matches: FACT, LEVEL 3, LONG, BUCKET 3-5)
    assert results["overlays"]["T1"]["overlay_bucket"] == "HUMAN_LIKELY_STRONG"
    
    # T2 should be WEAK (Matches 0)
    assert results["overlays"]["T2"]["overlay_bucket"] == "HUMAN_LIKELY_WEAK"

def test_bucket_logic():
    overlay = HumanPreferenceOverlay(Path("."))
    assert overlay._bucket_evidence(0) == "0"
    assert overlay._bucket_evidence(1) == "1-2"
    assert overlay._bucket_evidence(2) == "1-2"
    assert overlay._bucket_evidence(3) == "3-5"
    assert overlay._bucket_evidence(6) == "6+"
