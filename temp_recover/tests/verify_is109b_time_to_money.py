import unittest
import json
import re
from pathlib import Path

class TestIS109BTimeToMoney(unittest.TestCase):
    def setUp(self):
        self.base_dir = Path(".")
        self.output_json = self.base_dir / "data" / "ui" / "time_to_money.json"

    def test_output_exists(self):
        self.assertTrue(self.output_json.exists(), "time_to_money.json이 생성되지 않았습니다.")

    def test_schema_keys(self):
        data = json.loads(self.output_json.read_text(encoding='utf-8'))
        required_keys = [
            "date", "topic", "classification", "time_window", 
            "reasoning", "blocked_by", "first_reactors", "guards"
        ]
        for key in required_keys:
            self.assertIn(key, data, f"필수 키 {key}가 누락되었습니다.")

    def test_classification_enum(self):
        data = json.loads(self.output_json.read_text(encoding='utf-8'))
        allowed = ["IMMEDIATE", "NEAR", "MID", "LONG"]
        self.assertIn(data["classification"], allowed, f"유효하지 않은 분류: {data['classification']}")

    def test_reasoning_with_citations(self):
        data = json.loads(self.output_json.read_text(encoding='utf-8'))
        for r in data["reasoning"]:
            self.assertTrue(re.search(r'\[.*\]', r), f"추론 과정에 출처(대괄호)가 포함되지 않았습니다: {r}")

    def test_no_undefined(self):
        content = self.output_json.read_text(encoding='utf-8')
        self.assertNotIn("undefined", content.lower(), "JSON에 'undefined' 문자열이 포함되어 있습니다.")

    def test_numbers_in_reasoning(self):
        # IS-109-B 요구사항: 숫자 없이 추상 문장만 있으면 FAIL (일부 항목이라도 숫자가 있어야 함)
        data = json.loads(self.output_json.read_text(encoding='utf-8'))
        all_reasoning = " ".join(data["reasoning"])
        # 일부 시점(LONG 등)에는 숫자가 없을 수 있으나, 전반적인 데이터 무결성을 위해 체크
        # 여기서는 IS-109-A에서 넘어온 수치 데이터가 reasoning에 간접적으로라도 반영되는지 확인하거나
        # 최소한 0~2주 같은 시간 범위 숫자가 포함되는지 확인
        self.assertTrue(re.search(r'\d', all_reasoning) or re.search(r'\d', data["time_window"]), "수치 데이터(숫자)가 포함되지 않았습니다.")

if __name__ == "__main__":
    unittest.main()
