from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from src.registry.loader import load_datasets

@dataclass
class CheckResult:
    ok: bool
    lines: list[str]
    per_dataset: list[dict]

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
    per_dataset: list[dict] = []

    report = base_dir / "data" / "reports" / y / m / d / "daily_brief.md"
    if report.exists():
        lines.append(f"[OK] report: {report.as_posix()}")
    else:
        ok = False
        lines.append(f"[MISS] report: {report.as_posix()}")

    for ds in datasets:
        anomalies = base_dir / "data" / "features" / "anomalies" / y / m / d / f"{ds.dataset_id}.json"
        topics = base_dir / "data" / "topics" / y / m / d / f"{ds.dataset_id}.json"
        curated = base_dir / ds.curated_path

        a_ok = anomalies.exists()
        t_ok = topics.exists()
        c_ok = curated.exists()

        if a_ok:
            lines.append(f"[OK] anomalies({ds.dataset_id}): {anomalies.as_posix()}")
        else:
            ok = False
            lines.append(f"[MISS] anomalies({ds.dataset_id}): {anomalies.as_posix()}")

        if t_ok:
            lines.append(f"[OK] topics({ds.dataset_id}): {topics.as_posix()}")
        else:
            ok = False
            lines.append(f"[MISS] topics({ds.dataset_id}): {topics.as_posix()}")

        if c_ok:
            lines.append(f"[OK] curated({ds.dataset_id}): {curated.as_posix()}")
        else:
            ok = False
            lines.append(f"[MISS] curated({ds.dataset_id}): {curated.as_posix()}")

        per_dataset.append(
            {
                "dataset_id": ds.dataset_id,
                "curated_path": curated.as_posix(),
                "curated_ok": c_ok,
                "anomalies_ok": a_ok,
                "topics_ok": t_ok,
            }
        )

    return CheckResult(ok=ok, lines=lines, per_dataset=per_dataset)
