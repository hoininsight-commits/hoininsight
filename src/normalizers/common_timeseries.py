from __future__ import annotations

from pathlib import Path
from typing import Dict, Any

import pandas as pd

from src.utils.fingerprint import make_fingerprint

REQUIRED = [
    "ts_utc",
    "entity",
    "value",
    "unit",
    "source",
    "dataset_id",
    "metric_name",
    "is_derived",
    "derived_from",
    "fingerprint",
]

def append_timeseries_csv(out_path: Path, row: Dict[str, Any]) -> Path:
    # schema enforce
    for k in REQUIRED:
        if k not in row:
            raise ValueError(f"missing required column: {k}")

    df = pd.DataFrame([row])

    if out_path.exists():
        old = pd.read_csv(out_path)
        df = pd.concat([old, df], ignore_index=True)

    # fingerprint-based dedupe (keep last)
    df = df.drop_duplicates(subset=["fingerprint"], keep="last")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    return out_path

def build_row(
    ts_utc: str,
    entity: str,
    value: float,
    unit: str,
    source: str,
    dataset_id: str,
    metric_name: str,
    is_derived: bool,
    derived_from: str,
) -> Dict[str, Any]:
    fp = make_fingerprint(entity, ts_utc, unit, source, metric_name)
    return {
        "ts_utc": ts_utc,
        "entity": entity,
        "value": float(value),
        "unit": unit,
        "source": source,
        "dataset_id": dataset_id,
        "metric_name": metric_name,
        "is_derived": bool(is_derived),
        "derived_from": derived_from,
        "fingerprint": fp,
    }
