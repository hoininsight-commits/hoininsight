import unittest
from src.issuesignal.why_now_synthesizer import WhyNowSynthesizer

class TestIS61WhyNow(unittest.TestCase):
    
    def test_deadline_trigger(self):
        print("\n[TEST] Verifying Deadline Trigger...")
        protagonist = {
            "source_date": "2026-02-01",
            "details": {"raw_summary": "The agreement deadline is approaching."}
        }
        result = WhyNowSynthesizer.synthesize(protagonist, [], False)
        print(f"Result: {result}")
        self.assertIn("DEADLINE", result)
        self.assertIn("기한 압박", result)

    def test_macro_coincidence(self):
        print("\n[TEST] Verifying Macro Coincidence...")
        protagonist = {
            "source_date": "2026-02-01",
            "details": {"raw_summary": "Just normal biz."}
        }
        # Macro event on same day (within 2 days)
        context = [{
            "evidence_grade": "HARD_FACT",
            "source_date": "2026-02-02", 
            "fact_text": "[FOMC] Rate Decision"
        }]
        result = WhyNowSynthesizer.synthesize(protagonist, context, False)
        print(f"Result: {result}")
        self.assertIn("외부 변수(Rate Decision) 발표 시점", result or "")
        self.assertIsNotNone(result)

    def test_rotation_trigger(self):
        print("\n[TEST] Verifying Rotation Trigger...")
        protagonist = {
            "source_date": "2026-02-01",
            "details": {"raw_summary": "Investing."}
        }
        result = WhyNowSynthesizer.synthesize(protagonist, [], True, "Energy")
        print(f"Result: {result}")
        self.assertIn("Energy 섹터로 이동하는 변곡점", result)

    def test_weak_signal_fallback_and_failure(self):
        print("\n[TEST] Verifying Weak Signal Failure...")
        protagonist = {
            "source_date": "2026-02-01",
            "bottleneck_score": 50, # Low score
            "details": {"raw_summary": "Just doing things.", "action_type": "AGREEMENT"}
        }
        result = WhyNowSynthesizer.synthesize(protagonist, [], False)
        print(f"Result: {result}")
        self.assertIsNone(result)
        
        # High Score Fallback
        print("\n[TEST] Verifying High Score Fallback...")
        protagonist["bottleneck_score"] = 85
        result = WhyNowSynthesizer.synthesize(protagonist, [], False)
        print(f"Result: {result}")
        self.assertIn("경쟁사가 따라올 수 없는 속도", result)

if __name__ == '__main__':
    unittest.main()
