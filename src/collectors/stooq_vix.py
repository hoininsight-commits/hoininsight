from __future__ import annotations

import csv
import io
import json
import requests
from datetime import datetime
from io import StringIO
from pathlib import Path
from urllib.request import Request, urlopen

import pandas as pd

from src.utils.retry import with_retry
from src.utils.target_date import get_target_parts
from src.utils.errors import SkipError

CSV_URL = "https://stooq.com/q/d/l/?s=%5Evix&i=d"

def _utc_date_parts() -> tuple[str, str, str]:
    return (
        datetime.utcnow().strftime("%Y"),
        datetime.utcnow().strftime("%m"),
        datetime.utcnow().strftime("%d"),
    )

def _utc_now() -> str:
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

def _fetch_csv(url: str) -> str:
    req = Request(url, headers={"User-Agent": "hoin-insight-bot"})
    with urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")

def write_raw_vix(base_dir: Path) -> Path:
    """
    Source: Stooq CSV download for ^VIX (daily).
    We store latest close as VIX index level.
    """
    source = "stooq.com"
    entity = "VIX"
    unit = "INDEX"
    ts_utc = _utc_now()
    
    y, m, d = get_target_parts()
    out_dir = base_dir / "data" / "raw" / "risk_vix_index_stooq" / y / m / d
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "vix.json"

    try:
        csv_text = with_retry(lambda: _fetch_csv(CSV_URL), attempts=3, base_sleep=1.0)
        df = pd.read_csv(StringIO(csv_text))
        
        # Stooq sometimes returns lower case columns
        df.columns = [c.capitalize() for c in df.columns]

        # Expected columns: Date, Open, High, Low, Close, Volume
        if "Close" not in df.columns:
            raise ValueError("stooq vix CSV missing Close column")

        df = df.dropna(subset=["Close"]).copy()
        if len(df) == 0:
            raise SkipError("stooq vix CSV has no rows (likely holiday or missing data)")

        last = df.iloc[-1]
        obs_date = str(last["Date"]) if "Date" in df.columns else ""
        close = float(last["Close"])
    except SkipError:
        raise
    except Exception as e:
        # If it's a network error or parsing error, we arguably should FAIL or SKIP.
        # But per requirements: "source data missing" => SKIP/WARN.
        # Let's re-raise as SkipError if it seems like a data availability issue, 
        # or just fail if it's a hard error.
        # For now, to meet "no mock" requirement, we simply interpret fetch failure as Skip/Fail.
        # The user said "Soft-fail rules".
        raise RuntimeError(f"VIX fetch failed: {e}") 
    
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
