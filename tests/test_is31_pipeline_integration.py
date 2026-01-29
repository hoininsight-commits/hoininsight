import unittest
import json
from pathlib import Path
from src.ops.quote_failsafe import QuoteFailsafe

class TestIS31Integration(unittest.TestCase):
    def test_demotion_logic(self):
        failsafe = QuoteFailsafe(Path("."))
        
        # 1. Mock a trigger topic that should be READY
        topic = {
            "topic_id": "T1",
            "trigger_type": "SPEECH",
            "status": "READY",
            "candidate_id": "E1",
            "source_candidates": ["E1"]
        }
        
        # 2. Mock events_index where E1 lacks an anchor token (should fail collection)
        events_index = {
            "E1": {
                "event_id": "E1",
                "trigger_type": "SPEECH",
                "raw_content": "The weather is nice.", # No anchor token
                "speaker": "Speaker",
                "event_name": "Test Event",
                "source_type": "OFFICIAL_TRANSCRIPT"
            }
        }
        
        processed = failsafe.process_ranked_topics([topic], events_index)
        
        # 3. Assert demotion
        self.assertEqual(processed[0]["status"], "HOLD")
        self.assertEqual(processed[0]["quote_verdict"], "REJECT")
        self.assertEqual(processed[0]["quote_reason_code"], "QUOTE_COLLECTION_FAILED")
        self.assertTrue(processed[0].get("is_quote_demoted"))

    def test_pass_logic(self):
        failsafe = QuoteFailsafe(Path("."))
        
        # 1. Mock a trigger topic
        topic = {
            "topic_id": "T2",
            "trigger_type": "SPEECH",
            "status": "READY",
            "candidate_id": "E2"
        }
        
        # 2. Mock events_index with anchor token
        events_index = {
            "E2": {
                "event_id": "E2",
                "trigger_type": "SPEECH",
                "raw_content": "We will raise interest rates.", # Has anchor
                "speaker": "Powell",
                "event_name": "FOMC",
                "event_time_utc": "2026-01-30T19:00:00Z",
                "source_type": "OFFICIAL_TRANSCRIPT",
                "source_url": "http://fed.gov"
            }
        }
        
        processed = failsafe.process_ranked_topics([topic], events_index)
        
        # 3. Assert PASS
        self.assertEqual(processed[0]["status"], "READY")
        self.assertEqual(processed[0]["quote_verdict"], "PASS")
        self.assertIsNotNone(processed[0].get("trigger_quote"))

if __name__ == '__main__':
    unittest.main()
