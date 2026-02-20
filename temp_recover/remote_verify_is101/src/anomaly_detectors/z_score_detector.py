from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import numpy as np
import pandas as pd

@dataclass
class AnomalyEvent:
    ts_utc: str
    dataset_id: str
    entity: str
    anomaly_type: str
    severity: int # 0-100, mapped from L1(30)/L2(60)/L3(90)
    level: str # L1, L2, L3
    evidence: dict

def _utc_date_parts() -> tuple[str, str, str]:
    return (
        datetime.now().strftime("%Y"),
        datetime.now().strftime("%m"),
        datetime.now().strftime("%d"),
    )

def detect_z_score(base_dir: Path, dataset_id: str, curated_csv: Path, entity: str) -> Path:
    """
    Implements ANOMALY_DETECTION_LOGIC v1.11 standards.
    - L1: |Z| >= 1.5 OR Percentile > 90%
    - L2: |Z| >= 2.0 OR Percentile > 95%
    """
    df = pd.read_csv(curated_csv)
    df["ts_utc"] = pd.to_datetime(df["ts_utc"], utc=True, errors="coerce")
    df = df.dropna(subset=["ts_utc"]).sort_values("ts_utc")
    
    if len(df) < 20: 
        # Not enough data for reliable stats
        return None

    # Calculate Rolling Stats (20-day window for Z-score)
    window = 20
    df['rolling_mean'] = df['value'].rolling(window=window).mean()
    df['rolling_std'] = df['value'].rolling(window=window).std()
    
    # Calculate Z-Score
    # Avoid div/0
    df['z_score'] = (df['value'] - df['rolling_mean']) / df['rolling_std'].replace(0, np.nan)
    
    # Calculate Percentile Rank (1-year window ~ 252 days)
    rank_window = 252
    df['percentile'] = df['value'].rolling(window=rank_window).apply(
        lambda x: (pd.Series(x).rank().iloc[-1] / len(x)) * 100, raw=False
    )

    # Analyze Latest Data Point
    last = df.iloc[-1]
    last_z = float(last['z_score']) if pd.notnull(last['z_score']) else 0.0
    last_p = float(last['percentile']) if pd.notnull(last['percentile']) else 50.0
    
    level = "NORMAL"
    severity = 0
    reasoning = []

    # Logic Implementation
    # L2 Condition
    if abs(last_z) >= 2.0:
        level = "L2"
        severity = 60
        reasoning.append(f"Z-Score {last_z:.2f} >= 2.0")
    elif last_p >= 95 or last_p <= 5:
        level = "L2"
        severity = 60
        reasoning.append(f"Percentile {last_p:.1f}% (Extreme)")
    # L1 Condition
    elif abs(last_z) >= 1.5:
        level = "L1"
        severity = 30
        reasoning.append(f"Z-Score {last_z:.2f} >= 1.5")
    elif last_p >= 90 or last_p <= 10:
        level = "L1"
        severity = 30
        reasoning.append(f"Percentile {last_p:.1f}% (Watch)")

    events = []
    if level != "NORMAL":
        events.append(
            AnomalyEvent(
                ts_utc=datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                dataset_id=dataset_id,
                entity=entity,
                anomaly_type="Z_SCORE_MODEL_V1",
                severity=severity,
                level=level,
                evidence={
                    "z_score": round(last_z, 2),
                    "percentile": round(last_p, 1),
                    "value": float(last['value']),
                    "rolling_mean_20d": float(last['rolling_mean']) if pd.notnull(last['rolling_mean']) else 0,
                    "reasoning": " + ".join(reasoning)
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
