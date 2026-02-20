
import unittest
import json
import shutil
from pathlib import Path
from datetime import datetime
import dataclasses
from src.issuesignal.dashboard.models import DecisionCard
from src.issuesignal.script_lock_engine import ScriptLockEngine
# Mock imports if needed, but we can verify by checking output existence
# or importing the module functions if possible. 
# Better to run a subprocess of run_issuesignal.py with controlled data
# But that's integration test.
# Let's verify valid DecisionCard structure and ScriptLockEngine standalone.

class TestIS62LoopLock(unittest.TestCase):
    def setUp(self):
        self.engine = ScriptLockEngine()
        self.protagonist = {
            "fact_text": "엔비디아, 차세대 GPU B100 전량 TSMC 3nm 공정 예약",
            "source": "Bloomberg",
            "details": {"company": "NVIDIA", "ticker": "NVDA"}
        }
        self.bottleneck = {"protagonists": [self.protagonist]}
        self.whynow = {"trigger_type": "CAPITAL_ROTATION", "description": "AI Semis Rotation"}

    def test_script_lock_structure(self):
        """Verify generated script follows 6-step lock."""
        result = self.engine.generate(self.protagonist, self.whynow, "Semiconductors")
        long_form = result.get('long_form', '')
        
        required_steps = [
            "1. 정의", "2. 표면 해석", "3. 시장의 오해", 
            "4. 구조적 강제", "5. WHY NOW", "6. 결론"
        ]
        for step in required_steps:
            self.assertIn(step, long_form, f"Missing locked step: {step}")

    def test_forbidden_words(self):
        """Verify forbidden words are rejected or handled."""
        # This test assumes the engine validator logic is working.
        # Let's test the validator explicitly if reachable
        is_valid, reason = ScriptLockEngine.validate("아마도 그럴 것 같습니다.")
        self.assertFalse(is_valid)
        self.assertIn("Forbidden word", reason)

    def test_mandatory_words(self):
        """Verify mandatory words."""
        is_valid, reason = ScriptLockEngine.validate("이것은 결정적이고 필연적인 흐름입니다.")
        self.assertTrue(is_valid)

if __name__ == '__main__':
    unittest.main()
