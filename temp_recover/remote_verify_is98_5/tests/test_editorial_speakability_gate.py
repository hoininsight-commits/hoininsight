import unittest
import json
import os
import shutil
from pathlib import Path
from src.ops.editorial_speakability_gate import EditorialSpeakabilityGate

class TestEditorialSpeakabilityGate(unittest.TestCase):
    def setUp(self):
        self.base_dir = Path("test_speak_tmp")
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.ops_dir = self.base_dir / "data" / "ops"
        self.ops_dir.mkdir(parents=True, exist_ok=True)
        self.gate = EditorialSpeakabilityGate(self.base_dir)
        self.ymd = "2026-01-26"

        # Default dummy data
        self.view_file = self.ops_dir / "topic_view_today.json"
        self.quality_file = self.ops_dir / "topic_quality_review_today.json"

    def tearDown(self):
        if self.base_dir.exists():
            shutil.rmtree(self.base_dir)

    def _write_inputs(self, view, quality):
        self.view_file.write_text(json.dumps(view, indent=2), encoding="utf-8")
        self.quality_file.write_text(json.dumps(quality, indent=2), encoding="utf-8")

    def test_speakable_now(self):
        """1) Verify SPEAKABLE_NOW when all conditions met."""
        view = {"sections": {"ready": [{"topic_id": "T1", "title": "Speakable", "lane": "ANOMALY", "evidence_count": 3}]}}
        quality = {"topics": [{
            "topic_id": "T1",
            "fact_anchor": "STRONG",
            "timing_edge": "ON_TIME",
            "narration_fit": "GOOD",
            "flags": []
        }]}
        self._write_inputs(view, quality)
        
        res = self.gate.run(self.ymd)
        t = res["verdicts"][0]
        self.assertEqual(t["speakability"], "SPEAKABLE_NOW")
        self.assertEqual(len(t["blocking_reasons"]), 0)

    def test_not_speakable_anchor_fail(self):
        """2a) Fails if anchor is WEAK."""
        view = {"sections": {"ready": [{"topic_id": "T2", "title": "Weak Anchor", "lane": "ANOMALY", "evidence_count": 0}]}}
        quality = {"topics": [{
            "topic_id": "T2",
            "fact_anchor": "WEAK",
            "timing_edge": "ON_TIME",
            "narration_fit": "GOOD",
            "flags": []
        }]}
        self._write_inputs(view, quality)
        
        res = self.gate.run(self.ymd)
        t = res["verdicts"][0]
        self.assertEqual(t["speakability"], "NOT_SPEAKABLE_YET")
        self.assertIn("INSUFFICIENT_ANCHOR_STRENGTH", t["blocking_reasons"])

    def test_not_speakable_timing_fail(self):
        """2b) Fails if timing is LATE."""
        view = {"sections": {"ready": [{"topic_id": "T3", "title": "Late Topic"}]}}
        quality = {"topics": [{
            "topic_id": "T3",
            "fact_anchor": "STRONG",
            "timing_edge": "LATE",
            "narration_fit": "GOOD",
            "flags": []
        }]}
        self._write_inputs(view, quality)
        
        res = self.gate.run(self.ymd)
        t = res["verdicts"][0]
        self.assertEqual(t["speakability"], "NOT_SPEAKABLE_YET")
        self.assertIn("TIMING_INVALID_OR_LATE", t["blocking_reasons"])

    def test_not_speakable_fit_fail(self):
        """2c) Fails if fit is POOR."""
        view = {"sections": {"ready": [{"topic_id": "T4", "title": "Poor Fit"}]}}
        quality = {"topics": [{
            "topic_id": "T4",
            "fact_anchor": "STRONG",
            "timing_edge": "ON_TIME",
            "narration_fit": "POOR",
            "flags": []
        }]}
        self._write_inputs(view, quality)
        
        res = self.gate.run(self.ymd)
        t = res["verdicts"][0]
        self.assertEqual(t["speakability"], "NOT_SPEAKABLE_YET")
        self.assertIn("LOW_NARRATIVE_FIT", t["blocking_reasons"])

    def test_not_speakable_risk_fail(self):
        """2d) Fails if HARD_RISK detected."""
        view = {"sections": {"ready": [{"topic_id": "T5", "flags": ["HARD_RISK_TITLE"]}]}}
        quality = {"topics": [{
            "topic_id": "T5",
            "fact_anchor": "STRONG",
            "timing_edge": "ON_TIME",
            "narration_fit": "GOOD",
            "flags": ["HARD_RISK_TITLE"]
        }]}
        self._write_inputs(view, quality)
        
        res = self.gate.run(self.ymd)
        t = res["verdicts"][0]
        self.assertEqual(t["speakability"], "NOT_SPEAKABLE_YET")
        self.assertIn("HARD_RISK_DETECTED", t["blocking_reasons"])

    def test_no_mutation(self):
        """3) Verify no mutation of inputs."""
        view = {"sections": {"ready": [{"topic_id": "TX", "title": "X"}]}}
        view_copy = json.loads(json.dumps(view))
        quality = {"topics": [{"topic_id": "TX", "fact_anchor": "STRONG"}]}
        self._write_inputs(view, quality)
        
        self.gate.run(self.ymd)
        self.assertEqual(view, view_copy)

    def test_empty_results(self):
        """5) Output files generated even when zero topics."""
        self._write_inputs({"sections": {}}, {"topics": []})
        self.gate.run(self.ymd)
        self.assertTrue(os.path.exists(self.base_dir / "data" / "ops" / "topic_speakability_today.json"))
        self.assertTrue(os.path.exists(self.base_dir / "data" / "ops" / "topic_speakability_today.md"))

if __name__ == "__main__":
    unittest.main()
