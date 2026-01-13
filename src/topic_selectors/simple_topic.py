from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

def _utc_now() -> str:
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

def _ymd() -> str:
    return datetime.utcnow().strftime("%Y/%m/%d")

def _read_json(p: Path) -> Dict[str, Any]:
    return json.loads(p.read_text(encoding="utf-8"))

def select_topics(base_dir: Path, dataset_id: str, report_key: str) -> Path:
    """
    Topic selector (topic_v1 output).
    Reads anomalies json and emits topics.json for the dataset.
    """
    ymd = _ymd()
    anomalies_path = base_dir / "data" / "features" / "anomalies" / ymd / f"{dataset_id}.json"
    payload = _read_json(anomalies_path)

    # Default score heuristic: abs(roc_1d) * 100
    roc = None
    if isinstance(payload, dict):
        roc = payload.get("roc_1d")
    if roc is None:
        roc = 0.0

    score = float(abs(float(roc)) * 100.0)
    severity = "HIGH" if score >= 3.0 else ("MED" if score >= 1.0 else "LOW")

    topic = {
        "ts_utc": _utc_now(),
        "dataset_id": dataset_id,
        "topic_id": f"{dataset_id}::roc_1d",
        "title": f"{report_key} 1D change spike" if severity != "LOW" else f"{report_key} daily move",
        "score": score,
        "severity": severity,
        "evidence": {
            "roc_1d": float(roc),
            "anomalies_path": anomalies_path.as_posix(),
        },
        "rationale": "Topic generated from anomaly signal (roc_1d).",
        "links": [],
    }

    out_dir = base_dir / "data" / "topics" / ymd
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{dataset_id}.json"
    out_path.write_text(json.dumps([topic], ensure_ascii=False, indent=2), encoding="utf-8")
    return out_path
