from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime
import pandas as pd
import yfinance as yf
from src.utils.retry import retry
from src.utils.target_date import get_target_parts

def _utc_now() -> str:
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

@retry(max_attempts=3, base_delay=1.0)
def _fetch_gold_data() -> tuple[str, float]:
    """
    Fetches the latest Gold Futures (GC=F) data using yfinance.
    Returns (obs_date, close_price).
    """
    ticker = yf.Ticker("GC=F")
    
    end_date = datetime.now() + pd.Timedelta(days=1)
    start_date = end_date - pd.Timedelta(days=10)
    
    hist = ticker.history(start=start_date.strftime("%Y-%m-%d"), end=end_date.strftime("%Y-%m-%d"))
    
    if hist.empty:
        raise ValueError("yfinance Gold (GC=F) returned empty history")
    
    last_row = hist.iloc[-1]
    
    obs_date = last_row.name.strftime("%Y-%m-%d")
    close_val = float(last_row["Close"])
    
    return obs_date, close_val

def write_raw_xau_usd(base_dir: Path) -> Path:
    source = "yfinance"
    entity = "XAUUSD"
    unit = "USD"
    ts_utc = _utc_now()

    y, m, d = get_target_parts()
    # New output path: metal_gold_xauusd_spot_yfinance
    out_dir = base_dir / "data" / "raw" / "metal_gold_xauusd_spot_yfinance" / y / m / d
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "xau_usd.json"

    obs_date, close = _fetch_gold_data()

    payload = {
        "ts_utc": ts_utc,
        "source": source,
        "entity": entity,
        "unit": unit,
        "obs_date": obs_date,
        "close": close,
    }

    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_path
