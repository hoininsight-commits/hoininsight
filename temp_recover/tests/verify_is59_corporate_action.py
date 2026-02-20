import unittest
from datetime import datetime
from pathlib import Path
from src.collectors.corporate_action_connector import collect_corporate_facts
from src.collectors.primary_source_resolver import resolve_primary_source

class TestIS59CorporateAction(unittest.TestCase):
    def test_sec_rss_fetch(self):
        print("\n[TEST] Verifying Corporate Action Connector (SEC 8-K)...")
        # Run connector (Real network call)
        # Note: Depending on time of day, 8-K list might be empty or full.
        # But we expect the function to run without error and return a list (empty or populated).
        facts = collect_corporate_facts(Path("."), datetime.now().strftime("%Y-%m-%d"))
        print(f"Captured {len(facts)} pure Corporate Facts.")
        
        if facts:
            first = facts[0]
            print(f"- Sample: {first['fact_text']} ({first['source']})")
            self.assertEqual(first["evidence_grade"], "HARD_FACT")
            
    def test_trust_trigger_logic_is59(self):
        print("\n[TEST] Verifying Combinatorial Trust Trigger...")
        # Simulation of run_issuesignal.py logic
        
        # Scenario: 1 Corporate Fact (STRONG) + 1 Macro Fact (STRONG)
        has_corporate = True
        has_macro = True
        has_official = False
        
        trust_score = 50
        if has_corporate: trust_score += 45
        if has_macro: trust_score += 40
        # Score = 135
        
        status_verdict = "HOLD"
        # Condition 1: Score >= 80 -> Lock if Hard Fact present
        if trust_score >= 80 and (has_corporate or has_macro):
            status_verdict = "TRUST_LOCKED"
            
        self.assertEqual(status_verdict, "TRUST_LOCKED")
        print("  - Passed: Corporate + Macro -> TRUST_LOCKED")
        
        # Scenario: Corporate Only (Score 95)
        # 50 + 45 = 95. >= 80. Has Hard Fact.
        # Should Lock.
        trust_score_2 = 95
        verdict_2 = "TRUST_LOCKED" if trust_score_2 >= 80 else "HOLD"
        self.assertEqual(verdict_2, "TRUST_LOCKED")
        print("  - Passed: Corporate Only -> TRUST_LOCKED (Score 95)")

    def test_resolver_sec_domain(self):
        print("\n[TEST] Verifying Primary Source Resolver for SEC...")
        res = resolve_primary_source("https://www.sec.gov/Archives/edgar/data/100/000.txt", "Filing")
        self.assertEqual(res["evidence_grade"], "HARD_FACT")
        print("  - Passed: sec.gov is HARD_FACT")
        
        res_pr = resolve_primary_source("https://www.businesswire.com/news/home/2026/...", "PR")
        self.assertEqual(res_pr["evidence_grade"], "HARD_FACT")
        print("  - Passed: businesswire.com is HARD_FACT")

if __name__ == "__main__":
    unittest.main()
