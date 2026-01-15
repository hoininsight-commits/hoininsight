from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime
import pandas as pd
import yfinance as yf
from src.utils.retry import retry
from src.utils.target_date import get_target_parts

def _utc_now() -> str:
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

@retry(max_attempts=3, base_delay=1.0)
def _fetch_spx_data() -> tuple[str, float]:
    """
    Fetches the latest SPX (S&P 500) data using yfinance (^GSPC).
    Returns (obs_date, close_price).
    """
    ticker = yf.Ticker("^GSPC")
    
    # Use explicit dates to avoid yfinance internal period calculation errors
    # yfinance 'end' is exclusive, so we add 1 day to include today's potential data
    end_date = datetime.utcnow() + pd.Timedelta(days=1)
    # Go back 10 days to cover weekends/holidays safely
    start_date = end_date - pd.Timedelta(days=10)
    
    hist = ticker.history(start=start_date.strftime("%Y-%m-%d"), end=end_date.strftime("%Y-%m-%d"))
    
    if hist.empty:
        # Try fetching 'max' if specific range fails, or just error out
        # But 'max' is heavy. Let's trust 7 days is enough for a daily job.
        # If today is Monday, 7 days covers last week.
        raise ValueError("yfinance SPX (^GSPC) returned empty history")
    
    # Get last available row
    last_row = hist.iloc[-1]
    
    # Date handling
    date_val = last_row.name
    obs_date = date_val.strftime("%Y-%m-%d")
    
    close_val = float(last_row["Close"])
    
    return obs_date, close_val

def write_raw_spx(base_dir: Path) -> Path:
    source = "yfinance"
    entity = "SPX"
    unit = "INDEX"
    ts_utc = _utc_now()

    y, m, d = get_target_parts()
    out_dir = base_dir / "data" / "raw" / "index_spx_sp500_stooq" / y / m / d
    # Note: Preserving "stooq" in directory name to avoid breaking downstream dependency paths for now
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "spx.json"

    try:
        obs_date, close = _fetch_spx_data()
    except Exception as e:
        # Re-raise to let the engine handle the FAIL status
        raise ValueError(f"Failed to fetch SPX from yfinance: {e}")

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
