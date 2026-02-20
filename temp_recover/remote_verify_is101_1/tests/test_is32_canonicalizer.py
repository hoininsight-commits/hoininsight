import unittest
from src.ops.source_canonicalizer import SourceCanonicalizer

class TestSourceCanonicalizer(unittest.TestCase):
    def setUp(self):
        self.canon = SourceCanonicalizer()

    def test_url_normalization_utm(self):
        url1 = "https://www.reuters.com/article/test?utm_source=twitter&id=123"
        url2 = "http://reuters.com/article/test/"
        
        s1 = self.canon.canonicalize({"url": url1, "publisher": "Reuters"})
        s2 = self.canon.canonicalize({"url": url2, "publisher": "Reuters"})
        
        self.assertEqual(s1["normalized_url"], "https://reuters.com/article/test")
        self.assertEqual(s2["normalized_url"], "http://reuters.com/article/test")
        # Fingerprints will differ due to scheme differences (http/https), 
        # but normalize_url handles path/query.

    def test_sec_doc_id(self):
        url = "https://www.sec.gov/Archives/edgar/data/320193/000032019324000006/aapl-20231230.htm"
        s = self.canon.canonicalize({"url": url, "publisher": "SEC", "source_type": "FILING"})
        
        self.assertIn("000032019324000006", s["canonical_source_id"])
        # Mirrors of the same SEC ID should have the same fingerprint
        self.assertEqual(s["canonical_fingerprint"], self.canon.canonicalize({"url": "https://mirror.com/000032019324000006", "publisher": "SEC"})["canonical_fingerprint"])

    def test_headline_fallback(self):
        s = self.canon.canonicalize({"title": "Major Policy Shift", "date": "2026-01-30"})
        self.assertIsNotNone(s["canonical_source_id"])
        self.assertIn("2026-01-30", s["canonical_source_id"])

if __name__ == '__main__':
    unittest.main()
