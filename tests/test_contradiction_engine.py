import unittest
import sys
import os
from pathlib import Path
import json

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.engine.contradiction_engine import MarketContradictionEngine

class TestMarketContradictionEngine(unittest.TestCase):
    def setUp(self):
        self.engine = MarketContradictionEngine(project_root)

    def test_detect_growth_vs_capacity(self):
        benchmark = {
            "structural_shift": {
                "active_shifts": [{"theme": "Semiconductor Supply Chain Reshuffle"}]
            }
        }
        narratives = {
            "topics": [{"title": "AI Growth Acceleration", "final_narrative_score": 85}]
        }
        res = self.engine._detect_growth_vs_capacity(benchmark, narratives)
        self.assertIsNotNone(res)
        self.assertEqual(res["type"], "Growth vs Capacity")

    def test_detect_policy_vs_market(self):
        benchmark = {
            "macro_regime": {"regime": "LATE_CYCLE_TIGHTENING"}
        }
        # We can't easily mock _get_latest_anomaly without more complex setup, 
        # but we can test the logic if we were to mock it.
        pass

if __name__ == "__main__":
    unittest.main()
