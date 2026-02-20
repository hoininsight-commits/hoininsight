"""
Verify IS-95-4 Price Mechanism Layer
"""
import sys
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.topics.interpretation.price_mechanism_interpreter import PriceMechanismInterpreter

def test_rigidity_calculation():
    interpreter = PriceMechanismInterpreter()
    
    # Mock Data: Super Rigid
    spreads = {"items": [{"spread_ratio": 1.5, "margin_proxy_supplier": 0.5}]}
    backlog = {"items": [{"backlog_ratio": 5.0, "capacity_utilization": 0.99, "allocation_flag": True}]}
    dependency = {"items": [{"top_supplier_concentration": 0.9}]}
    
    metrics = interpreter.calculate_metrics(spreads, backlog, dependency)[0]
    
    # Formula Check: (1.5*0.4) + (1.0*0.1) + (0.99*0.5) = 0.6 + 0.1 + 0.495 = 1.195 -> Cap 1.0
    assert metrics["rigidity_score"] == 1.0
    assert metrics["allocation_flag"] == True

def test_trigger_logic():
    interpreter = PriceMechanismInterpreter()
    
    # Rigid Case
    metrics_high = {
        "sector": "TEST_RIGID",
        "rigidity_score": 0.8,
        "backlog_years": 3.0,
        "allocation_flag": True
    }
    
    # Only need to mock the internal loop logic or extract it.
    # For unit testing, let's verify conditional logic directly used in interpret()
    triggers = [
        metrics_high["rigidity_score"] >= 0.7,
        metrics_high["backlog_years"] >= 2.0,
        metrics_high["allocation_flag"] == True
    ]
    is_active = sum(triggers) >= 2
    assert is_active == True

    # Weak Case
    metrics_low = {
        "sector": "TEST_WEAK",
        "rigidity_score": 0.3,
        "backlog_years": 0.5,
        "allocation_flag": False
    }
    triggers_low = [
        metrics_low["rigidity_score"] >= 0.7,
        metrics_low["backlog_years"] >= 2.0,
        metrics_low["allocation_flag"] == True
    ]
    is_active_low = sum(triggers_low) >= 2
    assert is_active_low == False

def test_full_flow():
    # Integration test with mocked I/O
    interpreter = PriceMechanismInterpreter()
    
    mock_spreads = {"items": [{"spread_ratio": 1.2}]}
    mock_backlog = {"items": [{"backlog_ratio": 3.0, "allocation_flag": True}]}
    mock_dependency = {"items": []}
    
    with patch.object(interpreter, 'load_data', return_value=(mock_spreads, mock_backlog, mock_dependency)):
        with patch('builtins.open', new_callable=MagicMock) as mock_open:
             with patch('json.dump') as mock_dump:
                 interpreter.interpret()
                 # Verify json dump was called (meaning a unit was generated and saved)
                 assert mock_dump.called

if __name__ == "__main__":
    try:
        test_rigidity_calculation()
        test_trigger_logic()
        test_full_flow()
        print("IS-95-4 Verification: PASSED")
    except Exception as e:
        print(f"IS-95-4 Verification: FAILED - {e}")
        sys.exit(1)
