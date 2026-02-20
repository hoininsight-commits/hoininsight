import unittest
from src.issuesignal.voice_lock import VoiceLockEngine

class TestIS39VoiceLock(unittest.TestCase):
    def setUp(self):
        self.engine = VoiceLockEngine()

    def test_certainty_mapping(self):
        text = "이는 가능성이 있다. 앞으로 전망된다."
        res = self.engine.apply_lock(text)
        self.assertIn("이미 결정됐다", res["locked_content"])
        self.assertIn("분석 결과는 하나다", res["locked_content"])

    def test_rhythm_shorten(self):
        # Test long sentence with question
        text = "이 부분이 중요한 이유는 무엇인가요? 지수 흐름 때문에 섹터 흐름이 분리됩니다."
        res = self.engine.apply_lock(text)
        self.assertIn(".", res["locked_content"])
        self.assertNotIn("?", res["locked_content"])
        self.assertNotIn("때문에", res["locked_content"])
        self.assertIn("이유는", res["locked_content"])

    def test_structural_validation(self):
        valid_text = "## 1. 정의\n## 2. 표면 해석\n## 3. 시장의 오해\n## 4. 구조적 강제\n## 5. 결론"
        invalid_text = "정의가 빠진 글입니다."
        
        res_v = self.engine.apply_lock(valid_text)
        res_iv = self.engine.apply_lock(invalid_text)
        
        self.assertTrue(res_v["voice_consistent"])
        self.assertFalse(res_iv["voice_consistent"])

if __name__ == '__main__':
    unittest.main()
