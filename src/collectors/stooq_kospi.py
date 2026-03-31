from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime
import pandas as pd
from src.utils.retry import retry
from src.utils.target_date import get_target_parts

def _utc_now() -> str:
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

@retry(max_attempts=3, base_delay=1.0)
def _fetch_kospi_data() -> tuple[str, float]:
    """
    Fetches the latest KOSPI data using Stooq CSV (^KOSPI).
    Returns (obs_date, close_price).
    """
    try:
        url = "https://stooq.com/q/d/l/?s=^kospi&i=d"
        # Stooq returns a CSV file
        df = pd.read_csv(url)
        
        if df.empty:
            raise ValueError("Stooq returned empty CSV for ^KOSPI")
            
        # Stooq CSV columns: Date,Open,High,Low,Close,Volume
        # Ensure Date is parsed
        if "Date" not in df.columns or "Close" not in df.columns:
             raise ValueError(f"Stooq CSV missing required columns. Cols: {df.columns}")

        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values("Date")
        
        last_row = df.iloc[-1]
        
        obs_date = last_row["Date"].strftime("%Y-%m-%d")
        close_val = float(last_row["Close"])
        
        return obs_date, close_val
        
    except Exception as e:
        raise ValueError(f"Failed to fetch KOSPI from Stooq: {e}")

def write_raw_kospi(base_dir: Path) -> Path:
    source = "stooq.com"
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
        raise ValueError(f"Failed to fetch KOSPI from Stooq: {e}")

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
