import os
import json
import unittest
from pathlib import Path
from datetime import datetime
from src.collectors.catalyst_event_collector import CatalystEventCollector

class TestCatalystEventLayer(unittest.TestCase):
    def setUp(self):
        self.project_root = Path(".")
        self.collector = CatalystEventCollector(self.project_root)
        self.test_data_dir = self.project_root / "data/ops"
        self.test_data_dir.mkdir(parents=True, exist_ok=True)

    def test_01_sec_filing_trigger(self):
        print("\n[Test 01] SEC Filing Trigger")
        mock_item = {
            "source_id": "sec_8k_rss",
            "title": "APPLE INC (AAPL) 8-K Agreement",
            "summary": "Item 1.01 Major agreement signed.",
            "link": "https://www.sec.gov/...",
            "date": "2026-02-03T10:00:00",
            "tag_mapping": "US_SEC_FILING"
        }
        event = self.collector._process_item(mock_item)
        self.assertIsNotNone(event)
        self.assertEqual(event["tag"], "US_CONTRACT_AWARD") # "agreement" keyword should map to award/contract
        self.assertIn("AAPL", event["entities"])

    def test_02_kr_disclosure_trigger(self):
        print("\n[Test 02] KR Disclosure Trigger")
        mock_item = {
            "source_id": "krx_disclosure",
            "title": "현대차(005380) 유상증자 결정",
            "summary": "핵심 자재 수급을 위한 유상증자",
            "link": "https://kind.krx.co.kr/...",
            "date": "2026-02-03T11:00:00"
        }
        event = self.collector._process_item(mock_item)
        self.assertIsNotNone(event)
        self.assertEqual(event["tag"], "KR_DART_DISCLOSURE")
        self.assertIn("005380", event["entities"])

    def test_03_rumor_trigger(self):
        print("\n[Test 03] Reputable Rumor Trigger")
        mock_item = {
            "source_id": "news_node",
            "title": "Exclusive: Google in takeover talks with HubSpot, sources say",
            "summary": "Acquisition rumor surfaces.",
            "link": "https://news.com/123",
            "date": "2026-02-03T12:00:00"
        }
        event = self.collector._process_item(mock_item)
        self.assertIsNotNone(event)
        self.assertEqual(event["tag"], "US_MA_RUMOR")
        self.assertEqual(event["confidence"], "B")

    def test_04_deduplication(self):
        print("\n[Test 04] Deduplication")
        events = [
            {"event_id": "id1", "title": "Event 1"},
            {"event_id": "id1", "title": "Event 1 Duplicate"},
            {"event_id": "id2", "title": "Event 2"}
        ]
        deduped = self.collector._deduplicate(events)
        self.assertEqual(len(deduped), 2)

    def test_05_multi_entity_extraction(self):
        print("\n[Test 05] Multi-entity Extraction")
        content = "Tesla and Panasonic agree on battery supply for USA factory."
        entities = self.collector._extract_entities(content)
        # Should catch Tesla and Panasonic as named entities
        self.assertIn("Tesla", entities)
        self.assertIn("Panasonic", entities)
        # Should not catch 'Agree' or 'On' (due to noise filter)
        self.assertNotIn("Agree", entities)
        self.assertNotIn("On", entities)

    def test_06_empty_day_graceful(self):
        print("\n[Test 06] Empty Day Graceful Output")
        # Temporarily mock simulate_fetching to return empty
        original_sim = self.collector._simulate_fetching
        self.collector._simulate_fetching = lambda: []
        events = self.collector.collect()
        self.collector._simulate_fetching = original_sim
        
        self.assertEqual(len(events), 0)
        self.assertTrue(Path(self.collector.output_path).exists())

def run_verification():
    print("\n" + "="*60)
    print("📋 IS-95-2 CATALYST EVENT LAYER VERIFICATION")
    print("="*60)
    
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCatalystEventLayer)
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    
    if result.wasSuccessful():
        print("\nVERIFICATION SUCCESS")
        return True
    else:
        print("\nVERIFICATION FAILURE")
        return False

if __name__ == "__main__":
    success = run_verification()
    if not success:
        exit(1)
