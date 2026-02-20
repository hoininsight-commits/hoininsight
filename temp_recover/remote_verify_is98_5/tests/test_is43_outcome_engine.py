import unittest
from src.issuesignal.outcome_classifier import OutcomeClassifier

class TestIS43OutcomeClassifier(unittest.TestCase):
    def setUp(self):
        self.classifier = OutcomeClassifier()

    def test_on_time_logic(self):
        signal = {"status": "READY"}
        # Reaction within 12h, correct direction
        reaction = {"time_diff_hours": 8, "direction_match": True, "volatility_level": "HIGH"}
        result = self.classifier.classify_outcome(signal, reaction)
        self.assertEqual(result, "정확")

    def test_early_logic(self):
        signal = {"status": "READY"}
        # Reaction after 60h (between 48-168h), correct direction
        reaction = {"time_diff_hours": 60, "direction_match": True, "volatility_level": "HIGH"}
        result = self.classifier.classify_outcome(signal, reaction)
        self.assertEqual(result, "너무 빠름")

    def test_silence_correct_logic(self):
        signal = {"status": "SILENT"}
        # No volatility increase
        reaction = {"volatility_level": "LOW"}
        result = self.classifier.classify_outcome(signal, reaction)
        self.assertEqual(result, "침묵이 옳았음")

    def test_failure_logic(self):
        signal = {"status": "READY"}
        # Wrong direction
        reaction = {"time_diff_hours": 12, "direction_match": False}
        result = self.classifier.classify_outcome(signal, reaction)
        self.assertEqual(result, "예측 실패")

if __name__ == '__main__':
    unittest.main()
