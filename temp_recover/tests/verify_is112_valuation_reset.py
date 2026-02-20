import unittest
import json
import re
from pathlib import Path

class TestIS112ValuationReset(unittest.TestCase):
    def setUp(self):
        self.base_dir = Path(".")
        self.output_json = self.base_dir / "data" / "ui" / "valuation_reset_card.json"

    def test_output_exists(self):
        self.assertTrue(self.output_json.exists(), "valuation_reset_card.json이 생성되지 않았습니다.")

    def test_schema_keys(self):
        data = json.loads(self.output_json.read_text(encoding='utf-8'))
        required_keys = [
            "date", "valuation_state", "one_liner", "core_reason", 
            "numeric_checks", "operator_judgement", "risk_note", "guards"
        ]
        for key in required_keys:
            self.assertIn(key, data, f"필수 키 {key}가 누락되었습니다.")

    def test_valuation_state_enum(self):
        data = json.loads(self.output_json.read_text(encoding='utf-8'))
        allowed = ["RESET", "OVERPRICED", "EARLY", "UNCONFIRMED"]
        self.assertIn(data["valuation_state"], allowed, f"유효하지 않은 가치 판정 상태: {data['valuation_state']}")

    def test_numeric_checks_format(self):
        data = json.loads(self.output_json.read_text(encoding='utf-8'))
        self.assertGreaterEqual(len(data["numeric_checks"]), 1, "numeric_checks 항목은 최소 1개 이상이어야 합니다.")
        for n in data["numeric_checks"]:
            # Check for numbers
            self.assertTrue(re.search(r'\d', n), f"numeric_checks 항목에 수치가 포함되어 있지 않습니다: {n}")
            # Check for citations (brackets or parentheses)
            self.assertTrue(re.search(r'\(.*\)|\[.*\]', n), f"numeric_checks 항목에 출처가 누락되었습니다: {n}")

    def test_no_undefined(self):
        content = self.output_json.read_text(encoding='utf-8')
        self.assertNotIn("undefined", content.lower(), "산출물에 'undefined' 문자열이 포함되어 있습니다.")

if __name__ == "__main__":
    unittest.main()
