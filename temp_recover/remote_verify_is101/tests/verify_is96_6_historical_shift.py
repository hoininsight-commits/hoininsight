"""
Verify IS-96-6 Historical Shift Framing
"""
import sys
import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.topics.interpretation.historical_shift_framing import HistoricalShiftFramer
from src.topics.narrator.narrative_skeleton import NarrativeSkeletonBuilder

def test_framer_trigger_conditions():
    framer = HistoricalShiftFramer()
    
    # Case 1: Low Score -> No Trigger
    unit_low = {"interpretation_key": "LABOR_MARKET_SHIFT", "confidence_score": 0.5}
    assert framer.check_conditions(unit_low) == False
    
    # Case 2: High Score -> Trigger
    unit_high = {"interpretation_key": "LABOR_MARKET_SHIFT", "confidence_score": 0.85}
    assert framer.check_conditions(unit_high) == True
    
    # Case 3: Hypothesis Jump Ready -> Trigger
    unit_hyp = {
        "interpretation_key": "LABOR_MARKET_SHIFT", 
        "confidence_score": 0.5,
        "hypothesis_jump": {"status": "READY"}
    }
    assert framer.check_conditions(unit_hyp) == True
    
    # Case 4: Invalid Key -> No Trigger
    unit_invalid = {"interpretation_key": "UNKNOWN_SHIFT", "confidence_score": 0.9}
    assert framer.check_conditions(unit_invalid) == False

def test_framer_generation():
    framer = HistoricalShiftFramer()
    unit = {
        "target_sector": "TEST_SECTOR",
        "interpretation_key": "AI_INDUSTRIALIZATION",
        "confidence_score": 0.9
    }
    
    frame = framer.generate_frame(unit)
    assert frame is not None
    assert frame["shift_type"] == "INDUSTRIAL_REVOLUTION_PHASE_SHIFT"
    assert "historical_claim" in frame
    assert "what_changed" in frame

def test_narrative_integration():
    # Mock file existence for integration test
    mock_frame = {
        "interpretation_key": "LABOR_MARKET_SHIFT",
        "shift_type": "MOCK_SHIFT",
        "historical_claim": "Mock Claim",
        "what_changed": ["A", "B"],
        "what_breaks_next": ["C"]
    }
    
    with patch("pathlib.Path.exists", return_value=True), \
         patch("pathlib.Path.read_text", return_value=json.dumps(mock_frame)):
        
        builder = NarrativeSkeletonBuilder()
        unit = {"interpretation_key": "LABOR_MARKET_SHIFT", "structural_narrative": "Base Narrative"}
        
        skeleton = builder.build(unit, {"speakability_flag": "READY"})
        
        # Verify Injection
        assert "[MOCK_SHIFT] Mock Claim" in skeleton["hook"]
        assert "era_declaration_block" in skeleton
        assert skeleton["era_declaration_block"]["shift_type"] == "MOCK_SHIFT"

if __name__ == "__main__":
    try:
        test_framer_trigger_conditions()
        test_framer_generation()
        test_narrative_integration()
        print("IS-96-6 Verification: PASSED")
    except Exception as e:
        print(f"IS-96-6 Verification: FAILED - {e}")
        sys.exit(1)
