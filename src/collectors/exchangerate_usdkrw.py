from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from urllib.request import urlopen, Request

URL = "https://open.er-api.com/v6/latest/USD"

def _utc_date_parts() -> tuple[str, str, str]:
    return (
        datetime.utcnow().strftime("%Y"),
        datetime.utcnow().strftime("%m"),
        datetime.utcnow().strftime("%d"),
    )

def write_raw_usdkrw(base_dir: Path) -> Path:
    req = Request(URL, headers={"User-Agent": "hoin-insight-bot"})
    with urlopen(req, timeout=30) as resp:
        raw = resp.read().decode("utf-8")
    j = json.loads(raw)
    krw = float(j["rates"]["KRW"])
    ts_utc = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    y, m, d = _utc_date_parts()
    out_dir = base_dir / "data" / "raw" / "exchangerate" / y / m / d
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "usdkrw.json"
    out_path.write_text(
        json.dumps(
            {
                "ts_utc": ts_utc,
                "price_krw_per_usd": krw,
                "source": "open.er-api.com",
                "entity": "USDKRW",
                "unit": "KRW",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return out_path
