import json
from pathlib import Path

def map_stock_decisions(decision, impact_data):
    """
    Maps theme-level decision to individual stocks.
    Weight stock confidence by its relevance score.
    """
    theme_decision = decision.get("decision", {})
    action = theme_decision.get("action", "WATCH")
    base_confidence = theme_decision.get("confidence", 0)
    
    stocks = impact_data.get("mentionable_stocks", [])
    results = []

    for stock in stocks:
        # Use relevance_score from impact_mentionables.json or default to 0.5
        # Note: relevance_score is usually 0-100 in engine, but 0-1 in UI.
        # We'll normalize if it's > 1.
        raw_relevance = stock.get("relevance", stock.get("score", 0.5))
        weight = raw_relevance / 100.0 if raw_relevance > 1 else raw_relevance
        
        stock_conf = base_confidence * weight
        
        results.append({
            "ticker": stock.get("ticker", stock.get("stock", "N/A")),
            "name": stock.get("name", stock.get("stock", "N/A")),
            "action": action,
            "confidence": round(stock_conf, 2),
            "relevance_weight": round(weight, 2)
        })

    return results

if __name__ == "__main__":
    dec = {"decision": {"action": "ACCUMULATE", "confidence": 0.8}}
    imp = {"mentionable_stocks": [{"stock": "NVDA", "score": 90}]}
    print(json.dumps(map_stock_decisions(dec, imp), indent=2))
