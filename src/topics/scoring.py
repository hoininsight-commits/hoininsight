from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Tuple

def _ymd() -> str:
    return datetime.utcnow().strftime("%Y/%m/%d")

def _read_json(p: Path) -> Any:
    return json.loads(p.read_text(encoding="utf-8"))

def _safe_get_roc_1d(payload: Any) -> float | None:
    if isinstance(payload, dict) and "roc_1d" in payload:
        try:
            return float(payload["roc_1d"])
        except Exception:
            return None
    return None

def load_regime_signals(base_dir: Path) -> Dict[str, float]:
    """
    Load regime anomaly signals (roc_1d) for VIX and US10Y.
    Returns dict like {"vix_roc_1d": 0.012, "us10y_roc_1d": -0.004}
    Missing files -> empty dict.
    """
    ymd = _ymd()
    out: Dict[str, float] = {}

    vix_path = base_dir / "data" / "features" / "anomalies" / ymd / "risk_vix_index_stooq.json"
    if vix_path.exists():
        try:
            out["vix_roc_1d"] = float(_read_json(vix_path).get("roc_1d"))
        except Exception:
            pass

    us10y_path = base_dir / "data" / "features" / "anomalies" / ymd / "rates_us10y_yield_ustreasury.json"
    if us10y_path.exists():
        try:
            out["us10y_roc_1d"] = float(_read_json(us10y_path).get("roc_1d"))
        except Exception:
            pass

    return out

def compute_regime_multiplier(regime: Dict[str, float]) -> Tuple[float, Dict[str, Any]]:
    """
    Simple regime multiplier:
      - if abs(vix_roc_1d) >= 0.01 -> *1.5
      - if abs(us10y_roc_1d) >= 0.005 -> *1.2
      - if both -> *1.8
    """
    vix = regime.get("vix_roc_1d")
    us10y = regime.get("us10y_roc_1d")

    vix_on = isinstance(vix, (int, float)) and abs(float(vix)) >= 0.01
    us10y_on = isinstance(us10y, (int, float)) and abs(float(us10y)) >= 0.005

    mult = 1.0
    if vix_on and us10y_on:
        mult = 1.8
    elif vix_on:
        mult = 1.5
    elif us10y_on:
        mult = 1.2

    meta = {
        "vix_roc_1d": vix,
        "us10y_roc_1d": us10y,
        "vix_on": bool(vix_on),
        "us10y_on": bool(us10y_on),
        "multiplier": float(mult),
        "rule": {
            "vix_threshold": 0.01,
            "us10y_threshold": 0.005,
            "mult_map": {"both": 1.8, "vix": 1.5, "us10y": 1.2, "none": 1.0},
        },
    }
    return float(mult), meta
