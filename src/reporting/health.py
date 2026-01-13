from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from src.registry.loader import load_datasets

@dataclass
class Health:
    ts_utc: str
    status: str
    datasets_enabled: int
    checks_ok: bool
    check_lines: list[str]
    per_dataset: list[dict]

def _utc_ymd() -> tuple[str, str, str]:
    return (
        datetime.utcnow().strftime("%Y"),
        datetime.utcnow().strftime("%m"),
        datetime.utcnow().strftime("%d"),
    )

def write_health(base_dir: Path, status: str, checks_ok: bool, check_lines: list[str], per_dataset: list[dict]) -> Path:
    y, m, d = _utc_ymd()
    reg = base_dir / "registry" / "datasets.yml"
    datasets = [ds for ds in load_datasets(reg) if ds.enabled]
    out_dir = base_dir / "data" / "reports" / y / m / d
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "health.json"

    payload = Health(
        ts_utc=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        status=status,
        datasets_enabled=len(datasets),
        checks_ok=checks_ok,
        check_lines=check_lines,
        per_dataset=per_dataset,
    ).__dict__

    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_path
