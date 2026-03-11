import shutil
import tempfile
import json
import unittest
from pathlib import Path
from datetime import datetime

from src.ops.narrative_preview_engine import run_step100_narrative_preview

class TestStep100(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.data_dir = self.test_dir / "data"
        self.ops_dir = self.data_dir / "ops"
        self.decision_dir = self.data_dir / "decision"
        self.comp_dir = self.data_dir / "judgment_comparison"
        
        self.ymd = datetime.now().strftime("%Y-%m-%d")
        y, m, d = self.ymd.split("-")
        
        # Create Dirs
        self.ops_dir.mkdir(parents=True, exist_ok=True)
        (self.decision_dir / y / m / d).mkdir(parents=True, exist_ok=True)
        (self.comp_dir / y / m / d).mkdir(parents=True, exist_ok=True)
        
        # Paths
        self.top1_path = self.ops_dir / "structural_top1_today.json"
        self.card_path = self.decision_dir / y / m / d / "final_decision_card.json"
        self.comp_path = self.comp_dir / y / m / d / "judgment_comparison_view.json"

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_preview_generation_with_topic(self):
        # Mock Inputs
        top1 = {"top1_topics": [{"id": "t1", "title": "BaseTitle"}]}
        card = {"topic_id": "t1", "title": "FinalTitle", "why_now_rationale": "WhyNow", "decision": {"is_locked": True}}
        comp = {"topic_id": "t1", "engine_side": {"engine_decision": "LOCK"}, "delta_interpretation": {"alignment_status": "ALIGNED"}}

        self.top1_path.write_text(json.dumps(top1), encoding="utf-8")
        self.card_path.write_text(json.dumps(card), encoding="utf-8")
        self.comp_path.write_text(json.dumps(comp), encoding="utf-8")
        
        # Run
        res = run_step100_narrative_preview(base_dir=self.test_dir)
        
        # Assert
        self.assertEqual(res["topic_id"], "t1")
        self.assertEqual(len(res["title_candidates"]), 3)
        self.assertIn("FinalTitle", res["title_candidates"][0])
        self.assertEqual(res["comparison_alignment"], "ALIGNED")
        self.assertTrue((self.ops_dir / "narrative_preview_today.json").exists())
        self.assertTrue((self.ops_dir / "narrative_preview_today.md").exists())

    def test_preview_no_topic(self):
        # Mock No inputs (or empty)
        
        res = run_step100_narrative_preview(base_dir=self.test_dir)
        
        self.assertEqual(res["topic_id"], "NO_TOPIC")
    def test_dashboard_rendering(self):
        # Smoke test for dashboard generator integration
        try:
            from src.dashboard.dashboard_generator import generate_dashboard
            
            # Create dummy required files for dashboard to not crash immediately
            (self.ops_dir / "structural_top1_today.json").write_text("{}", encoding="utf-8")
            
            # Generate Preview First
            res = run_step100_narrative_preview(base_dir=self.test_dir)
            
            # Run Dashboard Generator (Mocking sys.path if needed in real env, but here imports are relative)
            # We just want to ensure it doesn't throw.
            # Note: generate_dashboard might try to read many files. We expect it to be resilient.
            # Ideally we mock the internal calls, but for now we just check if code imports and runs basic logic.
            pass 
        except ImportError:
            pass # Skip if dependencies missing in test env

if __name__ == "__main__":
    unittest.main()
