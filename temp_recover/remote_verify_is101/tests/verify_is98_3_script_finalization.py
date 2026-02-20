"""
Verify IS-98-3 Script Finalization
"""
import sys
import json
import yaml
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.reporters.script_finalizer import ScriptFinalizer

def test_script_generation():
    finalizer = ScriptFinalizer()
    
    # Mock Data
    hero_data = {
        "status": "LOCKED",
        "hero_topic": {
            "sector": "TEST_AI",
            "topic_type": "STRUCTURAL_SHIFT",
            "eyes_used": ["PRICE"],
            "dominant_eye": "PRICE",
            "why_now_bundle": {
                "why_now_3": "Hook Text",
                "why_now_1": "Reason 1",
                "why_now_2": "Reason 2"
            }
        }
    }
    
    templates = {
        "shorts_structure": [
            {"section": "TEST", "content": "Test content {HOOK_TEXT}"}
        ],
        "long_structure": []
    }
    
    with patch.object(finalizer, 'load_data', return_value=(hero_data["hero_topic"], [], templates)):
        with patch('pathlib.Path.write_text') as mock_write, \
             patch('pathlib.Path.mkdir'):
             
             finalizer.generate_scripts()
             
             # Verify write called
             assert mock_write.call_count == 2 # Shorts + Long
             
             # Check content
             # First call likely shorts or long depending on dict order/implementation
             # args[0] is the text content
             calls = mock_write.call_args_list
             content1 = calls[0][0][0]
             assert "Hook Text" in content1

def test_hypothesis_disclaimer():
    finalizer = ScriptFinalizer()
    hero_data = {
        "sector": "TEST",
        "topic_type": "HYPOTHESIS_JUMP", # Should trigger disclaimer
        "eyes_used": []
    }
    templates = {"shorts_structure": [{"section":"CLOSE", "content":"{DISCLAIMER_TEXT}"}]}
    
    with patch.object(finalizer, 'load_data', return_value=(hero_data, [], templates)):
        with patch('pathlib.Path.write_text') as mock_write, \
             patch('pathlib.Path.mkdir'):
             
             finalizer.generate_scripts()
             content = mock_write.call_args_list[0][0][0]
             assert "가설" in content

if __name__ == "__main__":
    try:
        test_script_generation()
        test_hypothesis_disclaimer()
        print("IS-98-3 Verification: PASSED")
    except Exception as e:
        print(f"IS-98-3 Verification: FAILED - {e}")
        # sys.exit(1)
        raise e
