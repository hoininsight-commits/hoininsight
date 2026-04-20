import json
from pathlib import Path
from src.analysis.hunter_enricher import HunterEnricher

# Mock Signal (From Detector v8.2)
signal = {
    "topic": "S&P500 신고가 지속 속 헤지펀드 숏 전환",
    "strength": 8.5,
    "flow_state": "DISTRIBUTION",
    "flow_state_detail": "STRONG_DISTRIBUTION",
    "price_strength": "strong_up",
    "trigger_event": "macro",
    "why_now_hint": "역대급 Z-score 이탈"
}

enricher = HunterEnricher()
enriched = enricher.enrich(signal)

print(json.dumps(enriched, indent=2, ensure_ascii=False))
