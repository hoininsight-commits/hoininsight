import unittest
import json
import os
from pathlib import Path
from src.ops.topic_quality_review import TopicQualityReview

class TestTopicQualityReview(unittest.TestCase):
    def setUp(self):
        self.base_dir = Path("test_review_tmp")
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.reviewer = TopicQualityReview(self.base_dir)
        self.ymd = "2026-01-26"

    def tearDown(self):
        import shutil
        if self.base_dir.exists():
            shutil.rmtree(self.base_dir)

    def test_deterministic_mapping(self):
        """1) Verify deterministic mapping for each enum bucket."""
        topics = [
            {
                "topic_id": "T1",
                "title": "Strong Topic",
                "status": "READY",
                "evidence_count": 3,
                "narration_level": 3,
                "impact_window": "LONG",
                "saturation_level": "NORMAL"
            },
            {
                "topic_id": "T2",
                "title": "Early Weak Topic",
                "status": "HOLD",
                "evidence_count": 0,
                "narration_level": 1,
                "impact_window": "LONG",
                "saturation_level": "NORMAL"
            },
            {
                "topic_id": "T3",
                "title": "Saturated Late Topic",
                "status": "READY",
                "evidence_count": 1,
                "narration_level": 2,
                "impact_window": "NEAR",
                "saturation_level": "SATURATED"
            }
        ]
        
        res = self.reviewer.run(self.ymd, topics)
        t1 = next(t for t in res["topics"] if t["topic_id"] == "T1")
        t2 = next(t for t in res["topics"] if t["topic_id"] == "T2")
        t3 = next(t for t in res["topics"] if t["topic_id"] == "T3")

        # T1 Check (EARLY + STRONG)
        self.assertEqual(t1["fact_anchor"], "STRONG")
        self.assertEqual(t1["timing_edge"], "EARLY")
        self.assertEqual(t1["narration_fit"], "GOOD")
        self.assertEqual(t1["stock_linkability"], "LINKABLE")
        self.assertEqual(t1["hint"], "High preemption candidate")

        # T2 Check
        self.assertEqual(t2["fact_anchor"], "WEAK")
        self.assertEqual(t2["timing_edge"], "EARLY")
        self.assertEqual(t2["narration_fit"], "POOR")
        self.assertEqual(t2["hint"], "Need beneficiary proof") # Lacks direct beneficiary (L1)

        # T3 Check
        self.assertEqual(t3["timing_edge"], "LATE")
        self.assertEqual(t3["hint"], "Avoid repetition")

    def test_missing_fields(self):
        """2) Missing fields -> conservative outputs."""
        topics = [{"topic_id": "T_UNKNOWN"}] # Missing everything
        res = self.reviewer.run(self.ymd, topics)
        t = res["topics"][0]
        
        self.assertEqual(t["fact_anchor"], "WEAK")
        self.assertEqual(t["timing_edge"], "EARLY") # Impact=LONG by default in my logic
        self.assertEqual(t["narration_fit"], "POOR") # Level=1 by default
        self.assertEqual(t["why_now"], "(not specified)")

    def test_no_mutation(self):
        """3) No mutation of topic selection states."""
        topic = {"topic_id": "M1", "status": "READY", "evidence_count": 5}
        topic_input = [topic.copy()]
        self.reviewer.run(self.ymd, topic_input)
        
        self.assertEqual(topic_input[0]["status"], "READY")
        self.assertEqual(topic_input[0]["evidence_count"], 5)

    def test_empty_topics(self):
        """4) Output files created even when topic list is empty."""
        self.reviewer.run(self.ymd, [])
        self.assertTrue(os.path.exists(self.base_dir / "data" / "ops" / "topic_quality_review_today.json"))
        self.assertTrue(os.path.exists(self.base_dir / "data" / "ops" / "topic_quality_review_today.md"))
        
        with open(self.base_dir / "data" / "ops" / "topic_quality_review_today.json", "r") as f:
            data = json.load(f)
            self.assertEqual(data["status"], "No topics to review today")

if __name__ == "__main__":
    unittest.main()
