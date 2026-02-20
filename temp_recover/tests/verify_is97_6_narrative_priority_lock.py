"""
Verify IS-97-6 Narrative Priority Lock
"""
import sys
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.topics.lock.narrative_priority_lock import NarrativePriorityLock

def test_hero_selection():
    lock = NarrativePriorityLock()
    
    # Candidate A: High Priority (Structural + Power bottleneck)
    c1 = {
        "topic_id": "T1", 
        "sector": "POWER_GRID", 
        "topic_type": "STRUCTURAL_SHIFT", 
        "eyes_used": ["PRICE", "POLICY", "LABOR"],
        "dominant_eye": "PRICE",
        "why_now_bundle": {"why_now_1": "Test", "why_now_2": "Test", "why_now_3": "Test"}
    }
    # Candidate B: Lower Priority (Capital Repricing)
    c2 = {
        "topic_id": "T2", 
        "sector": "CONSUMER", 
        "topic_type": "CAPITAL_REPRICING",
        "eyes_used": ["PRICE", "CAPITAL", "EVENT"],
        "dominant_eye": "PRICE",
        "why_now_bundle": {"why_now_1": "Test", "why_now_2": "Test", "why_now_3": "Test"}
    }
    
    with patch.object(lock, 'load_data', return_value=([c1, c2], [], {})):
        with patch('json.dump') as mock_dump, \
             patch('builtins.open', MagicMock()):
             
             lock.process()
             
             # Check arguments to json.dump
             # First call is hero_topic_lock.json
             args, _ = mock_dump.call_args_list[0]
             hero_out = args[0]
             
             assert hero_out["status"] == "LOCKED"
             assert hero_out["hero_topic"]["topic_id"] == "T1"
             assert hero_out["hero_topic"]["priority_score"]["total"] > 0.5

def test_no_hero():
    lock = NarrativePriorityLock()
    with patch.object(lock, 'load_data', return_value=([], [], {})): # No candidates
        with patch('json.dump') as mock_dump, \
             patch('builtins.open', MagicMock()):
             
             lock.process()
             
             args, _ = mock_dump.call_args_list[0]
             hero_out = args[0]
             
             assert hero_out["status"] == "NO_HERO_TODAY"

if __name__ == "__main__":
    try:
        test_hero_selection()
        test_no_hero()
        print("IS-97-6 Verification: PASSED")
    except Exception as e:
        print(f"IS-97-6 Verification: FAILED - {e}")
        # sys.exit(1)
        raise e
