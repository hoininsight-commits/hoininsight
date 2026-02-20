import unittest
import json
import re
from pathlib import Path

class TestIS110ExpectationGap(unittest.TestCase):
    def setUp(self):
        self.base_dir = Path(".")
        self.output_json = self.base_dir / "data" / "ui" / "expectation_gap_card.json"

    def test_output_exists(self):
        self.assertTrue(self.output_json.exists())

    def test_schema_keys(self):
        data = json.loads(self.output_json.read_text(encoding='utf-8'))
        required_keys = ["date", "topic", "gap_type", "headline", "one_liner"]
        for key in required_keys:
            self.assertIn(key, data)

    def test_gap_type_enum(self):
        data = json.loads(self.output_json.read_text(encoding='utf-8'))
        allowed = ["EXPECTATION_SHOCK", "RELIEF_RALLY", "CONFIRMATION", "FUNDAMENTAL_DROP"]
        self.assertIn(data["gap_type"], allowed)

    def test_no_undefined(self):
        content = self.output_json.read_text(encoding='utf-8')
        self.assertNotIn("undefined", content.lower())

if __name__ == "__main__":
    unittest.main()
