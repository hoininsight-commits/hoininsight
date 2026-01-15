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
    return base_dir / "data" / "raw" / "risk_vix_index_stooq" / y / m / d / "vix.json"

def write_curated_vix_csv(base_dir: Path) -> Path:
    rp = raw_path_for_today(base_dir)
    payload = json.loads(rp.read_text(encoding="utf-8"))

    row = build_row(
        ts_utc=payload["ts_utc"],
        entity=payload["entity"],
        value=float(payload["close"]),
        unit=payload["unit"],
        source=payload["source"],
        dataset_id="risk_vix_index_stooq",
        metric_name="close",
        is_derived=False,
        derived_from="",
    )

    out_path = base_dir / "data" / "curated" / "risk" / "vix.csv"
    return append_timeseries_csv(out_path, row)
