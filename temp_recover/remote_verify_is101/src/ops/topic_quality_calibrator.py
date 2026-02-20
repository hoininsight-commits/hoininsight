from __future__ import annotations
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

class TopicQualityCalibrator:
    """
    Step 56: Topic Quality Calibration Loop.
    Logs human editorial judgment (STRONG, BORDERLINE, WEAK) 
    WITHOUT affecting engine logic.
    """

    QUALITY_VERDICTS = ["STRONG", "BORDERLINE", "WEAK"]

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.log_file = base_dir / "data" / "ops" / "topic_quality_log.jsonl"
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def log_verdict(self, ymd: str, topic_id: str, title: str, verdict: str, 
                   lane: str = "FACT", narration_level: int = 1, impact_tag: str = "") -> Dict[str, Any]:
        """
        Appends a quality verdict to the log.
        VERDICT_ENUM: [STRONG, BORDERLINE, WEAK]
        """
        if verdict not in self.QUALITY_VERDICTS:
            raise ValueError(f"Invalid quality verdict: {verdict}. Must be one of {self.QUALITY_VERDICTS}")

        record = {
            "run_date": ymd,
            "topic_id": topic_id,
            "title": title,
            "verdict": verdict,
            "lane": lane,
            "narration_level": narration_level,
            "impact_tag": impact_tag,
            "timestamp": datetime.now().isoformat()
        }

        # Append-only JSONL
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

        return record

    def get_todays_summary(self, ymd: str) -> Dict[str, int]:
        """
        Returns a summary of verdicts for a specific date.
        Latest verdict per topic_id wins.
        """
        if not self.log_file.exists():
            return {"STRONG": 0, "BORDERLINE": 0, "WEAK": 0}

        latest_verdicts = {}
        with open(self.log_file, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip(): continue
                try:
                    record = json.loads(line)
                    if record.get("run_date") == ymd:
                        latest_verdicts[record["topic_id"]] = record["verdict"]
                except: continue

        summary = {"STRONG": 0, "BORDERLINE": 0, "WEAK": 0}
        for v in latest_verdicts.values():
            if v in summary:
                summary[v] += 1
        return summary

    def get_latest_verdict(self, ymd: str, topic_id: str) -> Optional[str]:
        """Returns the latest verdict for a topic on a specific date."""
        if not self.log_file.exists():
            return None

        verdict = None
        with open(self.log_file, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip(): continue
                try:
                    record = json.loads(line)
                    if record.get("run_date") == ymd and record.get("topic_id") == topic_id:
                        verdict = record["verdict"]
                except: continue
        return verdict
