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
def _fetch_usdkrw_data() -> tuple[str, float]:
    """
    Fetches the latest USDKRW (KRW=X) data using yfinance.
    Returns (obs_date, close_price).
    """
    ticker = yf.Ticker("KRW=X")
    
    # Use explicit dates to avoid yfinance internal period calculation errors
    end_date = datetime.now() + pd.Timedelta(days=1)
    # Go back 10 days to cover weekends/holidays safely
    start_date = end_date - pd.Timedelta(days=10)
    
    hist = ticker.history(start=start_date.strftime("%Y-%m-%d"), end=end_date.strftime("%Y-%m-%d"))
    
    if hist.empty:
        raise ValueError("yfinance USDKRW (KRW=X) returned empty history")
    
    # Get last available row
    last_row = hist.iloc[-1]
    
    # Date handling
    date_val = last_row.name
    obs_date = date_val.strftime("%Y-%m-%d")
    
    close_val = float(last_row["Close"])
    
    return obs_date, close_val

def write_raw_usdkrw(base_dir: Path) -> Path:
    source = "yfinance"
    entity = "USDKRW"
    unit = "KRW"
    ts_utc = _utc_now()

    y, m, d = get_target_parts()
    # New output path: fx_usdkrw_spot_open_yfinance
    out_dir = base_dir / "data" / "raw" / "fx_usdkrw_spot_open_yfinance" / y / m / d
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "usdkrw.json"

    obs_date, close = _fetch_usdkrw_data()

    # Align payload structure with other yfinance collectors
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
