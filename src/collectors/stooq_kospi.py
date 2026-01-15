from __future__ import annotations

import csv
import io
import json
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen

import pandas as pd
import requests

from src.utils.retry import retry
from src.utils.target_date import get_target_parts

CSV_URL = "https://stooq.com/q/d/l/?s=%5Ekospi&i=d"

def _utc_now() -> str:
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

@retry(max_attempts=3, base_delay=1.0)
def _fetch_csv(url: str) -> str:
    req = Request(url, headers={"User-Agent": "hoin-insight-bot"})
    with urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")

def write_raw_kospi(base_dir: Path) -> Path:
    source = "stooq.com"
    entity = "KOSPI"
    unit = "INDEX"
    ts_utc = _utc_now()

    y, m, d = get_target_parts()
    out_dir = base_dir / "data" / "raw" / "index_kospi_stooq" / y / m / d
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "kospi.json"

    csv_text = _fetch_csv(CSV_URL)
    df = pd.read_csv(io.StringIO(csv_text))

    if "Close" not in df.columns:
        raise ValueError("stooq kospi CSV missing Close column")

    df = df.dropna(subset=["Close"]).copy()
    if len(df) == 0:
        raise ValueError("stooq kospi CSV has no rows")

    last = df.iloc[-1]
    obs_date = str(last["Date"]) if "Date" in df.columns else ""
    close = float(last["Close"])

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
