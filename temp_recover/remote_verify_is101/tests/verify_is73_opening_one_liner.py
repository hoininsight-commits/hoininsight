
import sys
import unittest
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.issuesignal.opening_one_liner import synthesize_opening_one_liner

class TestOpeningOneLiner(unittest.TestCase):
    
    def test_failure_cases(self):
        """Test failure based on decision tree first failure node"""
        print("\n[TEST] Testing Failure Cases...")
        
        # 1. HF Fail
        tree = [
            {"name": "데이터 수집", "status": "PASS"},
            {"name": "팩트 체크", "status": "FAIL"}
        ]
        res = synthesize_opening_one_liner(None, tree)
        print(f"  - HF Fail: {res}")
        self.assertIn("하드 팩트가 부족", res)
        
        # 2. WhyNow Fail
        tree = [
            {"name": "데이터 수집", "status": "PASS"},
            {"name": "팩트 체크", "status": "PASS"},
            {"name": "시점 분석", "status": "FAIL"}
        ]
        res = synthesize_opening_one_liner(None, tree)
        print(f"  - WN Fail: {res}")
        self.assertIn("시점(WHY-NOW) 조건이 충족되지", res)

    def test_success_existing_whynow(self):
        """Test success case with existing why_now field"""
        print("\n[TEST] Testing Success (Existing WhyNow)...")
        top_topic = {
            "authority_sentence": "지금 금리 인하가 확정되어 부동산 유동성이 증가한다.",
            "why_now": "지금 금리 인하가 확정되어 부동산 유동성이 증가한다.",
            "actor": "건설사"
        }
        tree = [{"status": "PASS"}]
        res = synthesize_opening_one_liner(top_topic, tree)
        print(f"  - Result: {res}")
        self.assertEqual(res, top_topic['authority_sentence'])

    def test_tone_lock_filtering(self):
        """Test filtering of speculative words"""
        print("\n[TEST] Testing Tone Lock (Banned Words)...")
        top_topic = {
            "why_now": "내일 주가가 오를 가능성이 높다.", # Banned "가능성"
            "actor": "반도체",
            "tickers": [{"ticker": "005930"}]
        }
        tree = [{"status": "PASS"}]
        res = synthesize_opening_one_liner(top_topic, tree)
        print(f"  - Input: {top_topic['why_now']}")
        print(f"  - Output: {res}")
        
        # Should not contain "가능성"
        self.assertNotIn("가능성", res)
        # Should be fallback
        self.assertIn("반도체와 관련된 팩트가 확정", res)

    def test_fallback_derivation(self):
        """Test derivation when no sentence exists"""
        print("\n[TEST] Testing Fallback Derivation...")
        top_topic = {
            "actor": "해운사",
            "why_now": None
        }
        tree = [{"status": "PASS"}]
        res = synthesize_opening_one_liner(top_topic, tree)
        print(f"  - Derived: {res}")
        self.assertIn("해운사에 대한 확실한 변화가 감지", res)

if __name__ == '__main__':
    unittest.main()
