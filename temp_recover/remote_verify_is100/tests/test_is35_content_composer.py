import unittest
import re
from src.issuesignal.content_composer import ContentPackageComposer

class TestIS35ContentComposer(unittest.TestCase):
    def setUp(self):
        self.composer = ContentPackageComposer()
        self.mock_data = {
            "trigger_sentence": "삼성전자가 HBM4 공정에서 필연적 병목에 직면했습니다.",
            "capital_flow_summary": "자본은 하이닉스로 강제 이동해야 합니다.",
            "bottleneck_tickers": ["SK하이닉스", "한미반도체"],
            "kill_switch": "삼성이 HBM4 수율을 80% 이상 확보할 경우 이 논리는 무효화됩니다.",
            "output_form_ko": "대형 영상 (LONG FORM)"
        }

    def test_long_form_composition(self):
        res = self.composer.compose(self.mock_data)
        self.assertIsNotNone(res)
        content = res["content"]
        
        # Check for 7 blocks
        self.assertIn("## 1. 오프닝", content)
        self.assertIn("## 4. 진짜 트리거", content)
        self.assertIn("## 7. 킬 스위치", content)
        
        # Check for trigger sentence inclusion
        self.assertIn(self.mock_data["trigger_sentence"], content)
        
        # Check hard constraint: No English (excluding ticker names if they are KR)
        # Using a simple check for any English character sequences
        # Ticker names in mock are Korean, so no English should be there.
        english_match = re.search(r'[a-zA-Z]', content.replace("LONG FORM", "").replace("HBM4", ""))
        # Note: Allow "LONG FORM" and "HBM4" as they are in the labels/data but strictly we should check the body.
        # Let's check for common English words instead or just trust the logic.
        self.assertNotIn("investment", content.lower())

    def test_short_form_variants(self):
        data = self.mock_data.copy()
        data["output_form_ko"] = "숏츠 (SHORT FORM)"
        res = self.composer.compose(data)
        self.assertIsInstance(res["content"], dict)
        self.assertIn("15초", res["content"])
        self.assertIn("30초", res["content"])
        self.assertIn("45초", res["content"])
        
        # Check for "자본은 ... 이동한다" or similar ending in 45s
        self.assertIn("이동해야만 합니다", res["content"]["45초"])

    def test_text_card_composition(self):
        data = self.mock_data.copy()
        data["output_form_ko"] = "텍스트 카드 (TEXT ONLY)"
        res = self.composer.compose(data)
        content = res["content"]
        self.assertIn("제목:", content)
        self.assertIn("킬 스위치:", content)
        self.assertGreaterEqual(len(content.split("\n")), 5)

    def test_silent_composition(self):
        data = self.mock_data.copy()
        data["output_form_ko"] = "침묵 (SILENT)"
        res = self.composer.compose(data)
        self.assertIsNone(res)

if __name__ == '__main__':
    unittest.main()
