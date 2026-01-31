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

def raw_path_for_today(base_dir: Path) -> Path:
    y, m, d = _utc_date_parts()
    return base_dir / "data" / "raw" / "derived" / y / m / d / "corr_btc_spx_30d.json"

def write_curated_corr_btc_spx_30d(base_dir: Path) -> Path:
    rp = raw_path_for_today(base_dir)
    
    # Robust check: if raw file missing, we cannot normalize.
    # We raise FileNotFoundError or similar so the pipeline harness 
    # (wrapped in try/except) logs it, and output_check marks strictly/softly.
    if not rp.exists():
        raise FileNotFoundError(f"Missing raw file for BTC-SPX: {rp}")

    payload = json.loads(rp.read_text(encoding="utf-8"))

    derived_from = ",".join(payload["derived_from"])

    row = build_row(
        ts_utc=payload["obs_ts_utc"],
        entity=payload["entity"],
        value=float(payload["corr_30d"]),
        unit=payload["unit"],
        source=payload["source"],
        dataset_id="derived_corr_btc_spx_30d",
        metric_name="rolling_corr_30d",
        is_derived=True,
        derived_from=derived_from,
    )

    out_path = base_dir / "data" / "curated" / "derived" / "corr_btc_spx_30d.csv"
    return append_timeseries_csv(out_path, row)
