from __future__ import annotations

import json
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from urllib.request import urlopen, Request

from src.utils.retry import with_retry

URL = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_last_updated_at=true"

@dataclass
class BTCQuote:
    ts_utc: str
    price_usd: float
    last_updated_at: int

def _utc_date_parts() -> tuple[str, str, str]:
    return (
        datetime.utcnow().strftime("%Y"),
        datetime.utcnow().strftime("%m"),
        datetime.utcnow().strftime("%d"),
    )

def _fetch_raw() -> str:
    req = Request(URL, headers={"User-Agent": "hoin-insight-bot"})
    with urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")

def fetch_btc_quote() -> BTCQuote:
    raw = with_retry(_fetch_raw, attempts=3, base_sleep=1.0)
    j = json.loads(raw)
    
    if "bitcoin" not in j:
        raise ValueError(f"CoinGecko response missing 'bitcoin' key: {raw}")
    
    btc_data = j["bitcoin"]
    
    if "usd" not in btc_data:
        raise ValueError(f"CoinGecko response missing 'usd' price: {raw}")

    price = float(btc_data["usd"])
    
    # Robustly handle last_updated_at
    if "last_updated_at" in btc_data:
        last_updated_at = int(btc_data["last_updated_at"])
    else:
        # Fallback to current system time if API doesn't provide it
        last_updated_at = int(time.time())

    ts_utc = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    return BTCQuote(ts_utc=ts_utc, price_usd=price, last_updated_at=last_updated_at)

def write_raw_quote(base_dir: Path) -> Path:
    y, m, d = _utc_date_parts()
    out_dir = base_dir / "data" / "raw" / "coingecko" / y / m / d
    out_dir.mkdir(parents=True, exist_ok=True)
    quote = fetch_btc_quote()
    out_path = out_dir / "btc_usd.json"
    out_path.write_text(
        json.dumps(
            {
                "ts_utc": quote.ts_utc,
                "price_usd": quote.price_usd,
                "last_updated_at": quote.last_updated_at,
                "source": "coingecko",
                "entity": "BTCUSD",
                "unit": "USD",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return out_path
