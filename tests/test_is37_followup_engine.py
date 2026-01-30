import unittest
from src.issuesignal.followup_engine import FollowUpEngine

class TestIS37FollowUpEngine(unittest.TestCase):
    def setUp(self):
        self.engine = FollowUpEngine()

    def test_followup_generation_policy(self):
        data = {
            "title": "금리 동결 결정",
            "raw_content": "한국은행이 금리를 동결하기로 정책을 발표했습니다.",
            "status": "READY"
        }
        plans = self.engine.plan_follow_ups(data)
        self.assertGreaterEqual(len(plans), 1)
        self.assertIn("정책 이행", plans[0]["topic"])
        self.assertIn("즉시", plans[0]["timing"]) # Check within translated string
        self.assertIn("POLICY", plans[0]["reason"])

    def test_followup_generation_earnings(self):
        data = {
            "title": "삼성전자 실적 발표",
            "raw_content": "삼성전자가 역대급 매출 및 영업이익을 달성했습니다.",
            "status": "READY"
        }
        plans = self.engine.plan_follow_ups(data)
        self.assertGreaterEqual(len(plans), 1)
        self.assertIn("실적 컨펌", plans[0]["topic"])
        self.assertIn("이벤트 기반", plans[0]["timing"])

    def test_silent_no_followup(self):
        data = {
            "status": "SILENT"
        }
        plans = self.engine.plan_follow_ups(data)
        self.assertEqual(len(plans), 0)

    def test_repetition_guard_placeholder(self):
        # Current logic uses fixed lists, but we ensure it doesn't return same exact thing
        # for every single topic without any variance.
        # In a real scenario, this would check against a 'memory' of previous topics.
        pass

if __name__ == '__main__':
    unittest.main()
