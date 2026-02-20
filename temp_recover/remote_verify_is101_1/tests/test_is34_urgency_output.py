import unittest
from src.issuesignal.urgency_engine import UrgencyEngine
from src.issuesignal.output_decider import OutputDecider

class TestIS34UrgencyOutput(unittest.TestCase):
    def setUp(self):
        self.urgency = UrgencyEngine()
        self.decider = OutputDecider()

    def test_urgency_scoring(self):
        # Case 1: High urgency keywords
        trigger = {"title": "긴급: 금리 인상 마감 임박", "raw_content": "자금 투자 마감 전 최종 공지"}
        score = self.urgency.calculate_urgency(trigger)
        self.assertGreaterEqual(score, 90)
        
        # Case 2: Medium urgency
        trigger = {"title": "금리 변동 추이 분석"}
        score = self.urgency.calculate_urgency(trigger)
        self.assertGreaterEqual(score, 40)
        self.assertLess(score, 60)

    def test_too_late_override(self):
        # Case 1: Keyword 'already priced'
        trigger = {"title": "이미 반영된 금리 결과"}
        reason = self.urgency.check_too_late(trigger)
        self.assertIsNotNone(reason)
        
        # Case 2: Time decay overflow (>36h) from IS-33
        trigger = {"elapsed_hours": 40}
        reason = self.urgency.check_too_late(trigger)
        self.assertIn("36시간 이상 경과", reason)

    def test_output_decider(self):
        # Long Form
        fmt, reason = self.decider.decide(95)
        self.assertEqual(fmt, "대형 영상 (LONG FORM)")
        
        # Shorts
        fmt, reason = self.decider.decide(75)
        self.assertEqual(fmt, "숏츠 (SHORT FORM)")
        
        # Too Late -> Silent
        fmt, reason = self.decider.decide(95, too_late_reason="선반영 뉴스")
        self.assertEqual(fmt, "침묵")
        self.assertIn("이미 반영됨", reason)

if __name__ == '__main__':
    unittest.main()
