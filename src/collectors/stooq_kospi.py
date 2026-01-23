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
def _fetch_kospi_data() -> tuple[str, float]:
    """
    Fetches the latest KOSPI data using yfinance (^KS11).
    Returns (obs_date, close_price).
    """
    try:
        ticker = yf.Ticker("^KS11")
        # Use explicit dates to avoid yfinance internal period calculation errors
        # yfinance 'end' is exclusive, so we add 1 day to include today's potential data
        end_date = datetime.utcnow() + pd.Timedelta(days=1)
        # Go back 10 days to cover weekends/holidays safely
        start_date = end_date - pd.Timedelta(days=10)
        
        hist = ticker.history(start=start_date.strftime("%Y-%m-%d"), end=end_date.strftime("%Y-%m-%d"))
        
        if hist.empty:
            raise ValueError("yfinance KOSPI (^KS11) returned empty history")
        
        last_row = hist.iloc[-1]
        
        date_val = last_row.name
        obs_date = date_val.strftime("%Y-%m-%d")
        
        close_val = float(last_row["Close"])
        return obs_date, close_val
    except Exception as e:
        # Fallback to Stooq generic CSV (sometimes cleaner)
        # KOSPI symbol on Stooq is ^KOSPI
        try:
            url = "https://stooq.com/q/d/l/?s=^kospi&i=d"
            df = pd.read_csv(url)
            if df.empty:
                 raise ValueError("Stooq returned empty csv")
            # Stooq CSV columns: Date,Open,High,Low,Close,Volume
            # Sort by Date just in case
            df["Date"] = pd.to_datetime(df["Date"])
            df = df.sort_values("Date")
            last_row = df.iloc[-1]
            obs_date = last_row["Date"].strftime("%Y-%m-%d")
            close_val = float(last_row["Close"])
            return obs_date, close_val
        except Exception as e2:
            raise ValueError(f"Primary(yfinance) failed: {e}. Fallback(stooq) failed: {e2}")

def write_raw_kospi(base_dir: Path) -> Path:
    source = "yfinance"
    entity = "KOSPI"
    unit = "INDEX"
    ts_utc = _utc_now()

    y, m, d = get_target_parts()
    out_dir = base_dir / "data" / "raw" / "index_kospi_stooq" / y / m / d
    # Preserving directory name "stooq" for compatibility
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "kospi.json"

    try:
        obs_date, close = _fetch_kospi_data()
    except Exception as e:
        raise ValueError(f"Failed to fetch KOSPI from yfinance: {e}")

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
