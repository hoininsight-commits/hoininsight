from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from src.topics.scoring import load_regime_signals, compute_regime_multiplier

def _utc_now() -> str:
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

def _ymd() -> str:
    return datetime.utcnow().strftime("%Y/%m/%d")

def _read_json(p: Path) -> Any:
    return json.loads(p.read_text(encoding="utf-8"))

def select_topics(base_dir: Path, dataset_id: str, report_key: str) -> Path:
    """
    Topic selector (topic_v1 output).
    Reads anomalies json and emits topics.json for the dataset.
    Score v2: abs(roc_1d)*100 * regime_multiplier(VIX, US10Y).
    """
    ymd = _ymd()
    anomalies_path = base_dir / "data" / "features" / "anomalies" / ymd / f"{dataset_id}.json"
    payload = _read_json(anomalies_path)

    # Robust handling: payload might be a dict or a list of dicts
    data: Dict[str, Any] = {}
    if isinstance(payload, list):
        if len(payload) > 0 and isinstance(payload[-1], dict):
            # If list, use the last item (assuming mostly recent)
            data = payload[-1]
    elif isinstance(payload, dict):
        data = payload

    roc = data.get("roc_1d", 0.0)
    try:
        roc = float(roc)
    except Exception:
        roc = 0.0

    base_score = float(abs(roc) * 100.0)

    regime = load_regime_signals(base_dir)
    mult, mult_meta = compute_regime_multiplier(regime)
    score = float(base_score * mult)

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
            "base_score": base_score,
            "regime": mult_meta,
            "anomalies_path": anomalies_path.as_posix(),
        },
        "rationale": "Topic generated from anomaly signal (roc_1d) with regime multiplier (VIX/US10Y).",
        "links": [],
    }

    out_dir = base_dir / "data" / "topics" / ymd
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{dataset_id}.json"
    out_path.write_text(json.dumps([topic], ensure_ascii=False, indent=2), encoding="utf-8")
    return out_path
