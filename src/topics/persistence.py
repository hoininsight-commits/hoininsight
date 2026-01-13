from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

def _safe_read_json(p: Path) -> Any:
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None

def count_appearances_7d(base_dir: Path, dataset_id: str, topic_id: str) -> int:
    """
    Count how many times topic_id appeared in the last 7 days for a dataset.
    Scans: data/topics/YYYY/MM/DD/{dataset_id}.json
    """
    root = base_dir / "data" / "topics"
    n = 0
    for i in range(7):
        d = datetime.utcnow().date() - timedelta(days=i)
        p = root / f"{d.year:04d}" / f"{d.month:02d}" / f"{d.day:02d}" / f"{dataset_id}.json"
        payload = _safe_read_json(p)
        if isinstance(payload, list):
            for t in payload:
                if isinstance(t, dict) and str(t.get("topic_id", "")) == topic_id:
                    n += 1
    return int(n)
