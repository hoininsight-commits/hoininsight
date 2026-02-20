import os
import json
import yaml
import unittest
import shutil
from pathlib import Path
from src.ui.schedule_risk_calendar import ScheduleRiskCalendar

class TestScheduleRiskCalendar(unittest.TestCase):
    def setUp(self):
        self.base_dir = Path("temp_test_is102")
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        self.registry_dir = self.base_dir / "registry" / "schedules"
        self.decision_dir = self.base_dir / "data" / "decision"
        self.ui_dir = self.base_dir / "data" / "ui"
        
        for d in [self.registry_dir, self.decision_dir, self.ui_dir]:
            d.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        if self.base_dir.exists():
            shutil.rmtree(self.base_dir)

    def test_calendar_generation(self):
        # Mock Registry
        registry_data = {
            "schedules": [
                {
                    "date": "2026-03-20",
                    "date_type": "FIXED",
                    "region": "US",
                    "category": "MACRO",
                    "title": "FOMC",
                    "risk_mechanism": "Rates",
                    "affected_axes": ["RATES"],
                    "base_weight": 0.9,
                    "tags": ["FED"]
                },
                {
                    "date": "2026-04-10",
                    "date_type": "ESTIMATE",
                    "region": "KR",
                    "category": "POLICY",
                    "title": "Support Plan",
                    "risk_mechanism": "Policy",
                    "affected_axes": ["EARNINGS"],
                    "base_weight": 0.7,
                    "tags": ["KR_POLICY"]
                }
            ]
        }
        (self.registry_dir / "schedule_registry_v1.yml").write_text(yaml.dump(registry_data))
        
        # Mock Hero (Optional match)
        hero_summary = {"headline": "FED 관련 뉴스"}
        (self.ui_dir / "hero_summary.json").write_text(json.dumps(hero_summary))
        
        gen = ScheduleRiskCalendar(self.base_dir)
        gen.run(today_str="2026-02-01")
        
        # Check files
        self.assertTrue((self.ui_dir / "schedule_risk_calendar_90d.json").exists())
        self.assertTrue((self.ui_dir / "schedule_risk_calendar_180d.json").exists())
        self.assertTrue((self.ui_dir / "upcoming_risk_topN.json").exists())
        
        # Check Sorting and Caps
        top_n = json.loads((self.ui_dir / "upcoming_risk_topN.json").read_text())
        self.assertEqual(len(top_n["items"]), 2)
        
        # FOMC should be rank 1 (base 0.9 + prox 0.2 + theme 0.2 + sens 0.2 = 1.5, but rounded)
        # Actually calculation: 0.9 (base) + 0.2 (dist 47d) + 0.2 (theme FED) + 0.2 (RATES) = 1.5
        self.assertEqual(top_n["items"][0]["title"], "FOMC")
        
        # ESTIMATE Cap Check
        est_item = next(i for i in json.loads((self.ui_dir / "schedule_risk_calendar_180d.json").read_text())["items"] if i["date_type"] == "ESTIMATE")
        self.assertLessEqual(est_item["final_score"], 0.6)
        
        # Date Format Check
        self.assertTrue(all(len(i["date"]) == 10 for i in top_n["items"]))

if __name__ == "__main__":
    unittest.main()
