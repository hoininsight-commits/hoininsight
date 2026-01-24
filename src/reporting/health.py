from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import List

def write_health(base_dir: Path, status: str, checks_ok: bool, check_lines: List[str], per_dataset: List[dict]) -> Path:
    ymd = datetime.utcnow().strftime("%Y/%m/%d")
    out_dir = base_dir / "data" / "reports" / ymd
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "health.json"

    payload = {
        "ts_utc": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": status,
        "checks_ok": checks_ok,
        "checks": check_lines,
        "per_dataset": per_dataset,
    }

    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_path
