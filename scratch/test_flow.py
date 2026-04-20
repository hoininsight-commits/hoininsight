import json
from pathlib import Path
from src.agents.extensions.flow_overlay import FlowOverlay

base_dir = Path("/Users/jihopa/Antigravity/hoininsight")
flow_dir = base_dir / "data/flow"

# 1. Strong Case
(flow_dir / "foreign_flow.json").write_text(json.dumps({"trend_3d": "inflow"}))
overlay = FlowOverlay(base_dir)
s1 = {"topic": "Positive", "strength": 8.0, "extended_strength": 8.5}
print("--- Case: Strong Flow ---")
print(json.dumps(overlay.apply(s1), indent=2, ensure_ascii=False))

# 2. Weak Case (Outflow)
(flow_dir / "foreign_flow.json").write_text(json.dumps({"trend_3d": "outflow"}))
(flow_dir / "etf_flow.json").write_text(json.dumps({"KOSPI_ETF": {"trend": "outflow"}}))
s2 = {"topic": "Negative", "strength": 8.0, "extended_strength": 8.5}
print("\n--- Case: Weak Flow ---")
print(json.dumps(overlay.apply(s2), indent=2, ensure_ascii=False))
