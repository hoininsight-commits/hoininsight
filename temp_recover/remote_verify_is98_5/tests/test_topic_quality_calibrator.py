import unittest
import json
import shutil
from pathlib import Path
from datetime import datetime
from src.ops.topic_quality_calibrator import TopicQualityCalibrator

class TestTopicQualityCalibrator(unittest.TestCase):
    def setUp(self):
        self.base_dir = Path("test_calib_tmp")
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.calibrator = TopicQualityCalibrator(self.base_dir)
        self.ymd = "2026-01-26"

    def tearDown(self):
        if self.base_dir.exists():
            shutil.rmtree(self.base_dir)

    def test_log_writing_and_summary(self):
        """1) Verify log written with correct schema and summary logic."""
        # Log 3 topics
        self.calibrator.log_verdict(self.ymd, "T1", "Title 1", "STRONG", "FACT")
        self.calibrator.log_verdict(self.ymd, "T2", "Title 2", "BORDERLINE", "ANOMALY")
        self.calibrator.log_verdict(self.ymd, "T3", "Title 3", "WEAK", "FACT")
        
        # Verify JSONL content
        log_content = self.calibrator.log_file.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(log_content), 3)
        
        record = json.loads(log_content[0])
        self.assertEqual(record["topic_id"], "T1")
        self.assertEqual(record["verdict"], "STRONG")
        self.assertIn("timestamp", record)

        # Verify summary
        summary = self.calibrator.get_todays_summary(self.ymd)
        self.assertEqual(summary["STRONG"], 1)
        self.assertEqual(summary["BORDERLINE"], 1)
        self.assertEqual(summary["WEAK"], 1)

    def test_overwrite_logic(self):
        """2) Overwrite works per topic/day (latest wins)."""
        self.calibrator.log_verdict(self.ymd, "T1", "Title 1", "WEAK")
        self.calibrator.log_verdict(self.ymd, "T1", "Title 1", "STRONG") # Overwrite
        
        summary = self.calibrator.get_todays_summary(self.ymd)
        self.assertEqual(summary["STRONG"], 1)
        self.assertEqual(summary["WEAK"], 0)
        
        latest = self.calibrator.get_latest_verdict(self.ymd, "T1")
        self.assertEqual(latest, "STRONG")

    def test_invalid_verdict(self):
        """3) Invalid verdict raises ValueError."""
        with self.assertRaises(ValueError):
            self.calibrator.log_verdict(self.ymd, "T1", "Title 1", "EXCELLENT")

if __name__ == "__main__":
    unittest.main()
