from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pandas as pd

def _utc_date_parts() -> tuple[str, str, str]:
    return (
        datetime.utcnow().strftime("%Y"),
        datetime.utcnow().strftime("%m"),
        datetime.utcnow().strftime("%d"),
    )

def write_curated_usdkrw_csv(base_dir: Path) -> Path:
    y, m, d = _utc_date_parts()
    rp = base_dir / "data" / "raw" / "exchangerate" / y / m / d / "usdkrw.json"
    payload = json.loads(rp.read_text(encoding="utf-8"))

    out_dir = base_dir / "data" / "curated" / "fx"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "usdkrw.csv"

    row = {
        "ts_utc": payload["ts_utc"],
        "entity": payload["entity"],
        "value": float(payload["price_krw_per_usd"]),
        "unit": payload["unit"],
        "source": payload["source"],
        "dataset_id": "fx_usdkrw_spot_open_er_api",
        "is_derived": False,
        "derived_from": "",
    }
    df = pd.DataFrame([row])
    if out_path.exists():
        old = pd.read_csv(out_path)
        df = pd.concat([old, df], ignore_index=True)
    df = df.drop_duplicates(subset=["ts_utc", "entity", "dataset_id"], keep="last")
    df.to_csv(out_path, index=False)
    return out_path
