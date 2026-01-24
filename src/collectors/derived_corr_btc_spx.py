from __future__ import annotations

import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from src.utils.target_date import get_target_parts
from src.utils.errors import WarmupError

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

def write_raw_corr_btc_spx_30d(base_dir: Path) -> Path:
    """
    Derived metric:
      - BTCUSD vs SPX 30D rolling correlation of daily returns
     Reads:
      - data/curated/crypto/btc_usd.csv
      - data/curated/indices/spx.csv
    Writes:
      - data/raw/derived/YYYY/MM/DD/corr_btc_spx_30d.json
    """
    source = "derived"
    entity = "BTC_SPX_CORR30D"
    unit = "CORR"
    ts_utc = _utc_now()
    
    obs_ts = ts_utc
    value = 0.0

    try:
        btc = _load_curated(base_dir, "data/curated/crypto/btc_usd.csv")
        spx = _load_curated(base_dir, "data/curated/indices/spx.csv")

        btc = btc.set_index("ts")[["value"]].rename(columns={"value": "btc"})
        spx = spx.set_index("ts")[["value"]].rename(columns={"value": "spx"})

        df = btc.join(spx, how="inner").dropna()
        if len(df) < 35:
            # WARMUP Requirement: 35 days history
            raise WarmupError(f"insufficient history: {len(df)}/35 days overlapping")

        # daily returns (pct_change)
        df["r_btc"] = df["btc"].pct_change()
        df["r_spx"] = df["spx"].pct_change()
        df = df.dropna(subset=["r_btc", "r_spx"])

        corr = df["r_btc"].rolling(30).corr(df["r_spx"]).dropna()
        if len(corr) == 0:
            raise WarmupError("rolling correlation produced no values")

        value = float(corr.iloc[-1])
        obs_ts = corr.index[-1].strftime("%Y-%m-%dT%H:%M:%SZ")

    except WarmupError:
        raise
    except Exception as e:
        # Standard error
        raise RuntimeError(f"Derived BTC-SPX calc failed: {e}")

    y, m, d = get_target_parts()
    out_dir = base_dir / "data" / "raw" / "derived_corr_btc_spx_30d" / y / m / d
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "corr_btc_spx_30d.json"
    
    payload = {
        "ts_utc": ts_utc,
        "source": source,
        "entity": entity,
        "unit": unit,
        "obs_ts_utc": obs_ts,
        "corr_30d": value,
        "derived_from": ["crypto_btc_usd_spot_coingecko", "index_spx_sp500_stooq"],
    }

    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_path
