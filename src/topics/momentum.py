from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Tuple

def _safe_read_json(p: Path) -> Any:
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None

def _date_path(d: datetime.date) -> str:
    return f"{d.year:04d}/{d.month:02d}/{d.day:02d}"

def collect_scores_7d(base_dir: Path, dataset_id: str, topic_id: str) -> List[Tuple[str, float]]:
    """
    Returns list of (ymd_str, score) for last 7 days where topic_id exists.
    ymd_str: YYYY-MM-DD
    """
    out: List[Tuple[str, float]] = []
    root = base_dir / "data" / "topics"
    for i in range(6, -1, -1):  # oldest -> newest
        d = datetime.utcnow().date() - timedelta(days=i)
        p = root / _date_path(d) / f"{dataset_id}.json"
        payload = _safe_read_json(p)
        if isinstance(payload, list):
            for t in payload:
                if isinstance(t, dict) and str(t.get("topic_id", "")) == topic_id:
                    s = t.get("score", None)
                    if isinstance(s, (int, float)):
                        out.append((f"{d.year:04d}-{d.month:02d}-{d.day:02d}", float(s)))
    return out

def compute_momentum_7d(base_dir: Path, dataset_id: str, topic_id: str) -> Dict[str, Any]:
    """
    slope based momentum:
      slope >= +0.50 => UP
      slope <= -0.50 => DOWN
      else => FLAT
    """
    series = collect_scores_7d(base_dir, dataset_id, topic_id)
    if len(series) < 2:
        return {"momentum": "FLAT", "slope": 0.0, "n": len(series), "multiplier": 1.0}

    first = series[0][1]
    last = series[-1][1]
    denom = max(1, len(series) - 1)
    slope = (last - first) / float(denom)

    if slope >= 0.50:
        mom = "UP"
        mult = 1.10
    elif slope <= -0.50:
        mom = "DOWN"
        mult = 0.90
    else:
        mom = "FLAT"
        mult = 1.00

    return {"momentum": mom, "slope": float(slope), "n": len(series), "multiplier": float(mult)}
