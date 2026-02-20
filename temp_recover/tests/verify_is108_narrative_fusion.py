import unittest
import json
import re
from pathlib import Path
from src.ui.narrative_fusion_engine import NarrativeFusionEngine

class TestIS108NarrativeFusion(unittest.TestCase):
    def setUp(self):
        self.base_dir = Path(".")
        self.output_json = self.base_dir / "data" / "ui" / "daily_narrative_fusion.json"
        self.output_long = self.base_dir / "exports" / "daily_long_script.txt"
        self.output_shorts = self.base_dir / "exports" / "daily_shorts_scripts.json"
        
        # 엔진 실행
        engine = NarrativeFusionEngine(self.base_dir)
        engine.run()

    def test_outputs_exist(self):
        self.assertTrue(self.output_json.exists(), "daily_narrative_fusion.json이 생성되지 않았습니다.")
        self.assertTrue(self.output_long.exists(), "daily_long_script.txt가 생성되지 않았습니다.")
        self.assertTrue(self.output_shorts.exists(), "daily_shorts_scripts.json이 생성되지 않았습니다.")

    def test_json_schema(self):
        data = json.loads(self.output_json.read_text(encoding='utf-8'))
        self.assertIn("main_theme", data)
        self.assertIn("long_topic", data)
        self.assertIn("short_topics", data)
        self.assertIn("fusion_rule", data)
        
        # LONG 제약 조건: 반드시 1개
        self.assertTrue(len(data["long_topic"]["title"]) > 0)
        # SHORT 제약 조건: 1개 이상
        self.assertTrue(len(data["short_topics"]) >= 1)

    def test_numbers_with_citations(self):
        data = json.loads(self.output_json.read_text(encoding='utf-8'))
        # Long 토픽 숫자 검사
        for n in data["long_topic"]["numbers"]:
            self.assertTrue(re.search(r'\d', n), f"숫자가 포함되지 않았습니다: {n}")
            self.assertTrue(re.search(r'\(.*\)', n), f"출처(괄호)가 포함되지 않았습니다: {n}")

        # Short 토픽 숫자 검사
        for s in data["short_topics"]:
            kn = s["key_number"]
            # 내부 데이터인 경우 예외 허용 가능하나 기본적으로 숫자+출처 지향
            if "확인 중" not in kn:
                self.assertTrue(re.search(r'\d', kn), f"숫자가 포함되지 않았습니다: {kn}")
                self.assertTrue(re.search(r'\(.*\)', kn), f"출처(괄호)가 포함되지 않았습니다: {kn}")

    def test_korean_only_enforcement(self):
        # 텍스트 스크립트에서 영어 문장(단어 말고 문장 수준)이 있는지 간접 확인
        # 한글 글자 비율이 일정 이상(예: 50%)이어야 함
        content = self.output_long.read_text(encoding='utf-8')
        hangul_chars = re.findall(r'[가-힣]', content)
        english_chars = re.findall(r'[a-zA-Z]', content)
        
        self.assertTrue(len(hangul_chars) > len(english_chars), "한글보다 영어 비율이 높습니다. 한국어 전용 가드 위반 가능성.")

    def test_long_script_structure(self):
        content = self.output_long.read_text(encoding='utf-8')
        required_headers = [
            "1. 오프닝 훅",
            "2. 오늘의 핵심 질문",
            "3. 구조적 변화 설명",
            "4. 숫자로 증명",
            "5. 반대 시나리오",
            "6. 정리 멘트"
        ]
        for header in required_headers:
            self.assertIn(header, content, f"필수 섹션이 누락되었습니다: {header}")

if __name__ == "__main__":
    unittest.main()
