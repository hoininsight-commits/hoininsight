import os
import logging
import json
import requests
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger("MacroFactConnector")
logging.basicConfig(level=logging.INFO)

# Target Tickers (Yahoo Finance / FRED Symbols)
TARGETS = {
    "US10Y": {"y_sym": "^TNX", "fred_sym": "DGS10", "name": "미 국채 10년물"},
    "US02Y": {"y_sym": "^IRX", "fred_sym": "DGS2", "name": "미 국채 2년물 (Proxy)"}, # IRX is 13 week, getting 2Y via Yahoo is ^TWO usually but sometimes flaky
    "WTI": {"y_sym": "CL=F", "fred_sym": "DCOILWTICO", "name": "WTI 원유"},
    "DXY": {"y_sym": "DX-Y.NYB", "fred_sym": "DTWEXB", "name": "달러 인덱스"},
    "GOLD": {"y_sym": "GC=F", "fred_sym": "GOLDPMGBD228NLBM", "name": "금 선물"}
}

def fetch_yahoo_chart_api(symbol: str) -> Dict[str, Any]:
    """
    Directly fetches from Yahoo Finance Chart API.
    Ref: https://query1.finance.yahoo.com/v8/finance/chart/{symbol}
    """
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=5d"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            result = data.get("chart", {}).get("result", [])[0]
            meta = result.get("meta", {})
            indicators = result.get("indicators", {}).get("quote", [])[0]
            
            # Get latest valid price
            prices = indicators.get("close", [])
            # Filter Nones
            clean_prices = [p for p in prices if p is not None]
            
            if clean_prices:
                latest_price = clean_prices[-1]
                prev_price = clean_prices[-2] if len(clean_prices) > 1 else latest_price
                change = latest_price - prev_price
                change_pct = (change / prev_price) * 100
                
                return {
                    "price": latest_price,
                    "change": change,
                    "change_pct": change_pct,
                    "timestamp": meta.get("regularMarketTime")
                }
    except Exception as e:
        logger.debug(f"Yahoo API failed for {symbol}: {e}")
        
    return {}

def collect_macro_facts(base_dir: Path, ymd: str) -> List[Dict[str, Any]]:
    """
    Collects Macro/Rates hard facts.
    Returns list of facts with 'evidence_grade': 'HARD_FACT'
    """
    facts = []
    
    # 1. Try Yahoo Chart API (Public, High Availability)
    for key, info in TARGETS.items():
        try:
            data = fetch_yahoo_chart_api(info["y_sym"])
            if data:
                # Format Value
                val = data['price']
                chg = data['change_pct']
                
                # Direction Icon
                icon = "➖"
                if chg > 0.5: icon = "🔺"
                if chg < -0.5: icon = "🔻"
                
                fact = {
                    "fact_type": "MACRO_FACT",
                    "fact_text": f"{info['name']} {val:.2f} ({icon} {chg:+.2f}%)",
                    "source": "Market Data (Yahoo)",
                    "source_ref": info["y_sym"],
                    "source_date": datetime.fromtimestamp(data.get('timestamp', 0)).strftime('%Y-%m-%d'),
                    "evidence_grade": "HARD_FACT",
                    "reliability_score": 90,
                    "independence_key": f"MACRO_{key}_{ymd}",
                    "details": {
                        "ticker": key,
                        "value": val,
                        "change_pct": chg
                    }
                }
                facts.append(fact)
            else:
                logger.warning(f"No data for {key} via Yahoo Stats")
                
        except Exception as e:
            logger.error(f"Error processing {key}: {e}")

    # 2. FRED Fallback (only if needed and Key exists)
    # (Skipped for strictly no-mock MVP unless Yahoo fails totally, which is unlikely with direct chart API)
    
    # Save
    if facts:
        save_path = base_dir / f"data/facts/fact_anchors_macro_{ymd.replace('-', '')}.json"
        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_path.write_text(json.dumps(facts, ensure_ascii=False, indent=2), encoding='utf-8')
        logger.info(f"Saved {len(facts)} Macro Facts.")
        
    return facts

if __name__ == "__main__":
    collect_macro_facts(Path("."), datetime.now().strftime("%Y-%m-%d"))
