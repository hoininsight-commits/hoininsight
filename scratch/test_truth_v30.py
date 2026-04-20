import json
from pathlib import Path
from src.analysis.truth_engine import TruthEngine
from src.analysis.decision_engine import DecisionEngine

base_dir = Path("/Users/jihopa/Antigravity/hoininsight")

# 1. Instantiate TruthEngine to ensure files exist
te = TruthEngine(base_dir)

# 2. Simulate Consecutive Failures
perf_file = base_dir / "data/history/performance_state.json"
state = json.loads(perf_file.read_text())
state["consecutive_failures"] = 5
perf_file.write_text(json.dumps(state))

# 3. Evaluate with Penalty
signal = {
    "flow_direction": "inflow",
    "flow_confirmation": True,
    "price_strength": "strong_up",
    "trigger_event": "macro",
    "flow_consistency": 2
}
# TruthEngine 연동된 DecisionEngine 호출
res = DecisionEngine.evaluate(signal, base_dir)

print("--- Decision with Failure Penalty (CF: 0.5) ---")
print(f"Calibration Factor: {res['calibration_applied']}")
print(f"Original Bull Prob: {res['bull_probability']}")
print(f"Final Calibrated Confidence: {res['confidence']}")
print(f"Action: {res['action']}")
