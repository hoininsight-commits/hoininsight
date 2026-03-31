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
def _fetch_silver_data() -> tuple[str, float]:
    """
    Fetches the latest Silver Futures (SI=F) data using yfinance.
    Returns (obs_date, close_price).
    """
    ticker = yf.Ticker("SI=F")
    
    end_date = datetime.now() + pd.Timedelta(days=1)
    start_date = end_date - pd.Timedelta(days=10)
    
    hist = ticker.history(start=start_date.strftime("%Y-%m-%d"), end=end_date.strftime("%Y-%m-%d"))
    
    if hist.empty:
        raise ValueError("yfinance Silver (SI=F) returned empty history")
    
    last_row = hist.iloc[-1]
    
    obs_date = last_row.name.strftime("%Y-%m-%d")
    close_val = float(last_row["Close"])
    
    return obs_date, close_val

def write_raw_xag_usd(base_dir: Path) -> Path:
    source = "yfinance"
    entity = "XAGUSD"
    unit = "USD"
    ts_utc = _utc_now()

    y, m, d = get_target_parts()
    # New output path: metal_silver_xagusd_spot_yfinance
    out_dir = base_dir / "data" / "raw" / "metal_silver_xagusd_spot_yfinance" / y / m / d
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "xag_usd.json"

    obs_date, close = _fetch_silver_data()

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
