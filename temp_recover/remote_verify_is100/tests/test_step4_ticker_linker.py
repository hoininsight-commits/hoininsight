import unittest
from unittest.mock import patch, MagicMock
from src.tickers.ticker_linker_engine import TickerLinkerEngine
from src.tickers.company_map_registry import CandidateCompany, Step3BottleneckSignal, BOTTLENECK_SLOT_MAP

class TestStep4TickerLinker(unittest.TestCase):
    
    def setUp(self):
        self.engine = TickerLinkerEngine()
        
    def test_registry_lookup_fail(self):
        signal = Step3BottleneckSignal("T", "C", "INVALID_SLOT")
        res = self.engine.run(signal)
        self.assertEqual(res["status"], "REJECT")
        self.assertIn("No candidates", res["reject_reason"])

    @patch("src.tickers.ticker_linker_engine.BOTTLENECK_SLOT_MAP")
    def test_reality_fail(self, mock_map):
        c1 = CandidateCompany("FailCo", [], "R", [], revenue_exists=False, delivery_record=False) # 2 fails
        mock_map.get.return_value = [c1]
        
        signal = Step3BottleneckSignal("T", "C", "TEST_SLOT")
        res = self.engine.run(signal)
        self.assertEqual(res["status"], "REJECT")
        self.assertIn("Reality Fail", res["reject_reason"])

    @patch("src.tickers.ticker_linker_engine.BOTTLENECK_SLOT_MAP")
    def test_guardrail_fail_count(self, mock_map):
        c1 = CandidateCompany("OneFactCo", [], "R", ["FACT_1"]) # < 2 facts
        mock_map.get.return_value = [c1]
        
        signal = Step3BottleneckSignal("T", "C", "TEST_SLOT")
        res = self.engine.run(signal)
        self.assertEqual(res["status"], "REJECT")
        self.assertIn("Guardrail", res["reject_reason"])

    @patch("src.tickers.ticker_linker_engine.BOTTLENECK_SLOT_MAP")
    def test_guardrail_fail_pr(self, mock_map):
        c1 = CandidateCompany("PRCo", [], "R", ["FACT_1", "FACT_PR_ONLY_ROADMAP"]) # PR token
        mock_map.get.return_value = [c1]
        
        signal = Step3BottleneckSignal("T", "C", "TEST_SLOT")
        res = self.engine.run(signal)
        self.assertEqual(res["status"], "REJECT")
        self.assertIn("PR_ONLY Detected", res["reject_reason"])

    @patch("src.tickers.ticker_linker_engine.BOTTLENECK_SLOT_MAP")
    def test_scoring_success_collapse(self, mock_map):
        # 4 Candidates passed
        # Top 3 are strong, 4th is weak
        c1 = CandidateCompany("Strong1", [], "R", ["F1","F2"], market_share_proxy=10)
        c2 = CandidateCompany("Strong2", [], "R", ["F1","F2"], market_share_proxy=9)
        c3 = CandidateCompany("Strong3", [], "R", ["F1","F2"], market_share_proxy=8)
        c4 = CandidateCompany("Weak4", [], "R", ["F1","F2"], market_share_proxy=3) # < 0.7 * 8
        
        mock_map.get.return_value = [c1, c2, c3, c4]
        
        signal = Step3BottleneckSignal("T", "C", "TEST_SLOT")
        res = self.engine.run(signal)
        self.assertEqual(res["status"], "LOCKED")
        self.assertEqual(len(res["tickers"]), 3)
        names = [t["name"] for t in res["tickers"]]
        self.assertNotIn("Weak4", names)

    @patch("src.tickers.ticker_linker_engine.BOTTLENECK_SLOT_MAP")
    def test_scoring_reject_fragmented(self, mock_map):
        # 4 Candidates close in score
        c1 = CandidateCompany("C1", [], "R", ["F1","F2"], market_share_proxy=8)
        c2 = CandidateCompany("C2", [], "R", ["F1","F2"], market_share_proxy=8)
        c3 = CandidateCompany("C3", [], "R", ["F1","F2"], market_share_proxy=8)
        c4 = CandidateCompany("C4", [], "R", ["F1","F2"], market_share_proxy=7) # Close to 8
        
        mock_map.get.return_value = [c1, c2, c3, c4]
        
        signal = Step3BottleneckSignal("T", "C", "TEST_SLOT")
        res = self.engine.run(signal)
        self.assertEqual(res["status"], "REJECT")
        self.assertIn("Fragmented Market", res["reject_reason"])

if __name__ == "__main__":
    unittest.main()
