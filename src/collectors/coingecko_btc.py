from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from urllib.request import urlopen, Request

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

def fetch_btc_quote() -> BTCQuote:
    req = Request(URL, headers={"User-Agent": "hoin-insight-bot"})
    with urlopen(req, timeout=30) as resp:
        raw = resp.read().decode("utf-8")
    j = json.loads(raw)
    price = float(j["bitcoin"]["usd"])
    last_updated_at = int(j["bitcoin"]["last_updated_at"])
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
