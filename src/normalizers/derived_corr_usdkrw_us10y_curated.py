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
    return base_dir / "data" / "raw" / "derived" / y / m / d / "corr_usdkrw_us10y_30d.json"

def write_curated_corr_usdkrw_us10y_30d(base_dir: Path) -> Path:
    rp = raw_path_for_today(base_dir)

    # Robust check
    if not rp.exists():
        raise FileNotFoundError(f"Missing raw file for USDKRW-US10Y: {rp}")

    payload = json.loads(rp.read_text(encoding="utf-8"))

    derived_from = ",".join(payload["derived_from"])

    row = build_row(
        ts_utc=payload["obs_ts_utc"],
        entity=payload["entity"],
        value=float(payload["corr_30d"]),
        unit=payload["unit"],
        source=payload["source"],
        dataset_id="derived_corr_usdkrw_us10y_30d",
        metric_name="rolling_corr_30d",
        is_derived=True,
        derived_from=derived_from,
    )

    out_path = base_dir / "data" / "curated" / "derived" / "corr_usdkrw_us10y_30d.csv"
    return append_timeseries_csv(out_path, row)
