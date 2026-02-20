import sys
import unittest
from pathlib import Path
from src.issuesignal.capital_rotation.engine import CapitalRotationEngine

class TestCapitalRotation(unittest.TestCase):
    def setUp(self):
        self.base_dir = Path(".")
        self.engine = CapitalRotationEngine(self.base_dir)
        self.ymd = "2026-01-31" # Use a fixed date for testing logic

    def test_state_build_structure(self):
        print("\n[TEST] Verifying MacroState Structure...")
        state = self.engine.build_macro_state(self.ymd)
        print(f"State: {state}")
        
        required_keys = ["rate_regime", "inflation_regime", "liquidity", "yield_curve", "risk_sentiment"]
        for k in required_keys:
            self.assertIn(k, state)
            
    def test_rules_loading(self):
        print("\n[TEST] Verifying Rules Loading...")
        from src.issuesignal.capital_rotation.rules import ROTATION_RULES
        self.assertGreater(len(ROTATION_RULES), 0)
        print(f"Loaded {len(ROTATION_RULES)} rules.")

    def test_verdict_structure(self):
        print("\n[TEST] Verifying Verdict Structure...")
        verdict = self.engine.get_rotation_verdict(self.ymd)
        print(f"Verdict: {verdict}")
        
        self.assertIn("triggered", verdict)
        self.assertIn("logic_ko", verdict)
        self.assertIn("target_sector", verdict)
        
        if verdict["triggered"]:
            print(f"[INFO] Rotation Triggered: {verdict['target_sector']}")
            self.assertIsNotNone(verdict["rule_id"])
        else:
            print("[INFO] No Rotation Triggered (Valid State)")
            self.assertIsNone(verdict["rule_id"])

if __name__ == "__main__":
    unittest.main()
