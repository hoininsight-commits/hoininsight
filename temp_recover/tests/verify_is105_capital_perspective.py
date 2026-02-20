import unittest
import json
import os
from pathlib import Path
from src.ui.capital_perspective_narrator import CapitalPerspectiveNarrator

class TestIS105CapitalPerspective(unittest.TestCase):
    def setUp(self):
        self.base_dir = Path(".")
        self.output_path = self.base_dir / "data" / "ui" / "capital_perspective.json"
        self.export_dir = self.base_dir / "exports"
        
        # Run narrator
        narrator = CapitalPerspectiveNarrator(self.base_dir)
        narrator.run()

    def test_output_exists(self):
        self.assertTrue(self.output_path.exists())

    def test_strict_schema(self):
        data = json.loads(self.output_path.read_text(encoding='utf-8'))
        required_keys = [
            "headline", "core_statement", "capital_flow",
            "internal_shift", "why_now_capital", "risk_note"
        ]
        for key in required_keys:
            self.assertIn(key, data)
            self.assertTrue(data[key], f"Key {key} should not be empty")

    def test_capital_flow_has_numbers_and_citations(self):
        data = json.loads(self.output_path.read_text(encoding='utf-8'))
        for entry in data["capital_flow"]:
            # Check for numbers or decimal points or specific keywords that imply data
            self.assertTrue(any(c.isdigit() for c in entry) or "(" in entry, f"Entry '{entry}' must contain numbers and/or citations in parentheses")

    def test_no_undefined_literals(self):
        content = self.output_path.read_text(encoding='utf-8')
        self.assertNotIn("undefined", content.lower())
        self.assertNotIn("null", content.lower())

    def test_exports_generated(self):
        scripts = [
            "final_script_capital_shorts_1.txt",
            "final_script_capital_shorts_2.txt",
            "final_script_capital_shorts_3.txt",
            "final_script_capital_long.txt"
        ]
        for s in scripts:
            self.assertTrue((self.export_dir / s).exists())

if __name__ == "__main__":
    unittest.main()
