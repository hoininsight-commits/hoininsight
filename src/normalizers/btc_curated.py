from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import pandas as pd

@dataclass
class CuratedRow:
    ts_utc: str
    entity: str
    value: float
    unit: str
    source: str
    dataset_id: str
    is_derived: bool
    derived_from: str

def _utc_date_parts() -> tuple[str, str, str]:
    return (
        datetime.utcnow().strftime("%Y"),
        datetime.utcnow().strftime("%m"),
        datetime.utcnow().strftime("%d"),
    )

def raw_path_for_today(base_dir: Path) -> Path:
    y, m, d = _utc_date_parts()
    return base_dir / "data" / "raw" / "coingecko" / y / m / d / "btc_usd.json"

def write_curated_csv(base_dir: Path) -> Path:
    rp = raw_path_for_today(base_dir)
    payload = json.loads(rp.read_text(encoding="utf-8"))
    row = CuratedRow(
        ts_utc=payload["ts_utc"],
        entity=payload["entity"],
        value=float(payload["price_usd"]),
        unit=payload["unit"],
        source=payload["source"],
        dataset_id="crypto_btc_usd_spot_coingecko",
        is_derived=False,
        derived_from="",
    )
    out_dir = base_dir / "data" / "curated" / "crypto"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "btc_usd.csv"
    df = pd.DataFrame([row.__dict__])

    # 누적(additive) 저장: 기존 파일이 있으면 append
    if out_path.exists():
        old = pd.read_csv(out_path)
        df = pd.concat([old, df], ignore_index=True)

    # 중복 최소 방지: 동일 ts_utc는 마지막 값 유지
    df = df.drop_duplicates(subset=["ts_utc", "entity", "dataset_id"], keep="last")
    df.to_csv(out_path, index=False)
    return out_path
