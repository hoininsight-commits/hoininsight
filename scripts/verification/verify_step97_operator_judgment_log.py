import shutil
import tempfile
import json
import unittest
from pathlib import Path
from datetime import datetime

# Import target module
from src.ops.operator_judgment_log import run_step97_operator_judgment_log, build_operator_log_entry

class TestStep97(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.data_dir = self.test_dir / "data"
        self.decision_dir = self.data_dir / "decision"
        self.logs_dir = self.data_dir / "judgment_logs"
        
        # Setup mock date
        self.ymd = datetime.now().strftime("%Y-%m-%d")
        y, m, d = self.ymd.split("-")
        
        # Create mock input dir
        self.mock_decision_path = self.decision_dir / y / m / d
        self.mock_decision_path.mkdir(parents=True, exist_ok=True)
        
        # Write mock final decision card
        mock_card = {
            "topic_id": "topic_001_mock",
            "decision": {
                "is_locked": True,
                "status": "LOCKED"
            },
            "why_now_rationale": "Mock rationale for verification."
        }
        (self.mock_decision_path / "final_decision_card.json").write_text(json.dumps(mock_card), encoding="utf-8")
        
        # Mock target_date util roughly by overriding get_target_ymd logic via env or mocking
        # Since run_step97 uses src.utils.target_date.get_target_ymd, we might need to patch it
        # But simpler: we just rely on run_step97 defaulting to today if import fails, or we assume test runs today.
        # If run_step97 uses get_target_ymd(), we must ensure it returns "today" for this test to match self.ymd
        # Or we can just let it run and dynamic check the directory.

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_run_step97_creates_log(self):
        # 1. Run
        result = run_step97_operator_judgment_log(base_dir=self.test_dir)
        
        # 2. Assert Success
        self.assertEqual(result["status"], "success")
        
        # 3. Check File
        log_path = Path(result["path"])
        self.assertTrue(log_path.exists())
        
        content = log_path.read_text(encoding="utf-8")
        lines = content.strip().split("\n")
        self.assertEqual(len(lines), 1)
        
        entry = json.loads(lines[0])
        self.assertEqual(entry["engine_state"], "STEP_96_LOCKED")
        self.assertEqual(entry["continuity_flag"], True)
        self.assertEqual(entry["topic_id"], "topic_001_mock")
        self.assertEqual(entry["engine_decision"], "LOCK")
        self.assertEqual(entry["operator_action"], "HOLD") # Default

    def test_append_behavior(self):
        # Run twice
        run_step97_operator_judgment_log(base_dir=self.test_dir)
        result2 = run_step97_operator_judgment_log(base_dir=self.test_dir)
        
        log_path = Path(result2["path"])
        content = log_path.read_text(encoding="utf-8")
        lines = content.strip().split("\n")
        self.assertEqual(len(lines), 2)
        
        entry1 = json.loads(lines[0])
        entry2 = json.loads(lines[1])
        
        self.assertEqual(entry1["topic_id"], "topic_001_mock")
        self.assertEqual(entry2["topic_id"], "topic_001_mock")

if __name__ == "__main__":
    unittest.main()
