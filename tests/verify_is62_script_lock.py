import unittest
from src.issuesignal.script_lock_engine import ScriptLockEngine

class TestIS62ScriptLock(unittest.TestCase):
    
    def test_structure_generation(self):
        print("\n[TEST] Verifying 5-Step Structure (IS-66)...")
        protagonist = {
            "fact_text": "[Company A] Signed Exclusive Deal",
            "details": {"action_type": "AGREEMENT", "company": "Company A"},
            "bottleneck_reason": "Monopoly confirmed"
        }
        why_now = "Deadline approaching"
        
        result = ScriptLockEngine.generate(protagonist, why_now, "Energy")
        script = result['long_form']
        
        print(f"Generated Script:\n{script}")
        
        self.assertIn("1. 정의", script)
        self.assertIn("2. 표면 해석", script)
        self.assertIn("3. 시장의 오해", script)
        self.assertIn("4. 구조적 강제", script)
        self.assertIn("5. 결론", script)
        print("[PASS] 5-Step Structure Verified (IS-66 Updated).")

    def test_forbidden_words(self):
        print("\n[TEST] Verifying Forbidden Words...")
        bad_script = "이것은 추측입니다. 아마 될 수도 있습니다."
        valid, msg = ScriptLockEngine.validate(bad_script)
        self.assertFalse(valid)
        self.assertIn("Forbidden word", msg)
        print(f"[PASS] Forbidden Word Detected: {msg}")

    def test_mandatory_words(self):
        print("\n[TEST] Verifying Mandatory Words...")
        good_script = "이것은 필연입니다. 결정되었습니다."
        valid, msg = ScriptLockEngine.validate(good_script)
        self.assertTrue(valid)
        print("[PASS] Mandatory Words Verified.")
        
        bad_script = "안녕하세요. 좋은 아침입니다."
        valid, msg = ScriptLockEngine.validate(bad_script)
        self.assertFalse(valid)
        self.assertIn("Missing mandatory", msg)
        print(f"[PASS] Missing Mandatory Detected: {msg}")

if __name__ == '__main__':
    unittest.main()
