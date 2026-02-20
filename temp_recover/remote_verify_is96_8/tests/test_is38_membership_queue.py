import unittest
from src.issuesignal.membership_queue import MembershipQueueEngine

class TestIS38MembershipQueue(unittest.TestCase):
    def setUp(self):
        self.engine = MembershipQueueEngine()

    def test_queue_generation_eligibility(self):
        topics = [
            {
                "title": "금리 관련 주제",
                "urgency_score": 90,
                "follow_up_plans": [{"topic": "금리 후속 (LONG FORM)", "timing": "즉시 (24~48시간)", "reason": "POLICY"}]
            },
            {
                "title": "저긴급 주제",
                "urgency_score": 30,
                "follow_up_plans": [{"topic": "일반 후속", "timing": "장기", "reason": "CAPITAL_FLOW"}]
            }
        ]
        queue = self.engine.generate_queue(topics)
        self.assertEqual(len(queue), 1)
        self.assertEqual(queue[0]["title"], "금리 후속")
        self.assertEqual(queue[0]["status"], "분석중")

    def test_disclosure_limiter_stripping(self):
        topics = [
            {
                "title": "삼성전자 실적",
                "urgency_score": 75,
                "follow_up_plans": [{"topic": "삼성전자 하반기 전망 (SHORT FORM)", "timing": "단기 (1~2주)", "reason": "EARNINGS"}]
            }
        ]
        queue = self.engine.generate_queue(topics)
        # We check if (SHORT FORM) was stripped
        self.assertEqual(queue[0]["title"], "삼성전자 하반기 전망")
        # Ensure no tickers or kill switches are in the item (they aren't added by default)
        self.assertNotIn("ticker", queue[0])
        self.assertNotIn("kill_switch", queue[0])

    def test_observation_points_generation(self):
        topics = [
            {
                "title": "미 연준 금리 결정",
                "urgency_score": 80,
                "follow_up_plans": [{"topic": "금리 정책 반응", "timing": "이벤트 기반 (실적/발표/인도)", "reason": "POLICY"}]
            }
        ]
        queue = self.engine.generate_queue(topics)
        self.assertGreater(len(queue[0]["observation_points"]), 0)
        self.assertIn("정책", queue[0]["observation_points"][0])

if __name__ == '__main__':
    unittest.main()
