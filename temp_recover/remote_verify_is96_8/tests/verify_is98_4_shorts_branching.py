"""
Verify IS-98-4 Shorts Branching Layer
"""
import sys
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.reporters.shorts_brancher import ShortsBrancher

def test_angle_generation():
    brancher = ShortsBrancher()
    
    hero = {
        "sector": "AI_POWER",
        "topic_type": "STRUCTURAL_SHIFT",
        "why_now_bundle": {"why_now_1": "Test 1", "why_now_2": "Test 2", "why_now_3": "Test 3"}
    }
    
    # Mock Data Loads
    with patch.object(brancher, 'load_data', return_value=(hero, [], [])):
        with patch('pathlib.Path.write_text') as mock_write, \
             patch('pathlib.Path.mkdir'):
             
             brancher.run()
             
             # Should generate 4 files
             assert mock_write.call_count == 4
             
             # Check distinctness of first two
             calls = mock_write.call_args_list
             s1 = calls[0][0][0]
             s2 = calls[1][0][0]
             
             # Hooks should be different
             assert "[거시 구조]" in s1
             assert "[병목 돌파]" in s2
             assert brancher.calculate_overlap(s1, s2) < 0.6 # Allow for template commonality

def test_hypothesis_disclaimer():
    brancher = ShortsBrancher()
    hero = {
        "sector": "TEST",
        "topic_type": "HYPOTHESIS_JUMP",
        "why_now_bundle": {}
    }
    with patch.object(brancher, 'load_data', return_value=(hero, [], [])):
        with patch('pathlib.Path.write_text') as mock_write, \
             patch('pathlib.Path.mkdir'):
             
             brancher.run()
             s1 = mock_write.call_args_list[0][0][0]
             assert "가설" in s1

if __name__ == "__main__":
    try:
        test_angle_generation()
        test_hypothesis_disclaimer()
        print("IS-98-4 Verification: PASSED")
    except Exception as e:
        print(f"IS-98-4 Verification: FAILED - {e}")
        # sys.exit(1)
        raise e
