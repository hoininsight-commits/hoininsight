import unittest
from src.ops.diversity_enforcer import DiversityEnforcer

class TestDiversityEnforcer(unittest.TestCase):
    def setUp(self):
        self.enforcer = DiversityEnforcer()

    def test_wire_chain_duplication(self):
        sources = [
            {"publisher": "Reuters", "raw_content": "Original wire content"},
            {"publisher": "Yahoo Finance", "raw_content": "According to Reuters...", "normalized_url": "https://finance.yahoo.com/news/1"}
        ]
        res = self.enforcer.enforce(sources)
        self.assertEqual(res["verdict"], "HOLD")
        self.assertEqual(res["reason_code"], "WIRE_CHAIN_DUPLICATION")
        self.assertEqual(res["clusters_count"], 1)

    def test_pass_diverse_sources(self):
        sources = [
            {"publisher": "SEC", "source_type": "FILING", "url": "https://sec.gov/1", "title": "10-K"},
            {"publisher": "Reuters", "source_type": "NEWS", "url": "https://reuters.com/2", "title": "News Report"}
        ]
        res = self.enforcer.enforce(sources)
        self.assertEqual(res["verdict"], "PASS")
        self.assertEqual(res["clusters_count"], 2)
        self.assertEqual(res["families_count"], 2)

    def test_lack_families(self):
        sources = [
            {"publisher": "Reuters", "source_type": "NEWS", "url": "https://reuters.com/1"},
            {"publisher": "Bloomberg", "source_type": "NEWS", "url": "https://bloomberg.com/2"} # Both are MAJOR_MEDIA
        ]
        res = self.enforcer.enforce(sources)
        self.assertEqual(res["verdict"], "HOLD")
        self.assertEqual(res["reason_code"], "LACK_SOURCE_FAMILIES")

if __name__ == '__main__':
    unittest.main()
