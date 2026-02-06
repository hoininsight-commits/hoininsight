import unittest
import json
from pathlib import Path

class TestIS111SectorRotation(unittest.TestCase):
    def setUp(self):
        self.base_dir = Path(".")
        self.output_json = self.base_dir / "data" / "ui" / "sector_rotation_acceleration.json"
        self.long_script = self.base_dir / "exports" / "sector_rotation_long.txt"
        self.shorts_script = self.base_dir / "exports" / "sector_rotation_shorts.txt"

    def test_output_exists(self):
        self.assertTrue(self.output_json.exists(), "JSON 출력 파일이 존재하지 않습니다.")

    def test_schema_validity(self):
        data = json.loads(self.output_json.read_text(encoding='utf-8'))
        required_keys = ["date", "from_sector", "to_sector", "acceleration", "confidence", "evidence", "operator_sentence"]
        for key in required_keys:
            self.assertIn(key, data, f"키 누락: {key}")
        
        self.assertIn(data["acceleration"], ["ACCELERATING", "ROTATING", "NONE"])
        self.assertIn(data["confidence"], ["HIGH", "MEDIUM", "LOW"])

    def test_evidence_citations(self):
        data = json.loads(self.output_json.read_text(encoding='utf-8'))
        self.assertGreaterEqual(len(data["evidence"]), 1)
        for ev in data["evidence"]:
            # 출처 (괄호) 포함 확인
            self.assertTrue("(" in ev and ")" in ev, f"출처 미표기 근거 발견: {ev}")

    def test_no_undefined(self):
        content = self.output_json.read_text(encoding='utf-8')
        self.assertNotIn("undefined", content.lower())
        
        if self.long_script.exists():
            self.assertNotIn("undefined", self.long_script.read_text(encoding='utf-8').lower())

    def test_scripts_exist(self):
        self.assertTrue(self.long_script.exists(), "롱폼 대본이 생성되지 않았습니다.")
        self.assertTrue(self.shorts_script.exists(), "쇼츠 대본이 생성되지 않았습니다.")

if __name__ == "__main__":
    unittest.main()
