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
    level: str
    evidence: dict

def _utc_date_parts() -> tuple[str, str, str]:
    return (
        datetime.utcnow().strftime("%Y"),
        datetime.utcnow().strftime("%m"),
        datetime.utcnow().strftime("%d"),
    )

def detect_event_nonzero(base_dir: Path, dataset_id: str, curated_csv: Path, entity: str) -> Path:
    """
    Simple detector for Event Counts (e.g. Filings).
    If latest value > 0, it's an Event -> Anomaly (L2).
    """
    if not curated_csv.exists():
        return None

    df = pd.read_csv(curated_csv)
    df["ts_utc"] = pd.to_datetime(df["ts_utc"], utc=True, errors="coerce")
    df = df.dropna(subset=["ts_utc"]).sort_values("ts_utc")
    
    if df.empty:
        return None

    last = df.iloc[-1]
    val = float(last['value'])
    
    events = []
    
    if val > 0:
        # Event Detected!
        events.append(
            AnomalyEvent(
                ts_utc=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                dataset_id=dataset_id,
                entity=entity,
                anomaly_type="EVENT_NONZERO",
                severity=60, # L2
                level="L2",
                evidence={
                    "value": val,
                    "threshold": 0,
                    "reasoning": f"New Event Detected (Count={int(val)})"
                },
            ).__dict__
        )
    else:
        # Save "Normal" state anyway so reports know it was checked? 
        # Usually z_score_detector only saves if anomaly (except recent update).
        # But report code expects JSON to exist to show "Low/Normal" status?
        # Let's save a "Normal" event if 0.
        events.append(
            AnomalyEvent(
                ts_utc=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                dataset_id=dataset_id,
                entity=entity,
                anomaly_type="EVENT_NONZERO",
                severity=0,
                level="NORMAL",
                evidence={
                    "value": val,
                    "threshold": 0,
                    "reasoning": "No Events"
                },
            ).__dict__
        )

    # Output
    y, m, d = _utc_date_parts()
    out_dir = base_dir / "data" / "features" / "anomalies" / y / m / d
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{dataset_id}.json"
    out_path.write_text(json.dumps(events, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_path
