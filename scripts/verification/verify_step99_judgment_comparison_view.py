import shutil
import tempfile
import json
import unittest
from pathlib import Path
from datetime import datetime

from src.ops.judgment_comparison_view import run_step99_judgment_comparison_view

class TestStep99(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.data_dir = self.test_dir / "data"
        self.logs_dir = self.data_dir / "judgment_logs"
        self.ledger_dir = self.data_dir / "judgment_ledger"
        self.decision_dir = self.data_dir / "decision"
        
        self.ymd = datetime.now().strftime("%Y-%m-%d")
        y, m, d = self.ymd.split("-")
        
        # Create Dirs
        (self.logs_dir / y / m / d).mkdir(parents=True, exist_ok=True)
        (self.ledger_dir / y / m / d).mkdir(parents=True, exist_ok=True)
        (self.decision_dir / y / m / d).mkdir(parents=True, exist_ok=True)
        
        # Verify Paths
        self.log_file = self.logs_dir / y / m / d / "operator_judgment_log.jsonl"
        self.ledger_file = self.ledger_dir / y / m / d / "judgment_ledger.jsonl"
        self.card_file = self.decision_dir / y / m / d / "final_decision_card.json"

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_alignment_no_topic(self):
        # Case: Engine NO_TOPIC, Human HOLD -> ALIGNED
        
        # Mock Inputs
        op_entry = {"engine_decision": "NO_TOPIC", "operator_action": "HOLD", "topic_id": "NO_TOPIC"}
        ledger_entry = {"ledger_tag": "NO_TOPIC_VALID_STATE", "ledger_reason": "Correct state"}
        card = {"topic_id": None}
        
        self.log_file.write_text(json.dumps(op_entry), encoding="utf-8")
        self.ledger_file.write_text(json.dumps(ledger_entry), encoding="utf-8")
        self.card_file.write_text(json.dumps(card), encoding="utf-8")
        
        # Run
        res = run_step99_judgment_comparison_view(base_dir=self.test_dir)
        view = res["view"]
        
        self.assertEqual(view["delta_interpretation"]["alignment_status"], "ALIGNED")
        self.assertEqual(view["delta_interpretation"]["divergence_type"], "NO_TOPIC_ALIGNMENT")

    def test_divergence_confidence_gap(self):
        # Case: Engine LOCK, Human REJECT -> CONFIDENCE_GAP
        
        op_entry = {"engine_decision": "LOCK", "operator_action": "REJECT", "topic_id": "t1"}
        ledger_entry = {"ledger_tag": "HUMAN_CONFIDENCE_DROP", "ledger_reason": "Too risky"}
        card = {"topic_id": "t1", "structural_basis": ["s1"]}
        
        self.log_file.write_text(json.dumps(op_entry), encoding="utf-8")
        self.ledger_file.write_text(json.dumps(ledger_entry), encoding="utf-8")
        self.card_file.write_text(json.dumps(card), encoding="utf-8")
        
        res = run_step99_judgment_comparison_view(base_dir=self.test_dir)
        view = res["view"]
        
        self.assertEqual(view["delta_interpretation"]["alignment_status"], "DIVERGED")
        self.assertEqual(view["delta_interpretation"]["divergence_type"], "CONFIDENCE_GAP")
        self.assertTrue("Engine locked but Human REJECT" in view["delta_interpretation"]["divergence_reason"])

if __name__ == "__main__":
    unittest.main()
