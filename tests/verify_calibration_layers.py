import sys
from pathlib import Path

# Setup Project Root
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
sys.path.append(str(PROJECT_ROOT))

from src.ops.timing_calibration_layer import calibrate_timing
from src.impact.selection_calibration_layer import calibrate_selection, calibrate_allocation

def test_timing_calibration():
    print(">>> Testing Timing Calibration...")
    
    # Case 1: EMERGING + Low Momentum -> WATCH
    decision = {"action": {"value": "ENTER", "source": "raw"}}
    context = {"stage": "EMERGING", "momentum_score": 0.4}
    calibrated = calibrate_timing(decision.copy(), context)
    assert calibrated["action"]["value"] == "WATCH"
    print("✅ EMERGING + Low Momentum -> WATCH")

    # Case 2: EMERGING + High Momentum -> ENTER
    context = {"stage": "EMERGING", "momentum_score": 0.7}
    calibrated = calibrate_timing(decision.copy(), context)
    assert calibrated["action"]["value"] == "ENTER"
    print("✅ EMERGING + High Momentum -> ENTER")

    # Case 3: EXPANSION + Low Momentum -> HOLD
    context = {"stage": "EXPANSION", "momentum_score": 0.45}
    calibrated = calibrate_timing(decision.copy(), context)
    assert calibrated["action"]["value"] == "HOLD"
    print("✅ EXPANSION + Low Momentum -> HOLD")

def test_selection_calibration():
    print("\n>>> Testing Selection & Allocation Calibration...")
    
    mock_impact = [
        {"ticker": "AAPL", "directness": "direct", "evidence_basis": ["node1", "node2"]}, # score: 1.0 + 0.2 = 1.2
        {"ticker": "MSFT", "directness": "indirect", "evidence_basis": ["node1"]},        # score: 0.5 + 0.1 = 0.6
        {"ticker": "NVDA", "directness": "direct", "evidence_basis": ["node1", "node2", "node3"]}, # score: 1.0 + 0.3 = 1.3
        {"ticker": "TSLA", "directness": "indirect", "evidence_basis": []},              # score: 0.5 + 0.0 = 0.5
        {"ticker": "GOOG", "directness": "direct", "evidence_basis": ["node1"]}           # score: 1.0 + 0.1 = 1.1
    ]
    
    # 1. Selection (Top 3)
    selected = calibrate_selection(mock_impact)
    assert len(selected) == 3
    assert selected[0]["ticker"] == "NVDA"
    assert selected[1]["ticker"] == "AAPL"
    assert selected[2]["ticker"] == "GOOG"
    print("✅ Top 3 Selection verified (NVDA, AAPL, GOOG)")

    # 2. Allocation
    confidence = {"value": 0.8}
    allocated = calibrate_allocation(selected, confidence)
    assert allocated[0]["weight"] == round(0.8 * 1.3, 2)
    print(f"✅ Weight Allocation verified: {allocated[0]['ticker']} = {allocated[0]['weight']}")

if __name__ == "__main__":
    try:
        test_timing_calibration()
        test_selection_calibration()
        print("\n=== STEP-H-CORE VERIFICATION SUCCESS ===")
    except Exception as e:
        print(f"\n❌ VERIFICATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
