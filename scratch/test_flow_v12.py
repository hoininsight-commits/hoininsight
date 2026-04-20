import json
from pathlib import Path
from src.agents.extensions.flow_overlay import FlowOverlay

base_dir = Path("/Users/jihopa/Antigravity/hoininsight")
flow_dir = base_dir / "data/flow"
overlay = FlowOverlay(base_dir)

# Mock Data
all_data = {
    "market": {
        "data": {
            "multi_period_stats": {
                "sp500": {"z_score_20d": 2.0, "5d_change_pct": 3.0}
            }
        }
    }
}

# Case: STRONG_UP + STRONG_INFLOW (Consistency +2)
(flow_dir / "foreign_flow.json").write_text(json.dumps({"trend_3d": "inflow"}))
(flow_dir / "etf_flow.json").write_text(json.dumps({"KOSPI_ETF": {"trend": "inflow"}}))

s1 = {"topic": "S&P500 신고가", "strength": 8.0, "key_indicators": ["sp500"]}
r1 = overlay.apply(s1, all_data)
print(f"--- Case: Strong Up + Inflow ---")
print(f"Price Strength: {r1['price_strength']}")
print(f"Consistency: {r1['flow_consistency']}")
print(f"State: {r1['flow_state_detail']}")
print(f"Strength: {r1['extended_strength']}") # 8 + 3 = 11 -> 10

# Case: WEAK_UP + STRONG_OUTFLOW (Consistency -2 -> STRONG_DISTRIBUTION)
all_data_2 = {
    "market": {"data": {"multi_period_stats": {"sp500": {"z_score_20d": 0.5, "5d_change_pct": 0.2}}}}
}
(flow_dir / "foreign_flow.json").write_text(json.dumps({"trend_3d": "outflow"}))
(flow_dir / "etf_flow.json").write_text(json.dumps({"SPY": {"trend": "outflow"}}))

s2 = {"topic": "S&P500 야금야금 상승", "strength": 8.0, "key_indicators": ["sp500"]}
r2 = overlay.apply(s2, all_data_2)
print(f"\n--- Case: Weak Up + Strong Outflow ---")
print(f"Price Strength: {r2['price_strength']}")
print(f"Consistency: {r2['flow_consistency']}")
print(f"State: {r2['flow_state_detail']}")
print(f"Strength: {r2['extended_strength']}") # 8 - 3 = 5
