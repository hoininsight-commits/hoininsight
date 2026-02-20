import unittest
from datetime import datetime
from src.ops.quote_evidence_collector import QuoteEvidenceCollector

class TestQuoteEvidenceCollector(unittest.TestCase):
    def setUp(self):
        self.collector = QuoteEvidenceCollector()

    def test_collect_speech_with_anchor(self):
        trigger = {
            "trigger_type": "SPEECH",
            "raw_content": "We decided to raise the interest rates by 25 basis points.",
            "speaker": "Jerome Powell",
            "event_name": "FOMC Press Conference",
            "event_time_utc": "2026-01-30T19:00:00Z",
            "source_type": "OFFICIAL_TRANSCRIPT",
            "source_url": "https://federalreserve.gov/news"
        }
        result = self.collector.collect_quote(trigger)
        self.assertIsNotNone(result)
        self.assertEqual(result["speaker"], "Jerome Powell")
        self.assertIn("raise", result["quote_text"].lower())

    def test_reject_no_anchor(self):
        trigger = {
            "trigger_type": "SPEECH",
            "raw_content": "The weather is nice in Washington today.",
            "speaker": "Speaker",
            "event_name": "Casual Chat",
            "source_type": "OFFICIAL_TRANSCRIPT"
        }
        result = self.collector.collect_quote(trigger)
        self.assertIsNone(result)

    def test_calendar_special_case(self):
        trigger = {
            "trigger_type": "CALENDAR",
            "event_name": "Earnings Release: AAPL",
            "event_time_utc": "2026-01-30T21:30:00Z",
            "speaker": "Apple Inc.",
            "source_type": "OFFICIAL_SCHEDULE",
            "raw_content": "AAPL Q4 Earnings Release at 4:30 PM ET"
        }
        result = self.collector.collect_quote(trigger)
        self.assertIsNotNone(result)

    def test_out_of_scope(self):
        trigger = {
            "trigger_type": "PRICE_SPIKE", # Out of scope
            "raw_content": "BTC up 10%",
            "source_type": "EXCHANGE"
        }
        result = self.collector.collect_quote(trigger)
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
