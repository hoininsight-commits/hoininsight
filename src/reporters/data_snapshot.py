from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from src.registry.loader import load_datasets
from src.reporters.charts import generate_curated_charts

def _ymd() -> str:
    return datetime.utcnow().strftime("%Y/%m/%d")

def _ts_now() -> str:
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

def _parse_ts(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, utc=True, errors="coerce")

def _safe_read_csv(p: Path) -> Optional[pd.DataFrame]:
    if not p.exists():
        return None
    try:
        df = pd.read_csv(p)
        return df
    except Exception:
        return None

def _safe_read_json(p: Path) -> Optional[Any]:
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None

def _find_report_dirs(base_dir: Path, days: int) -> List[Path]:
    """
    Find up to N days of report directories under data/reports/YYYY/MM/DD
    (UTC date folders).
    """
    reports_root = base_dir / "data" / "reports"
    out: List[Path] = []
    for i in range(days):
        d = datetime.utcnow().date() - timedelta(days=i)
        p = reports_root / f"{d.year:04d}" / f"{d.month:02d}" / f"{d.day:02d}"
        if p.exists():
            out.append(p)
    return out

def _health_status_for_dataset(health_payload: Any, dataset_id: str) -> Optional[str]:
    if not isinstance(health_payload, dict):
        return None
    per = health_payload.get("per_dataset")
    if not isinstance(per, list):
        return None
    for item in per:
        if isinstance(item, dict) and item.get("dataset_id") == dataset_id:
            st = item.get("status")
            return str(st) if st is not None else None
    return None

@dataclass
class DatasetSnapshot:
    dataset_id: str
    report_key: str
    curated_path: str
    rows: int
    first_ts: str
    last_ts: str
    last_7d_rows: int
    last_30d_rows: int
    ok_7d: int
    skipped_7d: int
    fail_7d: int
    status_today: str

def build_snapshot(base_dir: Path, lookback_days: int = 30) -> Tuple[List[DatasetSnapshot], Dict[str, Any]]:
    ymd = _ymd()
    reg_path = base_dir / "registry" / "datasets.yml"
    datasets = [ds for ds in load_datasets(reg_path) if ds.enabled]

    # Read health history
    report_dirs_7d = _find_report_dirs(base_dir, 7)
    health_7d = []
    for rd in report_dirs_7d:
        hp = _safe_read_json(rd / "health.json")
        health_7d.append(hp)

    # Today's health
    today_health = _safe_read_json(base_dir / "data" / "reports" / ymd / "health.json")

    snaps: List[DatasetSnapshot] = []
    meta: Dict[str, Any] = {
        "ts_utc": _ts_now(),
        "ymd_utc": ymd,
        "enabled_datasets": len(datasets),
        "lookback_days": lookback_days,
        "health_dirs_7d": [p.as_posix() for p in report_dirs_7d],
    }

    for ds in datasets:
        curated = base_dir / ds.curated_path
        df = _safe_read_csv(curated)
        if df is None or "ts_utc" not in df.columns:
            rows = 0
            first_ts = "-"
            last_ts = "-"
            last_7d_rows = 0
            last_30d_rows = 0
        else:
            rows = int(len(df))
            ts = _parse_ts(df["ts_utc"]).dropna()
            if len(ts) == 0:
                first_ts = "-"
                last_ts = "-"
                last_7d_rows = 0
                last_30d_rows = 0
            else:
                first_ts = ts.min().strftime("%Y-%m-%dT%H:%M:%SZ")
                last_ts = ts.max().strftime("%Y-%m-%dT%H:%M:%SZ")
                
                # Correctly calculate now in UTC
                now = pd.Timestamp.now(tz="UTC")
                
                last_7d_rows = int((ts >= (now - pd.Timedelta(days=7))).sum())
                last_30d_rows = int((ts >= (now - pd.Timedelta(days=30))).sum())

        # Health status counts (7 days)
        ok_7d = 0
        skipped_7d = 0
        fail_7d = 0
        for hp in health_7d:
            st = _health_status_for_dataset(hp, ds.dataset_id)
            if st == "OK":
                ok_7d += 1
            elif st == "SKIPPED":
                skipped_7d += 1
            elif st == "FAIL":
                fail_7d += 1

        status_today = _health_status_for_dataset(today_health, ds.dataset_id) or "UNKNOWN"

        snaps.append(
            DatasetSnapshot(
                dataset_id=ds.dataset_id,
                report_key=ds.report_key,
                curated_path=ds.curated_path,
                rows=rows,
                first_ts=first_ts,
                last_ts=last_ts,
                last_7d_rows=last_7d_rows,
                last_30d_rows=last_30d_rows,
                ok_7d=ok_7d,
                skipped_7d=skipped_7d,
                fail_7d=fail_7d,
                status_today=status_today,
            )
        )

    return snaps, meta

def write_data_snapshot(base_dir: Path) -> Path:
    ymd = _ymd()
    out_dir = base_dir / "data" / "reports" / ymd
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "data_snapshot.md"

    # Generate charts first (best-effort)
    _, chart_results = generate_curated_charts(base_dir, days=90)
    chart_map = {r.dataset_id: r for r in chart_results}

    snaps, meta = build_snapshot(base_dir)

    # Sort by status today (OK first), then by report_key
    status_rank = {"OK": 0, "SKIPPED": 1, "FAIL": 2, "UNKNOWN": 3}
    snaps.sort(key=lambda s: (status_rank.get(s.status_today, 9), s.report_key))

    lines: List[str] = []
    lines.append("# Data Snapshot")
    lines.append("")
    lines.append(f"- ts_utc: `{meta['ts_utc']}`")
    lines.append(f"- ymd_utc: `{meta['ymd_utc']}`")
    lines.append(f"- enabled_datasets: `{meta['enabled_datasets']}`")
    lines.append("")
    lines.append("## Per-dataset Status (Today)")
    lines.append("")
    lines.append("| report_key | dataset_id | status_today | rows | first_ts_utc | last_ts_utc | last_7d_rows | last_30d_rows | ok_7d | skipped_7d | fail_7d | curated_path | chart_png |")
    lines.append("|---|---|---:|---:|---|---|---:|---:|---:|---:|---:|---|---|")
    for s in snaps:
        cr = chart_map.get(s.dataset_id)
        if cr and cr.ok and cr.png_path:
            chart_cell = f"[png]({cr.png_path})"
        else:
            chart_cell = "-"
        lines.append(
            f"| {s.report_key} | {s.dataset_id} | {s.status_today} | {s.rows} | {s.first_ts} | {s.last_ts} | "
            f"{s.last_7d_rows} | {s.last_30d_rows} | {s.ok_7d} | {s.skipped_7d} | {s.fail_7d} | {s.curated_path} | {chart_cell} |"
        )
    lines.append("")
    lines.append("## Charts")
    lines.append(f"- Directory: `data/reports/{ymd}/charts/`")
    lines.append("")
    lines.append("## Notes")
    lines.append("- rows/ts는 curated CSV 기준입니다.")
    lines.append("- ok_7d/skipped_7d/fail_7d는 최근 7일 health.json(per_dataset) 기록을 집계합니다.")
    lines.append("- 파생지표는 데이터 누적 전까지 SKIPPED가 정상일 수 있습니다(soft_fail).")
    lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    
    # [Phase 50] Also write JSON for Topic Gate Input
    import dataclasses
    json_path = out_dir / "daily_snapshot.json"
    snapshot_payload = {
        "meta": meta,
        "datasets": [dataclasses.asdict(s) for s in snaps],
        "chart_map": {k: dataclasses.asdict(v) for k, v in chart_map.items() if v.ok}
    }
    json_path.write_text(json.dumps(snapshot_payload, indent=2, ensure_ascii=False), encoding="utf-8")
    
    return out_path

