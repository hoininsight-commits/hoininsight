from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import json
import pandas as pd
import sys
# matplotlib imported lazily

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

def _safe_read_json(p: Path) -> Optional[Any]:
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None

@dataclass
class ChartResult:
    dataset_id: str
    report_key: str
    png_path: str
    ok: bool
    reason: str

def _collect_anomaly_days(base_dir: Path, dataset_id: str, days: int = 90, thr: float = 0.01) -> Dict[str, float]:
    """
    Collect anomaly days from data/features/anomalies/YYYY/MM/DD/{dataset_id}.json
    Returns map: {"YYYY-MM-DD": roc_1d, ...} for abs(roc_1d) >= thr
    """
    out: Dict[str, float] = {}
    root = base_dir / "data" / "features" / "anomalies"
    if not root.exists():
        return out

    # scan last N days by date
    for i in range(days):
        d = datetime.utcnow().date() - __import__("datetime").timedelta(days=i)
        p = root / f"{d.year:04d}" / f"{d.month:02d}" / f"{d.day:02d}" / f"{dataset_id}.json"
        
        # Robustly handle missing file
        if not p.exists():
            continue
            
        payload = _safe_read_json(p)
        
        # Handle list or dict payload
        data = {}
        if isinstance(payload, list):
            if len(payload) > 0 and isinstance(payload[-1], dict):
                data = payload[-1]
        elif isinstance(payload, dict):
            data = payload
            
        if "roc_1d" in data:
            try:
                roc = float(data["roc_1d"])
                if abs(roc) >= thr:
                    out[f"{d.year:04d}-{d.month:02d}-{d.day:02d}"] = roc
            except Exception:
                pass
    return out

def generate_curated_charts(base_dir: Path, days: int = 90) -> Tuple[Path, List[ChartResult]]:
    """
    Generates PNG charts for each enabled dataset's curated CSV.
    Output:
      data/reports/YYYY/MM/DD/charts/{dataset_id}.png
    Overlay:
      anomaly markers for days where abs(roc_1d) >= 0.01 within last N days.
    """
    ymd = _ymd()
    out_dir = base_dir / "data" / "reports" / ymd / "charts"
    out_dir.mkdir(parents=True, exist_ok=True)

    reg_path = base_dir / "registry" / "datasets.yml"
    datasets = [ds for ds in load_datasets(reg_path) if ds.enabled]

    results: List[ChartResult] = []

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("[Charts] Matplotlib not found, skipping charts.", file=sys.stderr)
        return out_dir, []

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

        # Correctly get current UTC time without double localization
        # pd.Timestamp.now(tz="UTC") is correct.
        cutoff = pd.Timestamp.now(tz="UTC") - pd.Timedelta(days=days)
        df90 = df[df["ts"] >= cutoff]
        if len(df90) == 0:
            df90 = df.tail(min(len(df), 200))

        # Collect anomaly days and map to points in df90 by date
        anomaly_map = _collect_anomaly_days(base_dir, ds.dataset_id, days=days, thr=0.01)
        df90_dates = df90.copy()
        df90_dates["date"] = df90_dates["ts"].dt.strftime("%Y-%m-%d")

        mark = df90_dates[df90_dates["date"].isin(anomaly_map.keys())]
        # marker size by abs(roc_1d)
        sizes = []
        for dstr in mark["date"].tolist():
            roc = float(anomaly_map.get(dstr, 0.0))
            sizes.append(max(20.0, min(120.0, abs(roc) * 8000.0)))

        png = out_dir / f"{ds.dataset_id}.png"

        plt.figure()
        plt.plot(df90["ts"], df90["value"])
        if len(mark) > 0:
            plt.scatter(mark["ts"], mark["value"], s=sizes)

        plt.title(f"{ds.report_key} ({ds.dataset_id})")
        plt.xlabel("ts_utc")
        plt.ylabel("value")
        plt.tight_layout()
        plt.savefig(png.as_posix(), dpi=140)
        plt.close()

        rel = f"data/reports/{ymd}/charts/{ds.dataset_id}.png"
        results.append(ChartResult(ds.dataset_id, ds.report_key, rel, True, "ok"))

    return out_dir, results
