import unittest
import sys
from pathlib import Path
import json

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.impact.mentionables_engine import MentionablesEngine

class TestMentionablesEngine(unittest.TestCase):
    def setUp(self):
        self.engine = MentionablesEngine(project_root)

    def test_sector_detection(self):
        story = {
            "title": "AI Infrastructure Surge",
            "summary": "HBM memory demand is skyrocketing due to AI data centers.",
            "impact_sectors": ["Technology"]
        }
        sectors = self.engine._detect_sectors(story)
        self.assertIn("HBM Memory", sectors)
        self.assertIn("AI Software", sectors)
        self.assertIn("Technology", sectors)

    def test_scoring(self):
        stock = "SKHynix"
        sector = "HBM Memory"
        story = {"impact_sectors": ["HBM Memory"], "featured_theme": "HBM Expansion"}
        benchmark = {"risk_state": "ON"}
        flow = {"top_capital_flow_theme": {"impact_direction": "POSITIVE"}}
        
        score = self.engine._calculate_score(stock, sector, story, benchmark, flow)
        # 0.5 * 100 + 0.3 * 90 + 0.2 * 90 = 50 + 27 + 18 = 95
        self.assertEqual(score, 95.0)

if __name__ == "__main__":
    unittest.main()
