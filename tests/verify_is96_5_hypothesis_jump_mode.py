import os
import json
import unittest
from pathlib import Path
from datetime import datetime
from src.decision.assembler import DecisionAssembler

class TestHypothesisJumpMode(unittest.TestCase):
    def setUp(self):
        self.project_root = Path(".")
        self.assembler = DecisionAssembler(output_dir="data/decision_test")
        self.test_events_file = self.project_root / "data/ops/catalyst_events.json"

    def test_01_official_source_ready(self):
        print("\n[Test 01] Official Source -> READY")
        catalyst_events = [{
            "event_id": "evt_official_001",
            "tag": "US_SEC_FILING",
            "title": "NVIDIA 8-K: Strategic Partnership with xAI",
            "entities": ["NVDA", "xAI"],
            "source": {"id": "sec_edgar", "url": "https://sec.gov"},
            "timestamp": datetime.now().isoformat(),
            "confidence": "A",
            "why_now_hint": "State-driven"
        }]
        
        results = self.assembler.assemble([], catalyst_events)
        unit = results["interpretation_units"][0]
        decision = results["speakability_decision"][unit["interpretation_id"]]
        skeleton = results["narrative_skeleton"][unit["interpretation_id"]]
        
        self.assertEqual(unit["mode"], "HYPOTHESIS_JUMP")
        self.assertEqual(decision["speakability_flag"], "READY")
        self.assertIn("지금은 '확정'이 아니라 '가능성'이다", skeleton["hook"])
        self.assertIn("NVIDIA 8-K", skeleton["evidence_3"][0])

    def test_02_single_rumor_hold(self):
        print("\n[Test 02] Single Rumor -> HOLD")
        catalyst_events = [{
            "event_id": "evt_rumor_001",
            "tag": "US_MA_RUMOR",
            "title": "Exclusive: SpaceX considering acquisition of xAI assets",
            "entities": ["SpaceX", "xAI"],
            "source": {"id": "reputable_news", "url": "https://news.com"},
            "timestamp": datetime.now().isoformat(),
            "confidence": "B",
            "why_now_hint": "Hybrid-driven"
        }]
        
        results = self.assembler.assemble([], catalyst_events)
        unit = results["interpretation_units"][0]
        decision = results["speakability_decision"][unit["interpretation_id"]]
        
        self.assertEqual(decision["speakability_flag"], "HOLD")
        self.assertIn("requires verification", decision["speakability_reasons"][0])

    def test_03_untrusted_source_drop(self):
        print("\n[Test 03] Untrusted Source -> DROP")
        # Trust 'D' is mocked in gate as DROP
        catalyst_events = [{
            "event_id": "evt_bad_001",
            "tag": "US_MA_RUMOR",
            "title": "Fake news about merger",
            "entities": ["ENTITY_X"],
            "source": {"id": "bad_source", "url": "https://fake.io"},
            "timestamp": datetime.now().isoformat(),
            "confidence": "D", 
            "why_now_hint": "State-driven"
        }]
        
        results = self.assembler.assemble([], catalyst_events)
        unit = results["interpretation_units"][0]
        decision = results["speakability_decision"][unit["interpretation_id"]]
        
        self.assertEqual(decision["speakability_flag"], "DROP")
        self.assertIn("untrusted", decision["speakability_reasons"][0].lower())

    def test_04_multi_entity_mapping(self):
        print("\n[Test 04] Multi-entity Mapping")
        catalyst_events = [{
            "event_id": "evt_multi_001",
            "tag": "US_CONTRACT_AWARD",
            "title": "Tesla and Panasonic deal",
            "entities": ["Tesla", "Panasonic"],
            "confidence": "A"
        }]
        
        results = self.assembler.assemble([], catalyst_events)
        unit = results["interpretation_units"][0]
        skeleton = results["narrative_skeleton"][unit["interpretation_id"]]
        
        self.assertIn("Tesla", skeleton["evidence_3"][2])
        self.assertIn("Panasonic", skeleton["evidence_3"][2])

    def test_05_checklist_validation(self):
        print("\n[Test 05] Checklist Presence Validation")
        catalyst_events = [{
            "event_id": "evt_check_001",
            "tag": "KR_DART_DISCLOSURE",
            "title": "삼성전자 유상증자",
            "entities": ["005930"],
            "confidence": "A"
        }]
        
        results = self.assembler.assemble([], catalyst_events)
        unit = results["interpretation_units"][0]
        skeleton = results["narrative_skeleton"][unit["interpretation_id"]]
        
        self.assertTrue(len(skeleton["checklist_3"]) >= 3)
        self.assertIn("독립 소스", skeleton["checklist_3"][0])

    def test_06_e2e_integration_persistence(self):
        print("\n[Test 06] E2E Integration & Persistence")
        catalyst_events = [{
            "event_id": "evt_e2e_001",
            "tag": "US_SEC_FILING",
            "title": "E2E Integration Success",
            "entities": ["APP"],
            "confidence": "A"
        }]
        
        results = self.assembler.assemble([], catalyst_events)
        self.assembler.save(results)
        
        output_file = Path("data/decision_test/interpretation_units.json")
        self.assertTrue(output_file.exists())
        with open(output_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            modes = [u["mode"] for u in data]
            self.assertIn("HYPOTHESIS_JUMP", modes)

def run_verification():
    print("\n" + "="*60)
    print("📋 IS-96-5 HYPOTHESIS JUMP MODE VERIFICATION")
    print("="*60)
    
    suite = unittest.TestLoader().loadTestsFromTestCase(TestHypothesisJumpMode)
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
