import unittest
import sys
from pathlib import Path
import json

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.theme.theme_narrative_engine import ThemeNarrativeEngine

class TestThemeNarrative(unittest.TestCase):
    def setUp(self):
        self.engine = ThemeNarrativeEngine(project_root)

    def test_narrative_expansion(self):
        # We test expansion for AI Power Constraint
        # First ensure top_early_theme exists for testing
        test_theme = {
            "theme": "AI Power Constraint",
            "score": 0.8,
            "stage": "PRE-STORY",
            "potential_sectors": ["Utilities", "Energy"],
            "signals": ["AI Capex", "Power Grid"]
        }
        test_path = self.engine.early_theme_path
        test_path.parent.mkdir(parents=True, exist_ok=True)
        with open(test_path, "w", encoding="utf-8") as f:
            json.dump(test_theme, f)
            
        res = self.engine.run_narrative_expansion()
        self.assertIsNotNone(res)
        self.assertEqual(res["theme"], "AI Power Constraint")
        self.assertIn("전력", res["explanation"])
        self.assertIn("Utilities", res["sector_impact"])

if __name__ == "__main__":
    unittest.main()
