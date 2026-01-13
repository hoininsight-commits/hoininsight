from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pandas as pd
from src.registry.loader import load_datasets

def _utc_date_parts() -> tuple[str, str, str]:
    return (
        datetime.utcnow().strftime("%Y"),
        datetime.utcnow().strftime("%m"),
        datetime.utcnow().strftime("%d"),
    )

def write_daily_brief(base_dir: Path) -> Path:
    y, m, d = _utc_date_parts()
    out_dir = base_dir / "data" / "reports" / y / m / d
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "daily_brief.md"

    reg = base_dir / "registry" / "datasets.yml"
    datasets = [ds for ds in load_datasets(reg) if ds.enabled]

    lines = [f"# Daily Brief ({y}-{m}-{d})", ""]

    for ds in datasets:
        lines.append(f"## {ds.report_key}")
        curated = base_dir / ds.curated_path
        if curated.exists():
            df = pd.read_csv(curated)
            last_row = df.iloc[-1].to_dict() if len(df) else {}
            lines.append(f"- last_ts_utc: {last_row.get('ts_utc','')}")
            lines.append(f"- last_value: {last_row.get('value','')}")
            lines.append(f"- unit: {last_row.get('unit','')}")
        else:
            lines.append("- (no curated data)")
        lines.append("")

    lines.append("## Topics")
    all_topics = []
    for ds in datasets:
        tp = base_dir / "data" / "topics" / y / m / d / f"{ds.dataset_id}.json"
        if tp.exists():
            all_topics.extend(json.loads(tp.read_text(encoding="utf-8")))
    all_topics = sorted(all_topics, key=lambda x: int(x.get("score", 0)), reverse=True)

    if not all_topics:
        lines.append("- (no topics today)")
    else:
        for t in all_topics:
            lines.append(f"- [{t.get('dataset_id','')}] {t['title']} | score={t['score']}")
            lines.append(f"  - {t['summary']}")

    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out_path
