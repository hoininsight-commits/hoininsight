import shutil
import tempfile
import json
import unittest
from pathlib import Path
from datetime import datetime

# Import target module
from src.ops.judgment_ledger import run_step98_judgment_ledger, classify_judgment

class TestStep98(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.data_dir = self.test_dir / "data"
        self.log_dir = self.data_dir / "judgment_logs"
        self.ledger_dir = self.data_dir / "judgment_ledger"
        
        self.ymd = datetime.now().strftime("%Y-%m-%d")
        y, m, d = self.ymd.split("-")
        
        # Create mock input dir
        self.mock_log_path = self.log_dir / y / m / d
        self.mock_log_path.mkdir(parents=True, exist_ok=True)
        
        # Write mock Step 97 log
        mock_entry = {
            "date": self.ymd,
            "time": "10:00",
            "engine_state": "STEP_96_LOCKED",
            "topic_id": "topic_001_mock",
            "engine_decision": "PASS",
            "operator_action": "HOLD",
            "continuity_flag": True
        }
        (self.mock_log_path / "operator_judgment_log.jsonl").write_text(json.dumps(mock_entry) + "\n", encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_run_step98_creates_ledger(self):
        # 1. Run
        result = run_step98_judgment_ledger(base_dir=self.test_dir)
        
        # 2. Assert Success
        self.assertEqual(result["status"], "success")
        
        # 3. Check File
        ledger_path = Path(result["path"])
        self.assertTrue(ledger_path.exists())
        
        content = ledger_path.read_text(encoding="utf-8")
        lines = content.strip().split("\n")
        self.assertEqual(len(lines), 1)
        
        entry = json.loads(lines[0])
        self.assertEqual(entry["ledger_tag"], "INSUFFICIENT_PRESSURE")
        self.assertEqual(entry["topic_id"], "topic_001_mock")
        
    def test_classification_logic(self):
        # Case: Reject
        entry_reject = {"operator_action": "REJECT", "engine_decision": "PASS"}
        res_reject = classify_judgment(entry_reject)
        self.assertEqual(res_reject["ledger_tag"], "HUMAN_CONFIDENCE_DROP")
        
        # Case: No Topic
        entry_no = {"operator_action": "HOLD", "engine_decision": "NO_TOPIC"}
        res_no = classify_judgment(entry_no)
        self.assertEqual(res_no["ledger_tag"], "NO_TOPIC_VALID_STATE")

    def test_append_behavior(self):
        # Run twice
        run_step98_judgment_ledger(base_dir=self.test_dir)
        run_step98_judgment_ledger(base_dir=self.test_dir)
        
        # Verify result path
        y, m, d = self.ymd.split("-")
        # Need to reconstruct path to verify append 
        # (Since run returns path of just written file, but we want to check content)
        ledger_path = self.ledger_dir / y / m / d / "judgment_ledger.jsonl"
        
        content = ledger_path.read_text(encoding="utf-8")
        lines = content.strip().split("\n")
        self.assertEqual(len(lines), 2)

if __name__ == "__main__":
    unittest.main()
