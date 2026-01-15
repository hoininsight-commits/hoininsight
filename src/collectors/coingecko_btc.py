from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
import pandas as pd
from pathlib import Path
import yfinance as yf
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
    Fetches the latest BTC-USD data using yfinance.
    Returns BTCQuote object for compatibility.
    """
    ticker = yf.Ticker("BTC-USD")
    
    # Use explicit dates + 1 day for inclusive 'today' in yfinance
    end_date = datetime.utcnow() + pd.Timedelta(days=1)
    # Crypto trades 24/7 so 3 days back is plenty
    start_date = end_date - pd.Timedelta(days=3)
    
    hist = ticker.history(start=start_date.strftime("%Y-%m-%d"), end=end_date.strftime("%Y-%m-%d"))
    
    if hist.empty:
        raise ValueError("yfinance BTC-USD returned empty history")
    
    last_row = hist.iloc[-1]
    
    # Close price
    price = float(last_row["Close"])
    
    # Timestamp handling
    # yfinance index is tz-aware usually
    ts_val = last_row.name
    # Convert to unix timestamp for last_updated_at compatibility
    last_updated_at = int(ts_val.timestamp())
    
    ts_utc = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    return BTCQuote(ts_utc=ts_utc, price_usd=price, last_updated_at=last_updated_at)

def write_raw_quote(base_dir: Path) -> Path:
    y, m, d = get_target_parts()
    out_dir = base_dir / "data" / "raw" / "crypto_btc_usd_spot_coingecko" / y / m / d
    # Maintaining "coingecko" directory name for path compatibility
    out_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        quote = fetch_btc_quote()
    except Exception as e:
         raise ValueError(f"Failed to fetch BTC from yfinance: {e}")

    out_path = out_dir / "btc_usd.json"
    out_path.write_text(
        json.dumps(
            {
                "ts_utc": quote.ts_utc,
                "price_usd": quote.price_usd,
                "last_updated_at": quote.last_updated_at,
                "source": "yfinance", # Updated source name
                "entity": "BTCUSD",
                "unit": "USD",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return out_path
