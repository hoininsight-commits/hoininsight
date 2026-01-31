from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from src.normalizers.common_timeseries import build_row, append_timeseries_csv

def _utc_date_parts() -> tuple[str, str, str]:
    return (
        datetime.now().strftime("%Y"),
        datetime.now().strftime("%m"),
        datetime.now().strftime("%d"),
    )

def write_curated_usdkrw_csv(base_dir: Path) -> Path:
    y, m, d = _utc_date_parts()
    rp = base_dir / "data" / "raw" / "fx_usdkrw_spot_open_yfinance" / y / m / d / "usdkrw.json"
    payload = json.loads(rp.read_text(encoding="utf-8"))

    row = build_row(
        ts_utc=payload["ts_utc"],
        entity=payload["entity"],
        value=float(payload["close"]),
        unit=payload["unit"],
        source=payload["source"],
        dataset_id="fx_usdkrw_spot_open_er_api",
        metric_name="spot_rate",
        is_derived=False,
        derived_from="",
    )

    out_path = base_dir / "data" / "curated" / "fx" / "usdkrw.csv"
    return append_timeseries_csv(out_path, row)
