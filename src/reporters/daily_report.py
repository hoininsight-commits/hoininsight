from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from src.registry.loader import load_datasets
from src.reporters.data_snapshot import write_data_snapshot

def _ymd() -> str:
    return datetime.utcnow().strftime("%Y/%m/%d")

def _read_json(p: Path) -> Any:
    return json.loads(p.read_text(encoding="utf-8"))

def _collect_all_topics(base_dir: Path) -> List[Dict[str, Any]]:
    ymd = _ymd()
    datasets = [ds for ds in load_datasets(base_dir / "registry" / "datasets.yml") if ds.enabled]
    all_topics: List[Dict[str, Any]] = []
    for ds in datasets:
        tp = base_dir / "data" / "topics" / ymd / f"{ds.dataset_id}.json"
        if tp.exists():
            payload = _read_json(tp)
            if isinstance(payload, list):
                for t in payload:
                    if isinstance(t, dict):
                        t["_report_key"] = ds.report_key
                        all_topics.append(t)
    return all_topics

def write_daily_brief(base_dir: Path) -> Path:
    # Always emit snapshot alongside daily_brief (file-based dashboard)
    write_data_snapshot(base_dir)

    ymd = _ymd()
    out_dir = base_dir / "data" / "reports" / ymd
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "daily_brief.md"

    topics = _collect_all_topics(base_dir)
    topics = [t for t in topics if isinstance(t.get("score", None), (int, float))]
    topics.sort(key=lambda x: float(x.get("score", 0.0)), reverse=True)
    top5 = topics[:5]

    lines: List[str] = []
    lines.append("# Daily Brief")
    lines.append("")
    lines.append("## TOP 5 Topics")
    if len(top5) == 0:
        lines.append("- (no topics)")
    else:
        for i, t in enumerate(top5, 1):
            lines.append(
                f"{i}. **{t.get('_report_key','')}** | {t.get('title','')} | "
                f"score={t.get('score')} | severity={t.get('severity')} | dataset={t.get('dataset_id')}"
            )
    lines.append("")
    lines.append("## Per-dataset Topics")
    if len(topics) == 0:
        lines.append("- (no topics)")
    else:
        for t in topics:
            lines.append(
                f"- [{t.get('severity')}] {t.get('_report_key','')}: {t.get('title','')} "
                f"(score={t.get('score')}, dataset={t.get('dataset_id')})"
            )

    lines.append("")
    lines.append("## Data Snapshot")
    lines.append(f"- See: `data/reports/{ymd}/data_snapshot.md`")
    lines.append("")

    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out_path
