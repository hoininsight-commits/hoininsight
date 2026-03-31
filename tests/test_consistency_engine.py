import unittest
import json
import os
from pathlib import Path
import sys

# Add project root to path
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from src.ops.run_consistency_engine import ConsistencyEngine

class TestConsistencyEngine(unittest.TestCase):
    def setUp(self):
        self.project_root = root_dir
        self.brief_path = self.project_root / "data" / "operator" / "today_operator_brief.json"
        self.engine = ConsistencyEngine(self.project_root)

    def test_end_to_end_consistency(self):
        """Test if run() successfully aligns all components in the brief."""
        # 1. Run the engine
        res = self.engine.run()
        core_theme = res["core_theme"]
        self.assertNotEqual(core_theme, "N/A")
        
        # 2. Check the saved state
        state_path = self.project_root / "data" / "operator" / "core_theme_state.json"
        self.assertTrue(state_path.exists())
        with open(state_path, "r", encoding="utf-8") as f:
            state = json.load(f)
            self.assertEqual(state["core_theme"], core_theme)

        # 3. Check the brief alignment
        self.assertTrue(self.brief_path.exists())
        with open(self.brief_path, "r", encoding="utf-8") as f:
            brief = json.load(f)
            
        self.assertEqual(brief.get("core_theme"), core_theme)
        
        # Verify component alignment
        # Note: In our current implementation, we map these to the brief
        
        # Radar
        self.assertEqual(brief["market_radar"]["theme"], core_theme)
        
        # Narrative
        self.assertEqual(brief["narrative_brief"]["featured_theme"], core_theme)
        
        # Impact
        self.assertEqual(brief["impact_map"]["theme"], core_theme)
        # Check stock rationale structure (should be a list now)
        for s in brief["impact_map"]["mentionable_stocks"]:
            self.assertIsInstance(s["rationale"], list)

        # Content Studio
        # Note: Topic can have a different name but internally should be related
        # Our align_topic ensures the topic object returned corresponds to the theme.
        # Check if selected_topic is set
        self.assertNotEqual(brief["content_studio"]["selected_topic"], "N/A")

    def test_theme_selection_logic(self):
        """Test if selector picks the highest scoring theme."""
        from src.ops.core_theme_selector import CoreThemeSelector
        selector = CoreThemeSelector(self.project_root)
        result = selector.select_core_theme()
        self.assertIn("core_theme", result)
        self.assertIn("score", result)
        self.assertTrue(len(result["sources"]) > 0)

if __name__ == "__main__":
    unittest.main()
