import unittest
from src.issuesignal.urgency_engine import UrgencyEngine
from src.issuesignal.output_decider import OutputDecider

class TestIS34PipelineIntegration(unittest.TestCase):
    def test_editorial_decision_flow(self):
        urgency_eng = UrgencyEngine()
        output_dec = OutputDecider()
        
        # 1. Mock a high urgency topic
        topic = {
            "topic_id": "T7",
            "title": "긴급: 금리 인상 결정 임박",
            "raw_content": "자금 투자 마감 전 최종 공지",
            "status": "READY"
        }
        
        # 2. Process
        u_score = urgency_eng.calculate_urgency(topic)
        too_late = urgency_eng.check_too_late(topic)
        fmt_ko, reason_ko = output_dec.decide(u_score, too_late)
        
        topic["urgency_score"] = u_score
        topic["output_format_ko"] = fmt_ko
        topic["editorial_reason_ko"] = reason_ko
        
        # 3. Assert
        self.assertGreaterEqual(topic["urgency_score"], 90)
        self.assertEqual(topic["output_format_ko"], "대형 영상 (LONG FORM)")
        self.assertIn("대형 기획 영상", topic["editorial_reason_ko"])

    def test_too_late_silent_flow(self):
        urgency_eng = UrgencyEngine()
        output_dec = OutputDecider()
        
        # Mock a 'too late' topic
        topic = {
            "topic_id": "T8",
            "title": "이미 반영된 연준 소식",
            "status": "READY"
        }
        
        u_score = urgency_eng.calculate_urgency(topic)
        too_late = urgency_eng.check_too_late(topic)
        fmt_ko, reason_ko = output_dec.decide(u_score, too_late)
        
        if "침묵" in fmt_ko and topic.get("status") == "READY":
             topic["status"] = "SILENT"
        
        self.assertEqual(topic["status"], "SILENT")
        self.assertIn("이미 반영됨", reason_ko)

if __name__ == '__main__':
    unittest.main()
