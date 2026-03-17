import unittest
import sys
from pathlib import Path
import json

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.theme.theme_evolution_engine import ThemeEvolutionEngine

class TestThemeEvolution(unittest.TestCase):
    def setUp(self):
        self.engine = ThemeEvolutionEngine(project_root)

    def test_stage_classification(self):
        self.assertEqual(self.engine._get_stage(0.1), "PRE-STORY")
        self.assertEqual(self.engine._get_stage(0.35), "EMERGING")
        self.assertEqual(self.engine._get_stage(0.55), "EXPANSION")
        self.assertEqual(self.engine._get_stage(0.75), "MAINSTREAM")
        self.assertEqual(self.engine._get_stage(0.95), "EXHAUSTION")

    def test_analysis_run(self):
        # Create mock input if missing
        test_theme = {"theme": "AI Power Constraint", "score": 0.8, "signals": ["S1", "S2"]}
        test_path = self.engine.early_theme_path
        test_path.parent.mkdir(parents=True, exist_ok=True)
        with open(test_path, "w", encoding="utf-8") as f:
            json.dump(test_theme, f)
            
        res = self.engine.run_evolution_analysis()
        self.assertIsNotNone(res)
        self.assertIn(res["stage"], ["EMERGING", "EXPANSION", "MAINSTREAM", "PRE-STORY", "EXHAUSTION"])

if __name__ == "__main__":
    unittest.main()
