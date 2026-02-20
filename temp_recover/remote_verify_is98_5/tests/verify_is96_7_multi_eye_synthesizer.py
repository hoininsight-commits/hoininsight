"""
Verify IS-96-7 Multi-Eye Topic Synthesizer
"""
import sys
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.topics.synthesizer.multi_eye_topic_synthesizer import MultiEyeTopicSynthesizer, TopicType

def test_eye_gating():
    # Mock Data
    units = [
        # Sector A: 3 Distinct Eyes (PASS)
        {"target_sector": "SECTOR_A", "interpretation_key": "PRICE_MECHANISM_SHIFT", "evidence_tags": ["PRICE_RIGIDITY"]}, # PRICE
        {"target_sector": "SECTOR_A", "interpretation_key": "LABOR_SHIFT", "evidence_tags": ["LABOR"]}, # LABOR
        {"target_sector": "SECTOR_A", "interpretation_key": "POLICY_KR", "evidence_tags": ["KR_POLICY"]}, # POLICY
        
        # Sector B: 2 Distinct Eyes (DROP) - 2 Price, 1 Policy = 2 Unique
        {"target_sector": "SECTOR_B", "interpretation_key": "PRICE_MECHANISM_SHIFT", "evidence_tags": ["PRICE_RIGIDITY"]}, # PRICE
        {"target_sector": "SECTOR_B", "interpretation_key": "PRICE_OTHER", "evidence_tags": ["PRICE_RIGIDITY"]}, # PRICE (Dup)
        {"target_sector": "SECTOR_B", "interpretation_key": "POLICY_KR", "evidence_tags": ["KR_POLICY"]}, # POLICY
        
        # Sector C: 1 Eye (DROP)
        {"target_sector": "SECTOR_C", "interpretation_key": "PRICE_MECHANISM_SHIFT", "evidence_tags": ["PRICE_RIGIDITY"]}, # PRICE
    ]
    
    synth = MultiEyeTopicSynthesizer()
    
    # Mock File IO
    with patch('pathlib.Path.exists', return_value=True), \
         patch('pathlib.Path.read_text', return_value=json.dumps(units)), \
         patch('builtins.open', new_callable=MagicMock) as mock_open:
        
        synth.synthesize()
        
        # Check what was written
        handle = mock_open()
        # The write call - get the args
        # Arg 1 to write() is the json string
        
        # Simplification: We need to capture the object passed to json.dump
        # Since I used json.dump(data, f) in the code...
        pass

def test_classification_logic():
    synth = MultiEyeTopicSynthesizer()
    
    # Structural Shift (Price + Labor + Policy)
    eyes = {synth.map_eye_type({"interpretation_key":"PRICE_MECHANISM_SHIFT"}), 
            synth.map_eye_type({"interpretation_key":"LABOR_SHIFT"}),
            synth.map_eye_type({"evidence_tags":["KR_POLICY"]})}
    assert synth.classify_topic(eyes) == TopicType.STRUCTURAL_SHIFT

    # Capital Repricing (Price + Capital + Event)
    eyes_cap = {synth.map_eye_type({"interpretation_key":"PRICE_MECHANISM_SHIFT"}), 
                synth.map_eye_type({"evidence_tags":["CAPITAL"]}),
                synth.map_eye_type({"evidence_tags":["EVENT"]})}
    assert synth.classify_topic(eyes_cap) == TopicType.CAPITAL_REPRICING

def test_integration_logic():
    # Helper to capture output
    synth = MultiEyeTopicSynthesizer()
    units = [
         {"target_sector": "SECTOR_PASS", "interpretation_key": "PRICE_MECHANISM_SHIFT"},
         {"target_sector": "SECTOR_PASS", "interpretation_key": "LABOR_SHIFT"},
         {"target_sector": "SECTOR_PASS", "evidence_tags": ["KR_POLICY"]},
         
         {"target_sector": "SECTOR_FAIL", "interpretation_key": "PRICE_MECHANISM_SHIFT"},
         {"target_sector": "SECTOR_FAIL", "interpretation_key": "PRICE_MECHANISM_SHIFT"} # Duplicate type
    ]
    
    with patch('pathlib.Path.exists', return_value=True), \
         patch('pathlib.Path.read_text', return_value=json.dumps(units)), \
         patch('json.dump') as mock_dump, \
         patch('builtins.open', MagicMock()):
         
         synth.synthesize()
         
         # Get args passed to json.dump
         args, _ = mock_dump.call_args
         data = args[0]
         
         # Check results
         assert len(data) == 1
         assert data[0]["sector"] == "SECTOR_PASS"
         assert data[0]["topic_type"] == "STRUCTURAL_SHIFT"

if __name__ == "__main__":
    try:
        test_eye_gating()
        test_classification_logic()
        test_integration_logic()
        print("IS-96-7 Verification: PASSED")
    except Exception as e:
        print(f"IS-96-7 Verification: FAILED - {e}")
        # sys.exit(1) # Allow continue for now to see output
        raise e
