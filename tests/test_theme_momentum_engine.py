import unittest
import sys
from pathlib import Path
import json

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.theme.theme_momentum_engine import NarrativeMomentumEngine

class TestThemeMomentum(unittest.TestCase):
    def setUp(self):
        self.engine = NarrativeMomentumEngine(project_root)

    def test_state_classification(self):
        self.assertEqual(self.engine._get_momentum_state(0.5), "ACCELERATING")
        self.assertEqual(self.engine._get_momentum_state(0.2), "BUILDING")
        self.assertEqual(self.engine._get_momentum_state(0.0), "STABLE")
        self.assertEqual(self.engine._get_momentum_state(-0.2), "COOLING")
        self.assertEqual(self.engine._get_momentum_state(-0.5), "COLLAPSING")

    def test_analysis_run(self):
        # Create mock input if missing
        test_evo = {"theme": "AI Power Constraint", "stage": "EXPANSION", "narrative_spread": 0.5, "capital_flow_confirmation": 0.5}
        test_path = self.engine.evolution_state_path
        test_path.parent.mkdir(parents=True, exist_ok=True)
        with open(test_path, "w", encoding="utf-8") as f:
            json.dump(test_evo, f)
            
        res = self.engine.run_momentum_analysis()
        self.assertIsNotNone(res)
        self.assertIn(res["momentum_state"], ["ACCELERATING", "BUILDING", "STABLE", "COOLING", "COLLAPSING"])

if __name__ == "__main__":
    unittest.main()
