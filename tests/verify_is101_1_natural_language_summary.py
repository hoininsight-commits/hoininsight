import os
import json
import unittest
import shutil
from pathlib import Path
from src.ui.natural_language_summary import NaturalLanguageSummary

class TestNaturalLanguageSummary(unittest.TestCase):
    def setUp(self):
        self.base_dir = Path("temp_test_is101_1")
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        self.decision_dir = self.base_dir / "data" / "decision"
        self.ui_dir = self.base_dir / "data" / "ui"
        
        self.decision_dir.mkdir(parents=True, exist_ok=True)
        self.ui_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        if self.base_dir.exists():
            shutil.rmtree(self.base_dir)

    def test_summary_generation(self):
        # Mock inputs
        hero = {
            "status": "LOCKED",
            "hero_topic": {
                "topic_id": "T1",
                "sector": "SEMICONDUCTORS",
                "topic_type": "STRUCTURAL_SHIFT",
                "why_now_bundle": {
                    "why_now_1": "NVIDIA 실적 발표",
                    "why_now_2": "HBM 수요 폭증"
                }
            }
        }
        (self.decision_dir / "hero_topic_lock.json").write_text(json.dumps(hero))
        
        unit = {
            "interpretation_id": "T1",
            "target_sector": "SEMICONDUCTORS",
            "theme": "STRUCTURAL_SHIFT",
            "derived_metrics_snapshot": {
                "rigidity_score": 0.88,
                "supply_gap": 15.5
            }
        }
        (self.decision_dir / "interpretation_units.json").write_text(json.dumps([unit]))
        
        citations = {
            "T1": {
                "SEMIS": {"sources": ["Bloomberg"]}
            }
        }
        (self.decision_dir / "evidence_citations.json").write_text(json.dumps(citations))
        
        gen = NaturalLanguageSummary(self.base_dir)
        gen.run()
        
        out_path = self.ui_dir / "hero_summary.json"
        self.assertTrue(out_path.exists())
        
        data = json.loads(out_path.read_text(encoding='utf-8'))
        
        # KEY CHECK
        required_keys = ["headline", "one_liner", "status", "why_now", "core_logic", "numbers_with_evidence", "risk_note"]
        for k in required_keys:
            self.assertIn(k, data)
            self.assertTrue(data[k], f"Key {k} is empty")

        # STATUS CHECK
        self.assertEqual(data["status"], "READY")

        # NUMBERS CHECK (must have ( and ))
        for n in data["numbers_with_evidence"]:
            self.assertIn("(", n)
            self.assertIn(")", n)
            
        self.assertIn("반도체", data["headline"])

    def test_hypothesis_status(self):
        hero = {
            "status": "LOCKED",
            "hero_topic": {"topic_id": "T2", "topic_type": "HYPOTHESIS_JUMP"}
        }
        (self.decision_dir / "hero_topic_lock.json").write_text(json.dumps(hero))
        (self.decision_dir / "interpretation_units.json").write_text(json.dumps([{"interpretation_id": "T2"}]))
        
        gen = NaturalLanguageSummary(self.base_dir)
        gen.run()
        
        data = json.loads((self.ui_dir / "hero_summary.json").read_text())
        self.assertEqual(data["status"], "HYPOTHESIS")

if __name__ == "__main__":
    unittest.main()
