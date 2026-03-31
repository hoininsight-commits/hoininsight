import unittest
import json
import os
from pathlib import Path
from src.ops.execution_tracker import ExecutionTracker
from src.ops.performance_evaluator import PerformanceEvaluator
from src.ops.risk_engine import RiskEngine

class TestExecutionAndRisk(unittest.TestCase):
    def setUp(self):
        self.project_root = Path(__file__).resolve().parent.parent
        self.log_path = self.project_root / "data" / "operator" / "execution_log.json"
        self.report_path = self.project_root / "data" / "operator" / "performance_report.json"
        self.risk_path = self.project_root / "data" / "operator" / "risk_state.json"

    def test_01_execution_tracking(self):
        tracker = ExecutionTracker(self.project_root)
        tracker.track_execution()
        
        self.assertTrue(self.log_path.exists())
        with open(self.log_path, "r", encoding="utf-8") as f:
            log = json.load(f)
        
        self.assertIsInstance(log, list)
        if len(log) > 0:
            entry = log[0]
            self.assertIn("date", entry)
            self.assertIn("theme", entry)
            self.assertIn("stock", entry)
            self.assertIn("entry_price", entry)

    def test_02_performance_evaluation(self):
        evaluator = PerformanceEvaluator(self.project_root)
        results = evaluator.evaluate_performance()
        
        self.assertTrue(self.report_path.exists())
        self.assertIsInstance(results, list)
        
        if len(results) > 0:
            item = results[0]
            self.assertIn("pnl", item)
            self.assertIn("status", item)
            self.assertTrue(item["status"] in ["WIN", "LOSS"])

    def test_03_risk_engine(self):
        engine = RiskEngine(self.project_root)
        risk = engine.build_risk()
        
        self.assertTrue(self.risk_path.exists())
        self.assertIsNotNone(risk)
        self.assertIn("risk_score", risk)
        self.assertIn("risk_level", risk)
        self.assertIn("invalidation", risk)
        
        self.assertTrue(0.0 <= risk["risk_score"] <= 1.0)
        self.assertIn(risk["risk_level"], ["LOW", "MEDIUM", "HIGH"])

if __name__ == "__main__":
    unittest.main()
