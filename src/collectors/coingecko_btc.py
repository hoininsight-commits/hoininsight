from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import requests
from src.utils.retry import retry
from src.utils.target_date import get_target_parts

@dataclass
class BTCQuote:
    ts_utc: str
    price_usd: float
    last_updated_at: int

@retry(max_attempts=3, base_delay=1.0)
def fetch_btc_quote() -> BTCQuote:
    """
    Fetches the latest BTC-USD data using CoinGecko API.
    """
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        price = data.get("bitcoin", {}).get("usd")
        
        if price is None:
            raise ValueError("CoinGecko response missing bitcoin/usd price")
            
        ts_utc = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        last_updated_at = int(datetime.now().timestamp())
        
        return BTCQuote(ts_utc=ts_utc, price_usd=float(price), last_updated_at=last_updated_at)
        
    except Exception as e:
        raise ValueError(f"CoinGecko API failed: {e}")

def write_raw_quote(base_dir: Path) -> Path:
    y, m, d = get_target_parts()
    out_dir = base_dir / "data" / "raw" / "crypto_btc_usd_spot_coingecko" / y / m / d
    out_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        quote = fetch_btc_quote()
    except Exception as e:
         raise RuntimeError(f"Failed to fetch BTC from CoinGecko: {e}")

    out_path = out_dir / "btc_usd.json"
    out_path.write_text(
        json.dumps(
            {
                "ts_utc": quote.ts_utc,
                "price_usd": quote.price_usd,
                "last_updated_at": quote.last_updated_at,
                "source": "coingecko", 
                "entity": "BTCUSD",
                "unit": "USD",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return out_path
