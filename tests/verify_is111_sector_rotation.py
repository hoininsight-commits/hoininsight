import unittest
import json
from pathlib import Path

class TestIS111SectorRotation(unittest.TestCase):
    def setUp(self):
        self.base_dir = Path(".")
        self.output_json = self.base_dir / "data" / "ui" / "sector_rotation_acceleration.json"

    def test_output_exists(self):
        self.assertTrue(self.output_json.exists(), "sector_rotation_acceleration.json이 생성되지 않았습니다.")

    def test_schema_keys(self):
        data = json.loads(self.output_json.read_text(encoding='utf-8'))
        required_keys = [
            "date", "from_sector", "to_sector", "acceleration", 
            "confidence", "evidence", "operator_sentence", "risk_note"
        ]
        for key in required_keys:
            self.assertIn(key, data, f"필수 키 {key}가 누락되었습니다.")

    def test_acceleration_enum(self):
        data = json.loads(self.output_json.read_text(encoding='utf-8'))
        allowed = ["ACCELERATING", "ROTATING", "NONE"]
        self.assertIn(data["acceleration"], allowed, f"유효하지 않은 가속도 유형: {data['acceleration']}")

    def test_evidence_format(self):
        data = json.loads(self.output_json.read_text(encoding='utf-8'))
        self.assertGreaterEqual(len(data["evidence"]), 2, "evidence 항목은 최소 2개 이상이어야 합니다.")
        for e in data["evidence"]:
            self.assertTrue("(" in e or "[" in e, f"출처가 누락된 근거: {e}")

    def test_no_undefined(self):
        content = self.output_json.read_text(encoding='utf-8')
        self.assertNotIn("undefined", content.lower(), "산출물에 'undefined' 문자열이 포함되어 있습니다.")

if __name__ == "__main__":
    unittest.main()
