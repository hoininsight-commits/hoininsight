import json
from pathlib import Path
from src.agents.extensions.detector_extensions import DetectorEnricher

base_dir = Path("/Users/jihopa/Antigravity/hoininsight")
today = "20260420"
enricher = DetectorEnricher(base_dir, today)

# Test Persistence: Yesterday had sp500, today has sp500
anomalies = [
    {
        "topic": "S&P500 신고가 지속",
        "anomaly_type": "SPEED",
        "strength": 8.0,
        "key_indicators": ["sp500"]
    }
]

all_data = {
    "market": {"data": {"multi_period_stats": {"sp500": {"z_score_20d": 1.9}}}},
    "sentiment": {"data": {"news_headlines": []}},
    "consensus": {"major_surprises": []}
}

enriched = enricher.enrich_candidates(anomalies, all_data)
# Should have persistence_days > 0 and is_persistent_signal if p_days >= 2
# Let's see how many days it finds.
print(f"Persistence Days: {enriched[0]['persistence_days']}")
print(f"Is Persistent: {enriched[0]['is_persistent_signal']}")
print(f"Extended Strength: {enriched[0]['extended_strength']}")
