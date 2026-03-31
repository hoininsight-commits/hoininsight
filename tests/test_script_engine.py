import unittest
import sys
from pathlib import Path
import json

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.content.script_engine import TodayScriptEngine

class TestScriptEngine(unittest.TestCase):
    def setUp(self):
        self.engine = TodayScriptEngine(project_root)

    def test_script_synthesis(self):
        # Create temporary mock files
        story_mock = {
            "title": "Quantum Leap in AI",
            "featured_theme": "AI Evolution",
            "summary": "The gap between software and hardware is narrowing.",
            "impact_sectors": ["Computing", "AI Software"]
        }
        with open(self.engine.story_path, 'w', encoding='utf-8') as f:
            json.dump(story_mock, f)
            
        res = self.engine.run_synthesis()
        self.assertIsNotNone(res)
        self.assertIn("Quantum Leap", res["hook"])
        self.assertIn("Computing", res["full_script"])

if __name__ == "__main__":
    unittest.main()
