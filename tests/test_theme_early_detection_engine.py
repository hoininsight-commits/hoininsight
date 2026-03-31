import unittest
import sys
from pathlib import Path
import json

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.theme.theme_early_detection_engine import ThemeEarlyDetectionEngine

class TestThemeEarlyDetection(unittest.TestCase):
    def setUp(self):
        self.engine = ThemeEarlyDetectionEngine(project_root)

    def test_detection_logic(self):
        # We test the pattern matching logic
        pattern = {
            "name": "AI Power Constraint",
            "keywords": ["AI Capex", "Power Demand"]
        }
        res = self.engine._find_matches(pattern, {}, {})
        self.assertIn("AI capex growth", res)
        
    def test_scoring(self):
        score = self.engine._calculate_score([], {}, {}, {}, {})
        self.assertGreater(score, 0.4)
        self.assertLess(score, 1.0)

if __name__ == "__main__":
    unittest.main()
