import unittest
import json
import re
from pathlib import Path
from src.ui.relationship_stress_generator import RelationshipStressGenerator

class TestIS106RelationshipStress(unittest.TestCase):
    def setUp(self):
        self.base_dir = Path(".")
        self.output_path = self.base_dir / "data" / "ui" / "relationship_stress_card.json"
        self.export_dir = self.base_dir / "exports"
        
        # Run generator
        gen = RelationshipStressGenerator(self.base_dir)
        gen.run()

    def test_output_exists(self):
        # Even if data is missing, we check if it was generated with the available data (NVIDIA vs OpenAI in logic)
        self.assertTrue(self.output_path.exists())

    def test_strict_schema(self):
        data = json.loads(self.output_path.read_text(encoding='utf-8'))
        required_keys = [
            "date", "status", "headline", "hook", "pair",
            "what_changed", "why_now", "cascade", "numbers_with_evidence", "risk_note"
        ]
        for key in required_keys:
            self.assertIn(key, data)
            self.assertTrue(data[key], f"Key {key} should not be empty")
        
        # Pair schema
        self.assertIn("a", data["pair"])
        self.assertIn("b", data["pair"])
        self.assertIn("a_kr", data["pair"])
        self.assertIn("b_kr", data["pair"])

    def test_numbers_with_evidence(self):
        data = json.loads(self.output_path.read_text(encoding='utf-8'))
        for entry in data["numbers_with_evidence"]:
            self.assertTrue(re.search(r'\d', entry), f"Entry '{entry}' must contain a number")
            self.assertIn("(", entry, f"Entry '{entry}' must contain a citation in parentheses")
            self.assertIn(")", entry, f"Entry '{entry}' must contain a citation in parentheses")

    def test_no_undefined_literals(self):
        content = self.output_path.read_text(encoding='utf-8')
        self.assertNotIn("undefined", content.lower())
        self.assertNotIn("null", content.lower())

    def test_status_enum(self):
        data = json.loads(self.output_path.read_text(encoding='utf-8'))
        self.assertIn(data["status"], ["READY", "HOLD", "HYPOTHESIS"])

    def test_risk_note_present(self):
        data = json.loads(self.output_path.read_text(encoding='utf-8'))
        self.assertTrue(len(data["risk_note"]) > 5)

if __name__ == "__main__":
    unittest.main()
