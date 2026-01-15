from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen
import requests
from src.utils.target_date import get_target_parts

from src.utils.retry import retry

def _utc_now() -> str:
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

@retry(max_attempts=3, base_delay=1.0)
def _fetch_json(url: str) -> dict:
    req = Request(url, headers={"Accept": "application/json", "User-Agent": "hoin-insight/1.0"})
    with urlopen(req, timeout=15) as resp:
        raw = resp.read().decode("utf-8")
    return json.loads(raw)

def write_raw_xau_usd(base_dir: Path) -> Path:
    """
    Source: https://api.gold-api.com/price/{symbol}
    We read XAU (gold) and store as XAUUSD spot price per oz in USD.
    """
    source = "gold-api.com"
    entity = "XAUUSD"
    unit = "USD"

    ts_utc = _utc_now()
    y, m, d = get_target_parts()

    out_dir = base_dir / "data" / "raw" / "metal_gold_xauusd_spot_gold_api" / y / m / d
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "xau_usd.json"

    url = "https://api.gold-api.com/price/XAU"
    payload = _fetch_json(url)

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
        "price_usd_per_oz": float(price),
        "raw": payload,
    }

    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_path
