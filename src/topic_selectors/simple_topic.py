from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

from src.topics.scoring import load_regime_signals, compute_regime_multiplier

def _utc_now() -> str:
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

def _ymd() -> str:
    return datetime.utcnow().strftime("%Y/%m/%d")

def _read_json(p: Path) -> Any:
    return json.loads(p.read_text(encoding="utf-8"))

def select_topics(base_dir: Path, dataset_id: str, report_key: str) -> Path:
    """
    Topic selector (Compatible with Z-Score Anomaly Model).
    Reads anomalies json and emits topics.json for the dataset.
    Score: Derived from Severity (0-100) * Regime Multiplier.
    """
    ymd = _ymd()
    anomalies_path = base_dir / "data" / "features" / "anomalies" / ymd / f"{dataset_id}.json"
    
    if not anomalies_path.exists():
        # No anomalies file -> No topic
        return None

    payload = _read_json(anomalies_path)
    
    # 1. Parse Anomaly Event
    event: Dict[str, Any] = {}
    
    if isinstance(payload, list):
        if len(payload) > 0 and isinstance(payload[-1], dict):
            # Use the latest event
            event = payload[-1]
    elif isinstance(payload, dict):
        event = payload
        
    # If no event found (empty list), return empty/low score
    if not event:
        # Create a placeholder "No Anomaly" topic?
        # Actually, if there is NO anomaly, we should probably output nothing or a 0-score keeper.
        # But previous system outputted 0-score. Let's keep 0-score for continuity unless dashboard filters it.
        severity_val = 0
        evidence = {}
        level = "NORMAL"
        anomaly_type = "NONE"
    else:
        severity_val = event.get("severity", 0)
        evidence = event.get("evidence", {})
        level = event.get("level", "NORMAL")
        anomaly_type = event.get("anomaly_type", "UNKNOWN")

    # 2. Calculate Score
    # Map Severity (0-100) to simple Topic Score (0-10?)
    # L1=30, L2=60, L3=90
    base_score = float(severity_val) / 10.0 # 3.0, 6.0, 9.0
    
    regime = load_regime_signals(base_dir)
    mult, mult_meta = compute_regime_multiplier(regime)
    
    final_score = float(base_score * mult)

    # 3. Determine Human-readable Severity
    if final_score >= 6.0: # L2 * 1.0
        final_severity = "HIGH"
    elif final_score >= 3.0: # L1
        final_severity = "MED"
    else:
        final_severity = "LOW"

    # 4. Construct Topic
    evidence_summary = evidence.get("reasoning", str(evidence))
    
    topic = {
        "ts_utc": _utc_now(),
        "dataset_id": dataset_id,
        "topic_id": f"{dataset_id}::{anomaly_type.lower()}",
        "title": f"{report_key} {level} Signal" if level != "NORMAL" else f"{report_key} (Normal)",
        "score": final_score,
        "severity": final_severity,
        "evidence": {
            "source_severity": severity_val,
            "level": level,
            "details": evidence,
            "regime": mult_meta,
            "anomalies_path": anomalies_path.as_posix(),
        },
        "rationale": f"[{level}] {evidence_summary} (Regime x{mult:.1f})",
        "links": [],
    }

    out_dir = base_dir / "data" / "topics" / ymd
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{dataset_id}.json"
    out_path.write_text(json.dumps([topic], ensure_ascii=False, indent=2), encoding="utf-8")
    return out_path
