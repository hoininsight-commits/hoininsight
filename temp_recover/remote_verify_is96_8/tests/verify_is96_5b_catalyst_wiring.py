import os
import json
import unittest
import yaml
from pathlib import Path
from src.collectors.catalyst_event_collector import CatalystEventCollector
from src.decision.assembler import DecisionAssembler

class TestCatalystWiring(unittest.TestCase):
    def setUp(self):
        self.project_root = Path(".")
        self.test_output_dir = self.project_root / "data/decision_test"
        self.catalyst_json = self.project_root / "data/ops/catalyst_events.json"
        self.manual_seed = self.project_root / "data/ops/manual_catalyst_events.yml"
        
        # Ensure clean state for test
        if self.test_output_dir.exists():
            import shutil
            shutil.rmtree(self.test_output_dir)

    def test_01_catalyst_collection_logic(self):
        print("\n[Test 01] Catalyst Collection & Entity Mapping")
        # Pre-populate manual seed if not exists
        seed_data = [{
            "event_id": "test_spacex_001",
            "title": "SpaceX and xAI strategic merger confirmed",
            "trust_score": 0.9,
            "tag": "US_MA_RUMOR"
        }]
        with open(self.manual_seed, "w", encoding="utf-8") as f:
            yaml.dump(seed_data, f)
            
        collector = CatalystEventCollector()
        events = collector.collect()
        
        self.assertTrue(len(events) >= 1)
        self.assertIn("SpaceX", events[0]["entities"])
        self.assertIn("xAI", events[0]["entities"])
        self.assertEqual(events[0]["confidence"], "A")

    def test_02_wiring_to_interpretation_units(self):
        print("\n[Test 02] Wiring to Interpretation Units (HYPOTHESIS_JUMP)")
        # 1. Run collector
        collector = CatalystEventCollector()
        events = collector.collect()
        
        # 2. Run assembler
        assembler = DecisionAssembler(output_dir=str(self.test_output_dir))
        results = assembler.assemble([], catalyst_events=events)
        
        units = results["interpretation_units"]
        self.assertTrue(any(u["mode"] == "HYPOTHESIS_JUMP" for u in units))
        
        # Check if SpaceX event produced a unit
        hyp_units = [u for u in units if u["mode"] == "HYPOTHESIS_JUMP"]
        self.assertIn("SpaceX", hyp_units[0]["reasoning_chain"]["trigger_event"])

    def test_03_speakability_routing_by_trust(self):
        print("\n[Test 03] Speakability Routing by Trust Score")
        # Create a low trust event
        low_trust_events = [{
            "event_id": "test_rumor_low",
            "title": "Unverified rumor about Apple buying Bitcoin",
            "trust_score": 0.3,
            "tag": "US_MA_RUMOR",
            "confidence": "C" 
        }]
        
        assembler = DecisionAssembler(output_dir=str(self.test_output_dir))
        results = assembler.assemble([], catalyst_events=low_trust_events)
        
        unit_id = results["interpretation_units"][0]["interpretation_id"]
        decision = results["speakability_decision"][unit_id]
        
        # Trust 0.3 should be HOLD in our SpeakabilityGate (mapped from trust C)
        self.assertEqual(decision["speakability_flag"], "HOLD")
        self.assertIn("Rumor/Catalyst requires verification", decision["speakability_reasons"][0])

def run_verification():
    print("\n" + "="*60)
    print("📋 IS-96-5b CATALYST WIRING VERIFICATION")
    print("="*60)
    
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCatalystWiring)
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
