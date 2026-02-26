import json
import re
from datetime import datetime, timedelta
from pathlib import Path

CONFLICT_KEYWORDS = {
    "Tightening": ["QT", "TIGHTENING", "HAWKISH", "RATE HIKE", "금리 인상", "긴축"],
    "Easing": ["QE", "EASING", "DOVISH", "RATE CUT", "금리 인하", "완화"],
    "Inflow": ["INFLOW", "BUY", "LONG", "수급 유입", "매수"],
    "Drain": ["OUTFLOW", "DRAIN", "SELL", "SHORT", "수급 유출", "매도"],
    "SupplyExp": ["SUPPLY INCREASE", "GLUT", "공급 과잉"],
    "DemandWeak": ["DEMAND WEAKNESS", "수요 둔화", "부진", "WEAK"],
    "StrongEarnings": ["EARNINGS SURPRISE", "어닝 서프라이즈", "실적 호조", "PROFIT"],
    "PriceDecline": ["PRICE DECLINE", "하락", "폭락", "CRASH", "BEAR"],
    "RegPressure": ["REGULATION", "규제", "압박", "제재", "BAN", "MANDATE", "FORCING", "COMPLY", "STANDARD"],
    "InvSurge": ["INVESTMENT", "투자", "유치", "유입", "FUNDING"],
    "GeoRisk": ["WAR", "CONFLICT", "전쟁", "분쟁", "RISK", "TENSION"],
    "AssetRally": ["RALLY", "상승", "급등", "BULL", "SURGE", "RECOVERY"],
    "MacroEvent": ["FOMC", "PPI", "CPI", "GDP", "EMPLOYMENT", "지표", "발표", "지수", "INDEX", "DATA", "MEETING", "MINUTES"]
}

def normalize_text(text):
    if not text: return ""
    text = re.sub(r"[^가-힣a-zA-Z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text.upper()

def simulate():
    base_dir = Path("/Users/jihopa/Downloads/HoinInsight_Remote")
    autopsy_path = base_dir / "data_outputs/ops/narrative_component_autopsy_last14days.json"
    
    if not autopsy_path.exists():
        print(f"Error: {autopsy_path} not found")
        return

    with open(autopsy_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Last 7 days
    today = datetime(2026, 2, 25)
    start_date = today - timedelta(days=6)
    
    subset = [item for item in data if datetime.strptime(item["date"], "%Y-%m-%d") >= start_date]
    
    results = []
    for item in subset:
        text = normalize_text(item.get("title", ""))
        
        def has(keys): return any(k in text for k in CONFLICT_KEYWORDS[keys])
        
        # Inferred Directions (for Phase 15B reporting)
        inflation_level = 1 if any(k in text for k in ["CPI", "INFLATION", "PPI"]) else 0
        rate_direction = 1 if has("Tightening") else -1 if has("Easing") else 0
        liquidity_direction = 1 if has("Inflow") else -1 if has("Drain") else 0
        risk_index_direction = 1 if has("GeoRisk") or "VIX" in text else 0
        asset_price_direction = 1 if has("AssetRally") else -1 if has("PriceDecline") else 0
        
        # Patterns
        patterns = {
            "Tightening_Inflow": has("Tightening") and has("Inflow"),
            "Easing_Drain": has("Easing") and has("Drain"),
            "Supply_Demand_Gap": has("SupplyExp") and has("DemandWeak"),
            "Earnings_Price_Conflict": has("StrongEarnings") and has("PriceDecline"),
            "Policy_Inv_Tension": has("RegPressure") and has("InvSurge"),
            "GeoRisk_Rally": has("GeoRisk") and has("AssetRally"),
            "Macro_Price_Divergence": has("MacroEvent") and (has("PriceDecline") or has("AssetRally"))
        }
        
        results.append({
            "topic_id": item.get("topic_id", "UNKNOWN"),
            "date": item.get("date"),
            "title": item.get("title"),
            "intermediate_values": {
                "inflation_level": inflation_level,
                "rate_direction": rate_direction,
                "liquidity_direction": liquidity_direction,
                "risk_index_direction": risk_index_direction,
                "asset_price_direction": asset_price_direction
            },
            "matched_patterns": [k for k, v in patterns.items() if v]
        })
        
    output_path = base_dir / "data_outputs/ops/conflict_mid_values.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"Simulation saved to {output_path}")

if __name__ == "__main__":
    simulate()
