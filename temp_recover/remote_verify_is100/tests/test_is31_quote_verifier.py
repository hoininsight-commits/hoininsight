import unittest
from src.ops.quote_source_verifier import QuoteSourceVerifier

class TestQuoteSourceVerifier(unittest.TestCase):
    def setUp(self):
        self.verifier = QuoteSourceVerifier()

    def test_official_source_pass(self):
        pack = {
            "quote_text": "We will raise rates.",
            "speaker": "Powell",
            "event_name": "FOMC",
            "event_time_utc": "2026-01-30T19:00:00Z",
            "source_type": "OFFICIAL_TRANSCRIPT"
        }
        res = self.verifier.verify_quote(pack, [])
        self.assertEqual(res["verdict"], "PASS")

    def test_official_missing_context(self):
        pack = {
            "quote_text": "We will raise rates.",
            "speaker": "Powell",
            "event_name": None, # Missing context
            "event_time_utc": "2026-01-30T19:00:00Z",
            "source_type": "OFFICIAL_TRANSCRIPT"
        }
        res = self.verifier.verify_quote(pack, [])
        self.assertEqual(res["verdict"], "HOLD")
        self.assertEqual(res["reason_code"], "NO_CONTEXT")

    def test_cross_source_pass(self):
        pack = {
            "quote_text": "Policy change incoming.",
            "speaker": "Minister",
            "event_name": "Presser",
            "event_time_utc": "2026-01-30T10:00:00Z",
            "source_type": "NEWS_API" 
        }
        sources = [
            {"publisher": "REUTERS"},
            {"publisher": "BLOOMBERG"}
        ]
        res = self.verifier.verify_quote(pack, sources)
        self.assertEqual(res["verdict"], "PASS")
        self.assertEqual(res["reason_code"], "CROSS_SOURCE_STRONG")

    def test_cross_source_mixed_pass(self):
        pack = {"quote_text": "v", "speaker": "S", "event_name": "E", "event_time_utc": "T", "source_type": "NEWS"}
        sources = [
            {"publisher": "REUTERS"}, # STRONG
            {"publisher": "CNBC"}     # MEDIUM
        ]
        res = self.verifier.verify_quote(pack, sources)
        self.assertEqual(res["verdict"], "PASS")

    def test_single_source_hold(self):
        pack = {"quote_text": "v", "speaker": "S", "event_name": "E", "event_time_utc": "T", "source_type": "NEWS"}
        sources = [
            {"publisher": "REUTERS"}
        ]
        res = self.verifier.verify_quote(pack, sources)
        self.assertEqual(res["verdict"], "HOLD")
        self.assertEqual(res["reason_code"], "SINGLE_SOURCE")

if __name__ == '__main__':
    unittest.main()
