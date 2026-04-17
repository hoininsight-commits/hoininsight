from __future__ import annotations

import json
import os
import requests
from pathlib import Path
from datetime import datetime
from src.utils.target_date import get_target_parts

def _utc_now() -> str:
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

def _fetch_kospi_yahoo() -> tuple[str, float]:
    """
    Fetches the latest KOSPI data using Yahoo Finance Chart API.
    Used as an alternative to yfinance library when it's blocked.
    """
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    ticker = "^KS11"
    # Try both query1 and query2 as fallback
    urls = [
        f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=5d",
        f"https://query2.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=5d"
    ]
    
    last_err = None
    for url in urls:
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            
            if not data.get("chart", {}).get("result"):
                continue
                
            result = data["chart"]["result"][0]
            timestamps = result.get("timestamp", [])
            indicators = result.get("indicators", {}).get("quote", [{}])[0]
            closes = indicators.get("close", [])
            
            if not closes:
                continue
                
            # Get the latest valid closing price
            for i in range(len(closes) - 1, -1, -1):
                if closes[i] is not None:
                    obs_date = datetime.fromtimestamp(timestamps[i]).strftime("%Y-%m-%d")
                    close_price = round(float(closes[i]), 2)
                    return obs_date, close_price
        except Exception as e:
            last_err = e
            continue
            
    raise ValueError(f"Failed to fetch KOSPI from Yahoo Finance (Tried all endpoints). Last error: {last_err}")

def write_raw_kospi(base_dir: Path) -> Path:
    source = "finance.yahoo.com"
    entity = "KOSPI"
    unit = "INDEX"
    ts_utc = _utc_now()

    y, m, d = get_target_parts()
    # Path MUST match what normalizer expects: raw/index_kospi_stooq
    out_dir = base_dir / "data" / "raw" / "index_kospi_stooq" / y / m / d
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "kospi.json"

    try:
        obs_date, close = _fetch_kospi_yahoo()
    except Exception as e:
        print(f"Error fetching KOSPI: {e}")
        # Soft-fail logic if needed, but registry handles it
        raise e

    payload = {
        "ts_utc": ts_utc,
        "source": source,
        "entity": entity,
        "unit": unit,
        "obs_date": obs_date,
        "close": close,
    }

    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved KOSPI raw data to {out_path}: {close}")
    return out_path

if __name__ == "__main__":
    write_raw_kospi(Path("."))
