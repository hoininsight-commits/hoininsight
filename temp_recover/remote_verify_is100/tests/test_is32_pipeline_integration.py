import unittest
from pathlib import Path
from src.ops.source_diversity_auditor import SourceDiversityAuditor

class TestIS32Integration(unittest.TestCase):
    def test_diversity_demotion_logic(self):
        auditor = SourceDiversityAuditor(Path("."))
        
        # 1. Mock a trigger topic that should be READY
        topic = {
            "topic_id": "T3",
            "trigger_type": "POLICY",
            "status": "READY",
            "candidate_id": "E3"
        }
        
        # 2. Mock events_index where E3 has only one cluster (even if 2 articles)
        events_index = {
            "E3": {
                "event_id": "E3",
                "source_type": "NEWS",
                "publisher": "Reuters",
                "title": "New Policy Announced",
                "raw_content": "Reuters reports new policy."
            }
        }
        
        processed = auditor.audit_topics([topic], events_index)
        
        # 3. Assert demotion (should be HOLD due to lack of clusters/families)
        self.assertEqual(processed[0]["status"], "HOLD")
        self.assertEqual(processed[0]["diversity_verdict"], "HOLD")
        self.assertEqual(processed[0]["diversity_reason_code"], "WIRE_CHAIN_DUPLICATION")

    def test_diversity_pass_logic(self):
        auditor = SourceDiversityAuditor(Path("."))
        
        topic = {
            "topic_id": "T4",
            "trigger_type": "POLICY",
            "status": "READY",
            "candidate_id": "E4",
            "source_candidates": ["E4", "E5"]
        }
        
        events_index = {
            "E4": {
                "event_id": "E4",
                "source_type": "OFFICIAL_RELEASE",
                "publisher": "Gov",
                "title": "Official Release",
                "url": "https://gov.site/1"
            },
            "E5": {
                "event_id": "E5",
                "source_type": "NEWS",
                "publisher": "Reuters",
                "title": "Major Move",
                "url": "https://reuters.com/1"
            }
        }
        
        processed = auditor.audit_topics([topic], events_index)
        
        # 3. Assert PASS (2 clusters, 2 families)
        self.assertEqual(processed[0]["status"], "READY")
        self.assertEqual(processed[0]["diversity_verdict"], "PASS")

if __name__ == '__main__':
    unittest.main()
