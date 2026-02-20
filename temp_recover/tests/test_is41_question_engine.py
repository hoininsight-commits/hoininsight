import unittest
from src.issuesignal.question_engine import AudienceQuestionEngine

class TestIS41QuestionEngine(unittest.TestCase):
    def setUp(self):
        self.engine = AudienceQuestionEngine()

    def test_prediction_logic(self):
        topic_policy = {"title": "미 연준 금리 동결 실적 발표", "urgency_score": 90}
        questions = self.engine.process_signal(topic_policy)
        
        # High urgency should have 4 questions
        self.assertEqual(len(questions), 4)
        self.assertTrue(any("금리" in q["question"] for q in questions))

    def test_classification_ticker_silent(self):
        topic = {"title": "반도체 수급", "urgency_score": 50}
        questions = self.engine.process_signal(topic)
        
        # Find question about ticker/company
        ticker_q = next((q for q in questions if "티커" in q["question"]), None)
        if ticker_q:
            self.assertEqual(ticker_q["classification"], "침묵 유지")
            self.assertEqual(ticker_q["strategy"], "(무대응)")

    def test_strategy_voice_lock(self):
        topic = {"title": "실적 발표", "urgency_score": 50}
        questions = self.engine.process_signal(topic)
        
        for q in questions:
            if q["strategy"] != "(무대응)":
                # Must be declarative (ends with '다' or '나')
                self.assertTrue(q["strategy"].endswith(("다.", "나.")))
                # No questions allowed in strategy
                self.assertNotIn("?", q["strategy"])

if __name__ == '__main__':
    unittest.main()
