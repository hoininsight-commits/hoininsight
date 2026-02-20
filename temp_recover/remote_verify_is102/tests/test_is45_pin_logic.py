
import unittest
from pathlib import Path
from src.reporters.decision_dashboard import DecisionDashboard

class TestIS45PinLogic(unittest.TestCase):
    def setUp(self):
        self.dashboard = DecisionDashboard(Path("."))

    def test_is45_pin_selection_logic(self):
        """
        [IS-45] Verify Today's PIN selection rules.
        """
        # Card A: READY, Urgent=90, Locked=True (Ideal PIN)
        card_a = {
            "topic_id": "A", "title": "Topic A", "status": "READY", 
            "urgency_score": 90, "voice_consistent": True, "decay_state_ko": "활성"
        }
        # Card B: READY, Urgent=95, Locked=False (Fail Lock)
        card_b = {
            "topic_id": "B", "title": "Topic B", "status": "READY", 
            "urgency_score": 95, "voice_consistent": False, "decay_state_ko": "활성"
        }
        # Card C: SILENT, Urgent=80, Locked=True (Fail Status - original logic used READY/ACTIVE only)
        # Note: If status is SILENT, it's excluded in _get_pin_candidates (unless accepted as input?)
        # _get_pin_candidates checks if status in ["READY", "ACTIVE"]
        card_c = {
            "topic_id": "C", "title": "Topic C", "status": "SILENT", 
            "urgency_score": 80, "voice_consistent": True, "decay_state_ko": "침묵"
        }
        # Card D: ACTIVE, Urgent=85, Locked=True (Ideal PIN 2)
        card_d = {
            "topic_id": "D", "title": "Topic D", "status": "ACTIVE", 
            "urgency_score": 85, "voice_consistent": True, "decay_state_ko": "활성"
        }
        # Card E: READY, Urgent=10, Locked=True (Low score but eligible)
        card_e = {
            "topic_id": "E", "title": "Topic E", "status": "READY", 
            "urgency_score": 10, "voice_consistent": True, "decay_state_ko": "활성"
        }
        # Card F: READY, Urgent=100, Locked=True, Decayed=Silent (Fail Decay)
        card_f = {
            "topic_id": "F", "title": "Topic F", "status": "READY", 
            "urgency_score": 100, "voice_consistent": True, "decay_state_ko": "침묵"
        }

        cards = [card_a, card_b, card_c, card_d, card_e, card_f]
        
        pins = self.dashboard._get_pin_candidates(cards)
        
        # Expected: A, D, E
        # Order: A (90), D (85), E (10)
        # B failed lock
        # C failed status
        # F failed decay
        
        self.assertEqual(len(pins), 3)
        self.assertEqual(pins[0]["topic_id"], "A")
        self.assertEqual(pins[1]["topic_id"], "D")
        self.assertEqual(pins[2]["topic_id"], "E")

if __name__ == '__main__':
    unittest.main()
