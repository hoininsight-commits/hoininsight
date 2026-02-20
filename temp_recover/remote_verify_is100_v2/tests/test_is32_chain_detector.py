import unittest
from src.ops.dependency_chain_detector import DependencyChainDetector

class TestDependencyChainDetector(unittest.TestCase):
    def setUp(self):
        self.detector = DependencyChainDetector()

    def test_media_attribution_korean(self):
        content = "로이터에 따르면, 연준이 금리를 인상할 가능성이 높습니다."
        source = {"raw_content": content, "publisher": "SomeNews"}
        res = self.detector.detect(source)
        self.assertEqual(res["dependency_label"], "DERIVED")
        self.assertEqual(res["derived_from"], "로이터")

    def test_media_attribution_english(self):
        content = "According to Reuters, the Fed is considering a pause."
        source = {"raw_content": content, "publisher": "MarketWatch"}
        res = self.detector.detect(source)
        self.assertEqual(res["dependency_label"], "DERIVED")
        self.assertIn("Reuters", res["derived_from"])

    def test_official_source_original(self):
        source = {
            "title": "Fed Press Release",
            "source_type": "OFFICIAL_RELEASE",
            "publisher": "Federal Reserve"
        }
        res = self.detector.detect(source)
        self.assertEqual(res["dependency_label"], "ORIGINAL")
        self.assertEqual(res["origin_confidence"], 95)

    def test_syndication_host(self):
        source = {
            "normalized_url": "https://finance.yahoo.com/news/test-article",
            "publisher": "Yahoo Finance"
        }
        res = self.detector.detect(source)
        self.assertEqual(res["dependency_label"], "DERIVED")
        self.assertEqual(res["derived_from"], "YAHOO_FINANCE")

if __name__ == '__main__':
    unittest.main()
