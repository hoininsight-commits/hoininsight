from __future__ import annotations

import requests
import json
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen

from src.utils.retry import with_retry
from src.utils.target_date import get_target_parts

def _utc_date_parts() -> tuple[str, str, str]:
    return (
        datetime.utcnow().strftime("%Y"),
        datetime.utcnow().strftime("%m"),
        datetime.utcnow().strftime("%d"),
    )

def _utc_now() -> str:
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

def _fetch_raw(url: str) -> str:
    req = Request(url, headers={"Accept": "application/json", "User-Agent": "hoin-insight-bot"})
    with urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")

def write_raw_xag_usd(base_dir: Path) -> Path:
    """
    Source: https://api.gold-api.com/price/{symbol}
    We read XAG (silver) and store as XAGUSD spot price in USD.
    """
    source = "gold-api.com"
    entity = "XAGUSD"
    unit = "USD"

    ts_utc = _utc_now()
    y, m, d = get_target_parts()

    out_dir = base_dir / "data" / "raw" / "metal_silver_xagusd_spot_gold_api" / y / m / d
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "xag_usd.json"

    url = "https://api.gold-api.com/price/XAG"
    raw = with_retry(lambda: _fetch_raw(url), attempts=3, base_sleep=1.0)
    payload = json.loads(raw)

    # Defensive parsing: prefer "price", else try currency key like "USD"
    price = None
    if isinstance(payload, dict):
        if "price" in payload:
            price = payload["price"]
        elif "USD" in payload:
            price = payload["USD"]

    if price is None:
        raise ValueError("gold-api response missing price")

    out = {
        "ts_utc": ts_utc,
        "source": source,
        "entity": entity,
        "unit": unit,
        "price_usd": float(price),
        "raw": payload,
    }

    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_path
