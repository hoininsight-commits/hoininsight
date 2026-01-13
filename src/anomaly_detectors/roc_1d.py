from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import pandas as pd

@dataclass
class AnomalyEvent:
    ts_utc: str
    dataset_id: str
    entity: str
    anomaly_type: str
    severity: int
    evidence: dict

def _utc_date_parts() -> tuple[str, str, str]:
    return (
        datetime.utcnow().strftime("%Y"),
        datetime.utcnow().strftime("%m"),
        datetime.utcnow().strftime("%d"),
    )

def detect_roc_1d(base_dir: Path, dataset_id: str, curated_csv: Path, entity: str, threshold_pct: float = 3.0) -> Path:
    df = pd.read_csv(curated_csv)
    df["ts_utc"] = pd.to_datetime(df["ts_utc"], utc=True, errors="coerce")
    df = df.dropna(subset=["ts_utc"]).sort_values("ts_utc")

    events = []
    if len(df) >= 2:
        last = df.iloc[-1]
        prev = df.iloc[-2]
        roc = (float(last["value"]) - float(prev["value"])) / float(prev["value"]) * 100.0
        if abs(roc) >= threshold_pct:
            sev = min(100, int(abs(roc) * 10))
            events.append(
                AnomalyEvent(
                    ts_utc=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                    dataset_id=dataset_id,
                    entity=entity,
                    anomaly_type="ROC_1D",
                    severity=sev,
                    evidence={
                        "threshold_pct": threshold_pct,
                        "roc_pct": roc,
                        "prev_ts": str(prev["ts_utc"]),
                        "prev_value": float(prev["value"]),
                        "last_ts": str(last["ts_utc"]),
                        "last_value": float(last["value"]),
                    },
                ).__dict__
            )

    y, m, d = _utc_date_parts()
    out_dir = base_dir / "data" / "features" / "anomalies" / y / m / d
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{dataset_id}.json"
    out_path.write_text(json.dumps(events, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_path
