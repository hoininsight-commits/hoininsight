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

def write_curated_example(base_dir: Path) -> Path:
    # TODO: source/raw 경로 교체
    source = "example_source"
    raw_filename = "example.json"

    y, m, d = _utc_date_parts()
    rp = base_dir / "data" / "raw" / source / y / m / d / raw_filename
    payload = json.loads(rp.read_text(encoding="utf-8"))

    # TODO: dataset_id / metric_name 교체
    row = build_row(
        ts_utc=payload["ts_utc"],
        entity=payload["entity"],
        value=float(payload["value"]),
        unit=payload["unit"],
        source=payload["source"],
        dataset_id="example_dataset_id",
        metric_name="metric_name",
        is_derived=False,
        derived_from="",
    )

    # TODO: curated_path 교체
    out_path = base_dir / "data" / "curated" / "example" / "example.csv"
    return append_timeseries_csv(out_path, row)
