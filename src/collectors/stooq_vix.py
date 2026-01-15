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
def _fetch_vix_data() -> tuple[str, float]:
    """
    Fetches the latest VIX data using yfinance (^VIX).
    Returns (obs_date, close_price).
    """
    ticker = yf.Ticker("^VIX")
    
    end_date = datetime.utcnow()
    start_date = end_date - pd.Timedelta(days=7)
    
    hist = ticker.history(start=start_date.strftime("%Y-%m-%d"), end=end_date.strftime("%Y-%m-%d"))
    
    if hist.empty:
        raise ValueError("yfinance VIX (^VIX) returned empty history")
    
    last_row = hist.iloc[-1]
    
    date_val = last_row.name
    obs_date = date_val.strftime("%Y-%m-%d")
    
    close_val = float(last_row["Close"])
    
    return obs_date, close_val

def write_raw_vix(base_dir: Path) -> Path:
    source = "yfinance"
    entity = "VIX"
    unit = "INDEX"
    ts_utc = _utc_now()

    y, m, d = get_target_parts()
    out_dir = base_dir / "data" / "raw" / "risk_vix_index_stooq" / y / m / d
    # Preserving directory name "stooq" for compatibility
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "vix.json"

    try:
        obs_date, close = _fetch_vix_data()
    except Exception as e:
        raise ValueError(f"Failed to fetch VIX from yfinance: {e}")

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
