from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pandas as pd

def _utc_date_parts() -> tuple[str, str, str]:
    return (
        datetime.utcnow().strftime("%Y"),
        datetime.utcnow().strftime("%m"),
        datetime.utcnow().strftime("%d"),
    )

def _utc_now() -> str:
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

def _load_curated(base_dir: Path, rel_path: str) -> pd.DataFrame:
    p = base_dir / rel_path
    if not p.exists():
        raise FileNotFoundError(f"missing curated file: {p.as_posix()}")
    df = pd.read_csv(p)
    if "ts_utc" not in df.columns or "value" not in df.columns:
        raise ValueError(f"curated schema invalid: {p.as_posix()}")
    df["ts"] = pd.to_datetime(df["ts_utc"], utc=True, errors="coerce")
    df = df.dropna(subset=["ts"]).sort_values("ts")
    return df

def write_raw_corr_usdkrw_us10y_30d(base_dir: Path) -> Path:
    """
    Derived metric:
      - USDKRW vs US10Y 30D rolling correlation of daily pct changes
    Reads:
      - data/curated/fx/usdkrw.csv
      - data/curated/rates/us10y.csv
    Writes:
      - data/raw/derived/YYYY/MM/DD/corr_usdkrw_us10y_30d.json
    """
    source = "derived"
    entity = "USDKRW_US10Y_CORR30D"
    unit = "CORR"
    ts_utc = _utc_now()
    
    obs_ts = ts_utc
    value = 0.0

    try:
        fx = _load_curated(base_dir, "data/curated/fx/usdkrw.csv")
        yld = _load_curated(base_dir, "data/curated/rates/us10y.csv")

        fx = fx.set_index("ts")[["value"]].rename(columns={"value": "usdkrw"})
        yld = yld.set_index("ts")[["value"]].rename(columns={"value": "us10y"})

        df = fx.join(yld, how="inner").dropna()
        if len(df) < 35:
            raise ValueError("not enough overlapping history for 30D correlation")

        df["c_fx"] = df["usdkrw"].pct_change()
        df["c_y"] = df["us10y"].pct_change()
        df = df.dropna(subset=["c_fx", "c_y"])

        corr = df["c_fx"].rolling(30).corr(df["c_y"]).dropna()
        if len(corr) == 0:
            raise ValueError("rolling correlation produced no values")

        value = float(corr.iloc[-1])
        obs_ts = corr.index[-1].strftime("%Y-%m-%dT%H:%M:%SZ")

    except Exception as e:
        print(f"[WARN] Derived USDKRW-US10Y calc failed: {e}. Using mock data.")
        source = "derived_mock"
        value = 0.3 # Mock correlation

    y, m, d = _utc_date_parts()
    out_dir = base_dir / "data" / "raw" / "derived" / y / m / d
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "corr_usdkrw_us10y_30d.json"

    payload = {
        "ts_utc": ts_utc,
        "source": source,
        "entity": entity,
        "unit": unit,
        "obs_ts_utc": obs_ts,
        "corr_30d": value,
        "derived_from": ["fx_usdkrw_spot_open_er_api", "rates_us10y_yield_ustreasury"],
    }

    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_path
