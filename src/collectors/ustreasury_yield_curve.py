from __future__ import annotations

import json
from datetime import datetime
from io import StringIO
from pathlib import Path
from urllib.request import Request, urlopen

import pandas as pd

from src.utils.retry import with_retry

CSV_URL = "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/2024/all?type=daily_treasury_yield_curve&field_tdr_date_value=all"

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

def write_raw_us10y(base_dir: Path) -> Path:
    """
    Fetch US Treasury daily yield curve CSV and extract latest available 10 Yr yield.
    Store raw as json in data/raw/ustreasury/YYYY/MM/DD/us10y.json
    """
    source = "treasury.gov"
    entity = "US10Y"
    unit = "PCT"
    ts_utc = _utc_now()

    y, m, d = _utc_date_parts()
    out_dir = base_dir / "data" / "raw" / "ustreasury" / y / m / d
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "us10y.json"

    csv_text = with_retry(lambda: _fetch_csv(CSV_URL), attempts=3, base_sleep=1.0)
    df = pd.read_csv(StringIO(csv_text))

    # Defensive column naming variations
    # Usually: "Date" and "10 Yr"
    date_col = "Date" if "Date" in df.columns else df.columns[0]
    ten_col = None
    for c in df.columns:
        if str(c).strip() in ["10 Yr", "10YR", "10Y", "10 Yr."]:
            ten_col = c
            break
    if ten_col is None:
        # fallback: find column containing '10' and 'Yr'
        for c in df.columns:
            s = str(c)
            if "10" in s and ("Yr" in s or "year" in s.lower()):
                ten_col = c
                break
    if ten_col is None:
        raise ValueError("cannot find 10Y column in treasury CSV")

    # Take the latest non-null value
    df = df.dropna(subset=[ten_col]).copy()
    if len(df) == 0:
        raise ValueError("treasury CSV has no 10Y data")

    last = df.iloc[-1]
    obs_date = str(last[date_col])
    us10y = float(last[ten_col])

    payload = {
        "ts_utc": ts_utc,
        "source": source,
        "entity": entity,
        "unit": unit,
        "obs_date": obs_date,
        "yield_pct": us10y,
    }

    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_path
