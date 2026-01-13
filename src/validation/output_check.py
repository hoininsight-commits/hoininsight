from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from src.registry.loader import load_datasets

@dataclass
class CheckResult:
    ok: bool
    lines: list[str]

def _utc_ymd() -> tuple[str, str, str]:
    return (
        datetime.utcnow().strftime("%Y"),
        datetime.utcnow().strftime("%m"),
        datetime.utcnow().strftime("%d"),
    )

def run_output_checks(base_dir: Path) -> CheckResult:
    y, m, d = _utc_ymd()
    reg = base_dir / "registry" / "datasets.yml"
    datasets = [ds for ds in load_datasets(reg) if ds.enabled]

    lines: list[str] = []
    ok = True

    # 공통 산출물(합본 리포트)
    report = base_dir / "data" / "reports" / y / m / d / "daily_brief.md"
    if report.exists():
        lines.append(f"[OK] report: {report.as_posix()}")
    else:
        ok = False
        lines.append(f"[MISS] report: {report.as_posix()}")

    # dataset별 산출물
    for ds in datasets:
        anomalies = base_dir / "data" / "features" / "anomalies" / y / m / d / f"{ds.dataset_id}.json"
        topics = base_dir / "data" / "topics" / y / m / d / f"{ds.dataset_id}.json"

        if anomalies.exists():
            lines.append(f"[OK] anomalies({ds.dataset_id}): {anomalies.as_posix()}")
        else:
            ok = False
            lines.append(f"[MISS] anomalies({ds.dataset_id}): {anomalies.as_posix()}")

        if topics.exists():
            lines.append(f"[OK] topics({ds.dataset_id}): {topics.as_posix()}")
        else:
            ok = False
            lines.append(f"[MISS] topics({ds.dataset_id}): {topics.as_posix()}")

    return CheckResult(ok=ok, lines=lines)
