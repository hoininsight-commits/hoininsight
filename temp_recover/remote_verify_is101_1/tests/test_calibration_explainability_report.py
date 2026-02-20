from __future__ import annotations
import json
from pathlib import Path
from src.ops.calibration_explainability_report import CalibrationExplainabilityReport

def test_mismatch_detection(tmp_path):
    base_dir = tmp_path
    report = CalibrationExplainabilityReport(base_dir)
    
    # Setup inputs
    ymd = "2026-01-26"
    
    # 1. Overlay (T1: LIKELY_WEAK)
    ov_dir = base_dir / "data" / "ops"
    ov_dir.mkdir(parents=True)
    (ov_dir / "human_pref_overlay_today.json").write_text(json.dumps({
        "overlays": {
            "T1": {
                "overlay_bucket": "HUMAN_LIKELY_WEAK",
                "missing_traits": ["EVIDENCE_6+"]
            },
            "T2": {
                "overlay_bucket": "HUMAN_LIKELY_STRONG",
                "matched_traits": ["FACT", "LEVEL_3"]
            }
        }
    }), encoding="utf-8")
    
    # 2. View
    (ov_dir / "topic_view_today.json").write_text(json.dumps({
        "sections": {
            "ready": [{"topic_id": "T1", "title": "Topic One"}, {"topic_id": "T2", "title": "Topic Two"}]
        }
    }), encoding="utf-8")
    
    # 3. Quality Log (T1: STRONG)
    log_file = ov_dir / "topic_quality_log.jsonl"
    with open(log_file, "w") as f:
        f.write(json.dumps({"run_date": ymd, "topic_id": "T1", "verdict": "STRONG"}) + "\n")
        f.write(json.dumps({"run_date": ymd, "topic_id": "T2", "verdict": "WEAK"}) + "\n")

    # Run
    res = report.run(ymd)
    
    assert res["label_counts"]["STRONG"] == 1
    assert len(res["mismatch_cases"]) == 2
    
    # Case 1: STRONG but Weak overlay
    m1 = next(m for m in res["mismatch_cases"] if m["topic_id"] == "T1")
    assert "missing" in m1["why"][0]
    
    # Case 2: WEAK but Strong overlay
    m2 = next(m for m in res["mismatch_cases"] if m["topic_id"] == "T2")
    assert "matches" in m2["why"][0]

def test_graceful_fallback(tmp_path):
    base_dir = tmp_path
    report = CalibrationExplainabilityReport(base_dir)
    # No files created
    res = report.run("2026-01-26")
    assert len(res["errors"]) > 0
    assert res["label_counts"]["UNLABELED"] == 0
