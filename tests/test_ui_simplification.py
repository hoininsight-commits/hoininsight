import unittest
import json
import os
from pathlib import Path
from src.ops.build_operator_brief import OperatorBriefBuilder

class TestUISimplification(unittest.TestCase):
    def setUp(self):
        self.project_root = Path(__file__).parent.parent
        self.builder = OperatorBriefBuilder(self.project_root)
        self.output_file = self.project_root / "data" / "operator" / "today_operator_brief.json"

    def test_brief_generation(self):
        """Test if today_operator_brief.json is generated correctly."""
        brief = self.builder.build()
        self.assertTrue(self.output_file.exists())
        
        # Verify structure
        self.assertIn("market_radar", brief)
        self.assertIn("narrative_brief", brief)
        self.assertIn("impact_map", brief)
        self.assertIn("content_studio", brief)
        
    def test_impact_map_mapping(self):
        """Test if impact map mapping handles mentionables correctly (no undefined)."""
        brief = self.builder.build()
        impact_map = brief.get("impact_map", {})
        stocks = impact_map.get("mentionable_stocks", [])
        
        if stocks:
            stock = stocks[0]
            self.assertIn("ticker", stock)
            self.assertIn("name", stock)
            self.assertIn("relevance_score", stock)
            self.assertIn("rationale", stock)
            self.assertNotEqual(stock["ticker"], "undefined")

    def test_routing_files_exist(self):
        """Test if all new UI components exist."""
        ui_path = self.project_root / "docs" / "ui"
        self.assertTrue((ui_path / "operator_market_radar.js").exists())
        self.assertTrue((ui_path / "operator_narrative_brief.js").exists())
        self.assertTrue((ui_path / "operator_impact_map.js").exists())
        self.assertTrue((ui_path / "operator_content_studio.js").exists())

if __name__ == "__main__":
    unittest.main()
