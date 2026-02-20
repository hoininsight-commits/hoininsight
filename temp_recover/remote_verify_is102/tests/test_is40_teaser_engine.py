import unittest
from src.issuesignal.teaser_engine import NextSignalTeaserEngine

class TestIS40TeaserEngine(unittest.TestCase):
    def setUp(self):
        self.engine = NextSignalTeaserEngine()

    def test_teaser_generation(self):
        membership_queue = [
            {
                "title": "금리 정책 결정",
                "expected_timing": "이번 주 (2~3일 내)",
                "status": "관찰중",
                "observation_points": ["정책 결정자의 발언 수위"]
            }
        ]
        res = self.engine.generate_teaser(membership_queue)
        self.assertIsNotNone(res)
        self.assertIn("이번 주", res["sentence"])
        self.assertIn("수위", res["sentence"])
        self.assertEqual(res["sentence"].count("."), 1) # Single sentence
        
    def test_voice_lock_integration(self):
        # Even if template is fixed, let's test the helper
        sentence = "이 현상은 가능성이 있습니다. 전망됩니다."
        locked = self.engine._enforce_teaser_rules(sentence)
        self.assertTrue(any(word in locked for word in ["이미 결정됐다", "해야 한다", "필연이다", "선택지는 없다"]))
        self.assertNotIn("전망됩니다", locked)
        self.assertTrue(locked.count(".") >= 1)

if __name__ == '__main__':
    unittest.main()
