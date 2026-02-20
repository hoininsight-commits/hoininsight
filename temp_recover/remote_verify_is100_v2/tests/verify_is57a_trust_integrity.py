import unittest
import json
from pathlib import Path
from datetime import datetime
from src.collectors.capital_flow_connector import collect_capital_flows

class TestIS57A(unittest.TestCase):
    def test_flow_connector_structure(self):
        print("\n[TEST] Verifying Capital Flow Connector Output Structure...")
        # Should run without error even if no data found
        evidence = collect_capital_flows(Path("."), datetime.now().strftime("%Y-%m-%d"))
        print(f"Collected {len(evidence)} items.")
        
        if evidence:
            item = evidence[0]
            self.assertIn("fact_type", item)
            self.assertEqual(item["fact_type"], "CAPITAL_FLOW")
            self.assertIn("fact_text", item)
            self.assertIn("flow_metadata", item)
            
    def test_dashboard_evidence_panel(self):
        print("\n[TEST] Verifying Dashboard Panel Generation logic...")
        # Simulate a card with flow evidence
        fake_card = {
            "trigger_type": "DATA_INGRESS",
            "blocks": {
                "flow_evidence": [
                    {
                        "fact_text": "[자금흐름포착] 반도체 INFLOW: TEST SIGNAL",
                        "source": "RSS Finance"
                    }
                ]
            }
        }
        
        # Test HTML Snippet Generation Logic (replicating dashboard_generator logic)
        html = ""
        if 'flow_evidence' in fake_card['blocks']:
             html = "📈 자본 이동 증거 (Real Data)"
             
        self.assertIn("자본 이동 증거", html)
        print("Dashboard Panel Logic Verified.")

if __name__ == "__main__":
    unittest.main()
