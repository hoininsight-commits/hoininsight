import unittest
from src.issuesignal.audience_gate import AudienceGateEngine

class TestIS36AudienceGate(unittest.TestCase):
    def setUp(self):
        self.gate = AudienceGateEngine()

    def test_internal_only_hold_status(self):
        # Even if urgency is high, HOLD status forces INTERNAL_ONLY
        data = {
            "status": "HOLD",
            "urgency_score": 95,
            "output_format_ko": "대형 영상 (LONG FORM)"
        }
        aud_ko, reason_ko = self.gate.classify(data)
        self.assertEqual(aud_ko, "내부전용")
        self.assertIn("보류(HOLD)", reason_ko)

    def test_internal_only_weak_diversity(self):
        data = {
            "status": "READY",
            "urgency_score": 95,
            "diversity_verdict": "HOLD" # Failed IS-32
        }
        aud_ko, reason_ko = self.gate.classify(data)
        self.assertEqual(aud_ko, "내부전용")
        self.assertIn("출처 다양성", reason_ko)

    def test_membership_long_form(self):
        data = {
            "status": "READY",
            "urgency_score": 85,
            "output_format_ko": "대형 영상 (LONG FORM)",
            "diversity_verdict": "PASS",
            "quote_verdict": "PASS"
        }
        aud_ko, reason_ko = self.gate.classify(data)
        self.assertEqual(aud_ko, "멤버십")
        self.assertIn("멤버십", reason_ko)

    def test_public_shorts(self):
        data = {
            "status": "READY",
            "urgency_score": 85,
            "output_format_ko": "숏츠 (SHORT FORM)",
            "diversity_verdict": "PASS",
            "quote_verdict": "PASS"
        }
        aud_ko, reason_ko = self.gate.classify(data)
        self.assertEqual(aud_ko, "공개")
        self.assertIn("공개 배포", reason_ko)

    def test_default_internal(self):
        data = {
            "status": "READY",
            "urgency_score": 45, # Low urgency
            "output_format_ko": "텍스트 카드",
            "diversity_verdict": "PASS",
            "quote_verdict": "PASS"
        }
        aud_ko, reason_ko = self.gate.classify(data)
        self.assertEqual(aud_ko, "내부전용")
        self.assertIn("긴급도가 낮거나", reason_ko)

if __name__ == '__main__':
    unittest.main()
