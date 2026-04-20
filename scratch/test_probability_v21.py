import json
from src.analysis.decision_engine import DecisionEngine

# Case: Strong Bull (All Positive)
s1 = {
    "flow_direction": "inflow",
    "flow_confirmation": True,
    "price_strength": "strong_up",
    "trigger_event": "macro",
    "flow_consistency": 2
}
r1 = DecisionEngine.evaluate(s1)
print("--- Case 1: Strong Bull ---")
print(json.dumps(r1, indent=2))

# Case: Uncertain (Mixed)
s2 = {
    "flow_direction": "outflow",
    "flow_confirmation": False,
    "price_strength": "weak_up",
    "trigger_event": "none",
    "flow_consistency": 0
}
r2 = DecisionEngine.evaluate(s2)
print("\n--- Case 2: Mixed/Uncertain ---")
print(json.dumps(r2, indent=2))
