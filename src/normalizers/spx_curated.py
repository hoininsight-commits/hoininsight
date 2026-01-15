from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from src.normalizers.common_timeseries import build_row, append_timeseries_csv

def _utc_date_parts() -> tuple[str, str, str]:
    return (
        datetime.utcnow().strftime("%Y"),
        datetime.utcnow().strftime("%m"),
        datetime.utcnow().strftime("%d"),
    )

def raw_path_for_today(base_dir: Path) -> Path:
    y, m, d = _utc_date_parts()
    return base_dir / "data" / "raw" / "index_spx_sp500_stooq" / y / m / d / "spx.json"

def write_curated_spx_csv(base_dir: Path) -> Path:
    rp = raw_path_for_today(base_dir)
    payload = json.loads(rp.read_text(encoding="utf-8"))

    row = build_row(
        ts_utc=payload["ts_utc"],
        entity=payload["entity"],
        value=float(payload["close"]),
        unit=payload["unit"],
        source=payload["source"],
        dataset_id="index_spx_sp500_stooq",
        metric_name="close",
        is_derived=False,
        derived_from="",
    )

    out_path = base_dir / "data" / "curated" / "indices" / "spx.csv"
    return append_timeseries_csv(out_path, row)
