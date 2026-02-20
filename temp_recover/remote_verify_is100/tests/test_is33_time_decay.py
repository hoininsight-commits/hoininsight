import unittest
from datetime import datetime, timedelta, timezone
from src.issuesignal.time_decay import TriggerTimeDecayEngine

class TestTriggerTimeDecayEngine(unittest.TestCase):
    def setUp(self):
        self.engine = TriggerTimeDecayEngine(max_lifetime_hours=48)

    def test_active_state(self):
        # 2 hours ago -> ~95% confidence
        now = datetime.now(timezone.utc)
        trigger_time = (now - timedelta(hours=2)).isoformat()
        trigger = {"event_time_utc": trigger_time}
        
        res = self.engine.process_trigger(trigger, current_time=now)
        self.assertGreaterEqual(res["current_confidence"], 90)
        self.assertEqual(res["decay_state_ko"], "활성")

    def test_hold_state(self):
        # 24 hours ago -> 50% confidence (48h max)
        now = datetime.now(timezone.utc)
        trigger_time = (now - timedelta(hours=24)).isoformat()
        trigger = {"event_time_utc": trigger_time}
        
        res = self.engine.process_trigger(trigger, current_time=now)
        self.assertEqual(res["current_confidence"], 50)
        self.assertEqual(res["decay_state_ko"], "보류")

    def test_silent_state(self):
        # 40 hours ago -> ~16% confidence
        now = datetime.now(timezone.utc)
        trigger_time = (now - timedelta(hours=40)).isoformat()
        trigger = {"event_time_utc": trigger_time}
        
        res = self.engine.process_trigger(trigger, current_time=now)
        self.assertLess(res["current_confidence"], 40)
        self.assertEqual(res["decay_state_ko"], "침묵")

    def test_re_arm_success(self):
        trigger = {
            "current_confidence": 30,
            "decay_state_internal": "SILENT",
            "decay_state_ko": "침묵"
        }
        new_evidence = [{"family": "FILINGS"}]
        
        res = self.engine.re_arm(trigger, new_evidence)
        self.assertEqual(res["current_confidence"], 60)
        self.assertEqual(res["decay_state_ko"], "보류")
        self.assertTrue(res["re_armed"])

    def test_re_arm_fail_weak_evidence(self):
        trigger = {
            "current_confidence": 30,
            "decay_state_internal": "SILENT",
            "decay_state_ko": "침묵"
        }
        new_evidence = [{"family": "MAJOR_MEDIA"}]
        
        res = self.engine.re_arm(trigger, new_evidence)
        self.assertEqual(res["current_confidence"], 30)
        self.assertFalse(res.get("re_armed", False))

if __name__ == '__main__':
    unittest.main()
