"""
Verify IS-96-x Labor Shift Interpretation
"""
import sys
import json
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.decision.labor_shift_interpreter import LaborShiftInterpreter

def test_interpretation_execution():
    interpreter = LaborShiftInterpreter()
    interpreter.interpret()
    
    output_path = Path(__file__).parent.parent / "data" / "decision" / "interpretation_units.json"
    assert output_path.exists()
    
    with open(output_path) as f:
        data = json.load(f)
        assert isinstance(data, list)
        
        # Find target item
        item = next((u for u in data if u.get("interpretation_key") == "LABOR_MARKET_SHIFT"), None)
        assert item is not None, "LABOR_MARKET_SHIFT entry not found"
        
        assert "target_sector" in item
        assert "hypothesis_jump" in item
        assert "independent_sources_count" in item["hypothesis_jump"]

if __name__ == "__main__":
    try:
        test_interpretation_execution()
        print("IS-96-x Interpretation Verification: PASSED")
    except Exception as e:
        print(f"IS-96-x Interpretation Verification: FAILED - {e}")
        sys.exit(1)
