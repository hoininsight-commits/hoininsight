import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from src.issuesignal.time_decay import TriggerTimeDecayEngine

class TestIS33Integration(unittest.TestCase):
    def test_pipeline_decay_flow(self):
        engine = TriggerTimeDecayEngine(max_lifetime_hours=48)
        
        # 1. Mock a trigger from 25 hours ago (should be HOLD / 보류)
        now = datetime.now(timezone.utc)
        trigger_time = (now - timedelta(hours=25)).isoformat()
        
        topic = {
            "topic_id": "T5",
            "event_time_utc": trigger_time,
            "status": "READY"
        }
        
        # 2. Process
        res = engine.process_trigger(topic, current_time=now)
        
        # 3. Assert
        self.assertEqual(res["decay_state_ko"], "보류")
        self.assertEqual(res["current_confidence"], 47) # 100 * (1 - 25/48) = 47.9 -> 47
        self.assertIn("시간 경과", res["elapsed_time_str"])
        
    def test_re_arm_in_pipeline(self):
        engine = TriggerTimeDecayEngine(max_lifetime_hours=48)
        
        # 30 hours ago -> ~37% (SILENT / 침묵)
        now = datetime.now(timezone.utc)
        trigger_time = (now - timedelta(hours=30)).isoformat()
        
        topic = {
            "topic_id": "T6",
            "event_time_utc": trigger_time,
            "status": "HOLD"
        }
        
        # First process
        engine.process_trigger(topic, current_time=now)
        self.assertEqual(topic["decay_state_ko"], "침묵")
        
        # Now re-arm with hard evidence
        hard_evidence = [{"family": "OFFICIAL"}]
        engine.re_arm(topic, hard_evidence)
        
        # Should be boosted by 30% -> 37 + 30 = 67% (HOLD / 보류)
        self.assertEqual(topic["decay_state_ko"], "보류")
        self.assertTrue(topic["re_armed"])

if __name__ == '__main__':
    unittest.main()
