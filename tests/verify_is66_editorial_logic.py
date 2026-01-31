
import unittest
from datetime import datetime
import sys
from pathlib import Path

# We need to test logic used in run_issuesignal.py
# Since logic isn't encapsulated in a class (it's in main), we should extract it or integration test it.
# Ideally, we should have a 'CandidateSelector' class. 
# For now, let's verify the ScriptLockEngine 5-step structure again as part of this.
# And verify the dashboard HTML generation (light check).

sys.path.append(str(Path(__file__).parent.parent))
from src.issuesignal.script_lock_engine import ScriptLockEngine

class TestIS66Editorial(unittest.TestCase):
    def test_5_step_structure(self):
        """Verify the new 5-step structure (IS-66)."""
        # 1. Def, 2. Surface, 3. Misread, 4. Structural, 5. Conclusion
        mock_cand = {
            "fact_text": "Fact Text",
            "details": {"company": "TestCorp", "action_type": "Action"},
            "bottleneck_reason": "Reason"
        }
        res = ScriptLockEngine.generate(mock_cand, "WhyNow", "Sector", [])
        algo_script = res['long_form']
        
        expected_headers = [
            "1. 정의 (Signal)",
            "2. 표면 해석 (Surface)",
            "3. 시장의 오해 (Misread)",
            "4. 구조적 강제 (Structural Force)",
            "5. 결론 (Conclusion)"
        ]
        
        for h in expected_headers:
            self.assertIn(h, algo_script, f"Missing header: {h}")

if __name__ == '__main__':
    unittest.main()
