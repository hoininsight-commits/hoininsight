import unittest
from src.issuesignal.bottleneck_ranker import BottleneckRanker

class TestIS60BottleneckRanker(unittest.TestCase):
    
    def test_protagonist_selection(self):
        print("\n[TEST] Verifying Bottleneck Protagonist Selection...")
        
        # Mock Facts
        facts = [
            # 1. Generic Agreement (Score: 50 + 10 = 60) -> Should fail
            {
                "fact_text": "[Company A] Agreement signed",
                "details": {"action_type": "AGREEMENT", "raw_summary": "Just a normal agreement."}
            },
            # 2. Exclusive Material Agreement (Score: 50 + 10 + 15 = 75) -> Should pass
            {
                "fact_text": "[Company B] Material Agreement",
                "details": {"action_type": "AGREEMENT", "raw_summary": "Entry into an exclusive supply agreement."}
            },
            # 3. Acquisition (Score: 50 + 20 = 70) -> Borderline (Needs keyword to be safe, or just hit 70 cutoff)
            # Ranker Cutoff is 75? Let's check code. Code says MIN_SCORE_THRESHOLD = 75.
            # So 70 is fail.
            {
                "fact_text": "[Company C] Acquisition Complete",
                "details": {"action_type": "ACQUISITION", "raw_summary": "Acquired target assets."}
            },
            # 4. Global Acquisition (Score: 50 + 20 + 10 = 80) -> Should pass
            {
                "fact_text": "[Company D] Global Acquisition",
                "details": {"action_type": "ACQUISITION", "raw_summary": "Acquired worldwide intellectual property assets."}
            }
        ]
        
        result = BottleneckRanker.rank_protagonists(facts)
        protagonists = result['protagonists']
        supporting = result['supporting']
        
        print(f"Protagonists ({len(protagonists)}):")
        for p in protagonists:
            print(f" - {p['fact_text']} (Score: {p['bottleneck_score']}) Reason: {p['bottleneck_reason']}")
            
        self.assertEqual(len(protagonists), 2)
        self.assertEqual(protagonists[0]['fact_text'], "[Company D] Global Acquisition") # Score 80
        self.assertEqual(protagonists[1]['fact_text'], "[Company B] Material Agreement") # Score 75
        
        self.assertEqual(len(supporting), 2)
        print("[PASS] Protagonist Logic Verified.")

    def test_debt_penalty(self):
        print("\n[TEST] Verifying Debt Penalty...")
        fact = [{
            "fact_text": "[Company Debt]",
            "details": {"action_type": "FINANCIAL_OBLIGATION", "raw_summary": "Issued Senior Notes."}
        }]
        result = BottleneckRanker.rank_protagonists(fact)
        # Score: 50 - 10 = 40. Fail.
        self.assertEqual(len(result['protagonists']), 0)
        self.assertEqual(result['supporting'][0]['bottleneck_score'], 40)
        print("[PASS] Penalty Logic Verified.")

if __name__ == '__main__':
    unittest.main()
