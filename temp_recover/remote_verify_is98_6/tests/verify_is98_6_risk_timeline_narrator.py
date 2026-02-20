import os
import json
import unittest
import shutil
from pathlib import Path
from src.ui.risk_timeline_narrator import RiskTimelineNarrator

class TestRiskTimelineNarrator(unittest.TestCase):
    def setUp(self):
        self.base_dir = Path("temp_test_is98_6")
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        self.ui_dir = self.base_dir / "data" / "ui"
        self.exports_dir = self.base_dir / "exports"
        
        self.ui_dir.mkdir(parents=True, exist_ok=True)
        self.exports_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        if self.base_dir.exists():
            shutil.rmtree(self.base_dir)

    def test_script_generation(self):
        # Mock inputs from IS-102
        top_n = {
            "as_of": "2026-02-01",
            "top_n": 7,
            "items": [
                {"rank": 1, "date": "2026-02-15", "title": "Near Risk", "one_liner": "Short pressure", "final_score": 0.9},
                {"rank": 2, "date": "2026-04-10", "title": "Mid Risk", "one_liner": "Mid pressure", "final_score": 0.7},
                {"rank": 3, "date": "2026-08-20", "title": "Long Risk", "one_liner": "Long direction", "final_score": 0.8}
            ]
        }
        (self.ui_dir / "upcoming_risk_topN.json").write_text(json.dumps(top_n))
        
        gen = RiskTimelineNarrator(self.base_dir)
        gen.run()
        
        # 1. File existence
        self.assertTrue((self.exports_dir / "risk_timeline_script_long.txt").exists())
        self.assertTrue((self.exports_dir / "risk_timeline_script_shorts.txt").exists())
        self.assertTrue((self.ui_dir / "risk_timeline_narrative.json").exists())
        
        # 2. Structure check
        long_text = (self.exports_dir / "risk_timeline_script_long.txt").read_text()
        self.assertIn("[PHASE 1", long_text)
        self.assertIn("[PHASE 2", long_text)
        self.assertIn("[PHASE 3", long_text)
        self.assertIn("Near Risk", long_text)
        self.assertIn("Mid Risk", long_text)
        self.assertIn("Long Risk", long_text)
        
        # 3. Toxicity/Panic check
        banned = ["폭락 확정", "무조건 무너진다", "전부 파세요"]
        for word in banned:
            self.assertNotIn(word, long_text)
            
        # 4. Shorts count check
        shorts_text = (self.exports_dir / "risk_timeline_script_shorts.txt").read_text()
        shorts_blocks = [s for s in shorts_text.split("---") if s.strip()]
        self.assertEqual(len(shorts_blocks), 3)
        
        # 5. Narrative data check
        narrative = json.loads((self.ui_dir / "risk_timeline_narrative.json").read_text())
        self.assertEqual(len(narrative["phases"]), 3)
        self.assertEqual(narrative["phases"][0]["phase"], 1)
        self.assertEqual(narrative["phases"][1]["phase"], 2)
        self.assertEqual(narrative["phases"][2]["phase"], 3)

if __name__ == "__main__":
    unittest.main()
