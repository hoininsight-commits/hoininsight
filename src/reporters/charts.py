from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

import pandas as pd
import matplotlib.pyplot as plt

from src.registry.loader import load_datasets

def _ymd() -> str:
    return datetime.utcnow().strftime("%Y/%m/%d")

def _parse_ts(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, utc=True, errors="coerce")

def _safe_read_csv(p: Path) -> Optional[pd.DataFrame]:
    if not p.exists():
        return None
    try:
        return pd.read_csv(p)
    except Exception:
        return None

@dataclass
class ChartResult:
    dataset_id: str
    report_key: str
    png_path: str
    ok: bool
    reason: str

def generate_curated_charts(base_dir: Path, days: int = 90) -> Tuple[Path, List[ChartResult]]:
    """
    Generates PNG charts for each enabled dataset's curated CSV.
    Output:
      data/reports/YYYY/MM/DD/charts/{dataset_id}.png
    """
    ymd = _ymd()
    out_dir = base_dir / "data" / "reports" / ymd / "charts"
    out_dir.mkdir(parents=True, exist_ok=True)

    reg_path = base_dir / "registry" / "datasets.yml"
    datasets = [ds for ds in load_datasets(reg_path) if ds.enabled]

    results: List[ChartResult] = []

    for ds in datasets:
        curated = base_dir / ds.curated_path
        df = _safe_read_csv(curated)
        if df is None:
            results.append(ChartResult(ds.dataset_id, ds.report_key, "", False, "missing_or_unreadable_curated_csv"))
            continue
        if "ts_utc" not in df.columns or "value" not in df.columns:
            results.append(ChartResult(ds.dataset_id, ds.report_key, "", False, "missing_required_columns(ts_utc,value)"))
            continue

        ts = _parse_ts(df["ts_utc"])
        df = df.copy()
        df["ts"] = ts
        df = df.dropna(subset=["ts"]).sort_values("ts")
        if len(df) == 0:
            results.append(ChartResult(ds.dataset_id, ds.report_key, "", False, "no_valid_ts_rows"))
            continue

        cutoff = pd.Timestamp.utcnow().tz_localize("UTC") - pd.Timedelta(days=days)
        df90 = df[df["ts"] >= cutoff]
        if len(df90) == 0:
            df90 = df.tail(min(len(df), 200))

        png = out_dir / f"{ds.dataset_id}.png"

        plt.figure()
        plt.plot(df90["ts"], df90["value"])
        plt.title(f"{ds.report_key} ({ds.dataset_id})")
        plt.xlabel("ts_utc")
        plt.ylabel("value")
        plt.tight_layout()
        plt.savefig(png.as_posix(), dpi=140)
        plt.close()

        rel = f"data/reports/{ymd}/charts/{ds.dataset_id}.png"
        results.append(ChartResult(ds.dataset_id, ds.report_key, rel, True, "ok"))

    return out_dir, results
