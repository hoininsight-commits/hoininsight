from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

def _utc_date_parts() -> tuple[str, str, str]:
    return (
        datetime.now().strftime("%Y"),
        datetime.now().strftime("%m"),
        datetime.now().strftime("%d"),
    )

def write_raw_example(base_dir: Path) -> Path:
    # TODO: source 이름으로 교체
    source = "example_source"
    # TODO: raw 파일명 교체
    filename = "example.json"

    ts_utc = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

    y, m, d = _utc_date_parts()
    out_dir = base_dir / "data" / "raw" / source / y / m / d
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / filename

    payload = {
        "ts_utc": ts_utc,
        "source": source,
        "entity": "EXAMPLE",
        "unit": "UNIT",
        "value": 123.0,
    }

    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_path
