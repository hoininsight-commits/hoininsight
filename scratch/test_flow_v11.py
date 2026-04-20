import json
from pathlib import Path
from src.agents.extensions.flow_overlay import FlowOverlay

base_dir = Path("/Users/jihopa/Antigravity/hoininsight")
flow_dir = base_dir / "data/flow"
overlay = FlowOverlay(base_dir)

# Mock Flow: Inflow
(flow_dir / "foreign_flow.json").write_text(json.dumps({"trend_3d": "inflow"}))

# 1. CONFIRMED_UPTREND (Price Up + Inflow)
s1 = {"topic": "S&P500 상승", "strength": 8.0, "extended_strength": 8.0}
r1 = overlay.apply(s1)
print(f"--- Case 1: UPTREND ---")
print(f"State: {r1['flow_state']}")
print(f"Strength: {r1['extended_strength']}") # Expected: 8 + 3 = 11 -> 10

# 2. ACCUMULATION (Price Down + Inflow)
s2 = {"topic": "나스닥 하락", "strength": 8.0, "extended_strength": 8.0}
r2 = overlay.apply(s2)
print(f"\n--- Case 2: ACCUMULATION ---")
print(f"State: {r2['flow_state']}")
print(f"Strength: {r2['extended_strength']}") # Expected: 8 + 2 = 10

# Mock Flow: Outflow
(flow_dir / "foreign_flow.json").write_text(json.dumps({"trend_3d": "outflow"}))
(flow_dir / "etf_flow.json").write_text(json.dumps({"KOSPI_ETF": {"trend": "outflow"}}))

# 3. DISTRIBUTION (Price Up + Outflow)
s3 = {"topic": "코스피 상승", "strength": 8.0, "extended_strength": 8.0}
r3 = overlay.apply(s3)
print(f"\n--- Case 3: DISTRIBUTION ---")
print(f"State: {r3['flow_state']}")
print(f"Strength: {r3['extended_strength']}") # Expected: 8 - 3 = 5

