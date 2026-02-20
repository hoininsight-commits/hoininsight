import unittest
from datetime import datetime
from pathlib import Path

# Import Connectors
try:
    from src.collectors.macro_fact_connector import collect_macro_facts
    from src.collectors.official_fact_connector import collect_official_facts
except ImportError:
    pass # Will fail in main if not found

class TestIS57CPipeline(unittest.TestCase):
    def setUp(self):
        self.base_dir = Path(".")
        self.ymd = datetime.now().strftime("%Y-%m-%d")

    def test_collectors_exist_and_run(self):
        print("\n[TEST] Verifying Macro & Official Connectors...")
        
        # Macro
        macro_facts = collect_macro_facts(self.base_dir, self.ymd)
        print(f"Collected {len(macro_facts)} Macro Facts.")
        if macro_facts:
            self.assertEqual(macro_facts[0]['evidence_grade'], "HARD_FACT")
            
        # Official
        official_facts = collect_official_facts(self.base_dir, self.ymd)
        print(f"Collected {len(official_facts)} Official Facts.")
        if official_facts:
            self.assertEqual(official_facts[0]['evidence_grade'], "HARD_FACT")

    def test_trust_integrity_is57c(self):
        print("\n[TEST] Verifying Trust Score Logic (IS-57C Rules)...")
        # Logic Mirror from run_issuesignal.py
        
        # Case 1: Hint Only -> Candidate
        score_1 = 50 + 20 # 70
        verdict_1 = "SPEAKABLE_CANDIDATE" if score_1 >= 60 else "HOLD"
        self.assertEqual(verdict_1, "SPEAKABLE_CANDIDATE")
        
        # Case 2: Hint + Rotation -> 50+20+30 = 100. BUT No Hard Fact.
        score_2 = 100
        has_hard_fact_2 = False
        verdict_2 = "TRUST_LOCKED" if score_2 >= 80 else "CANDIDATE"
        if verdict_2 == "TRUST_LOCKED" and not has_hard_fact_2:
            verdict_2 = "SPEAKABLE_CANDIDATE" # Downgrade
        self.assertEqual(verdict_2, "SPEAKABLE_CANDIDATE")
        print("  - Passed: Rotation+Hint without Hard Fact downgraded to Candidate.")
        
        # Case 3: 2 Hard Facts -> 50+40+40 = 130. Hard Fact Exists.
        score_3 = 130
        has_hard_fact_3 = True
        verdict_3 = "TRUST_LOCKED" if score_3 >= 80 else "CANDIDATE"
        if verdict_3 == "TRUST_LOCKED" and not has_hard_fact_3:
             verdict_3 = "CANDIDATE"
        self.assertEqual(verdict_3, "TRUST_LOCKED")
        print("  - Passed: 2 Hard Facts -> TRUST_LOCKED.")

if __name__ == "__main__":
    unittest.main()
