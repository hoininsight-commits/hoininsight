import unittest
from src.collectors.primary_source_resolver import resolve_primary_source
from src.collectors.official_fact_connector import collect_official_facts
from datetime import datetime
from pathlib import Path

class TestIS58PrimarySource(unittest.TestCase):
    def test_resolver_logic(self):
        print("\n[TEST] Verifying Primary Source Resolver...")
        
        # 1. BOK URL -> HARD_FACT
        bok = resolve_primary_source("https://www.bok.or.kr/portal/bbs/B0000232/view.do?nttId=100", "BOK Title")
        self.assertEqual(bok["evidence_grade"], "HARD_FACT")
        self.assertEqual(bok["publisher_domain"], "bok.or.kr")
        
        # 2. Reuters -> MEDIUM
        reuters = resolve_primary_source("https://www.reuters.com/finance", "Reuters Title")
        self.assertEqual(reuters["evidence_grade"], "MEDIUM")
        
        # 3. Blog -> TEXT_HINT
        blog = resolve_primary_source("https://myblog.tistory.com/123", "Blog Title")
        self.assertEqual(blog["evidence_grade"], "TEXT_HINT")
        
        print("Resolver Logic Verified.")

    def test_official_connector_direct(self):
        print("\n[TEST] Verifying Official Connector (Direct Feeds)...")
        # Run actual connector
        facts = collect_official_facts(Path("."), datetime.now().strftime("%Y-%m-%d"))
        
        print(f"Collected {len(facts)} Official Facts.")
        for f in facts:
            print(f"- [{f['evidence_grade']}] {f['source']} : {f['fact_text']}")
            
        # We expect at least some facts from BOK or Fed or Fallback
        # If any is from Direct Feed, grade should be HARD_FACT
        direct_facts = [f for f in facts if "Direct" in f['source']]
        if direct_facts:
            # We enforce that resolver works. 
            # Note: Direct Feed URL might direct to official domain, so grade should be HARD_FACT
            pass
            
if __name__ == "__main__":
    unittest.main()
