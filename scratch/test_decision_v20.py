import json
from pathlib import Path
from src.analysis.hunter_enricher import HunterEnricher

# Case: Strong Uptrend
signal = {
    "topic": "S&P500 급등",
    "extended_strength": 9.2,
    "flow_state": "CONFIRMED_UPTREND",
    "flow_state_detail": "CONFIRMED_UPTREND",
    "price_strength": "strong_up"
}

enricher = HunterEnricher()
enriched = enricher.enrich(signal)

print(json.dumps(enriched["decision_meta"], indent=2, ensure_ascii=False))
