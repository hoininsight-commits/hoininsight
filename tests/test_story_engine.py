import unittest
import sys
import os
from pathlib import Path
import json

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.engine.story_engine import MarketStoryEngine

class TestMarketStoryEngine(unittest.TestCase):
    def setUp(self):
        self.engine = MarketStoryEngine(project_root)

    def test_narrative_generation(self):
        market_state = "Bullish"
        top_contra = {
            "name": "Yield Divergence",
            "reason": "Yields rising despite inflation cooling.",
            "affected_sectors": ["Fixed Income", "Tech"]
        }
        featured_theme = {
            "title": "Quantum Computing Leap",
            "one_line_summary": "Quantum tech breaks encryption standards."
        }
        capital_flow = {
            "top_capital_flow_theme": {
                "theme": "Deep Tech Inflow",
                "impact_direction": "POSITIVE",
                "primary_sector": "Technology"
            }
        }
        
        story = self.engine._generate_narrative(market_state, top_contra, featured_theme, capital_flow)
        
        self.assertIn("Yield Divergence", story["title"])
        self.assertIn("Yields rising", story["summary"])
        self.assertEqual(story["featured_theme"], "Quantum Computing Leap")
        self.assertIn("Technology", story["impact_sectors"])

if __name__ == "__main__":
    unittest.main()
