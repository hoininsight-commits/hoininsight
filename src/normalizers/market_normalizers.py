from __future__ import annotations

import json
import pandas as pd
from pathlib import Path
from typing import Any, Dict, List

from src.normalizers.common_timeseries import build_row

def _read_jsonl(p: Path) -> List[Dict[str, Any]]:
    if not p.exists():
        return []
    out = []
    with open(p, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    out.append(json.loads(line))
                except:
                    pass
    return out

def _generic_normalize(dataset_id: str, curated_path: str, entity: str, unit: str, metric: str, source: str):
    """
    Reads raw jsonl (date, value/price/close/yield) and writes timestamps_v1 csv
    """
    # Find latest raw file
    base_raw = Path("data/raw") / dataset_id
    if not base_raw.exists():
        print(f"[WARN] No raw data for {dataset_id}")
        return

    files = sorted(base_raw.glob("*.jsonl"))
    if not files:
        print(f"[WARN] No .jsonl files in {base_raw}")
        return

    all_rows = []
    for f in files:
        items = _read_jsonl(f)
        for item in items:
            val = item.get("close") or item.get("price") or item.get("yield") or 0.0
            
            # Timestamp: "YYYY-MM-DD" -> "YYYY-MM-DDT00:00:00Z" ? 
            d = item.get("date", "")
            # Ensure ISO format (T00:00:00Z) if just date
            ts = f"{d}T00:00:00Z" if len(d) == 10 and "T" not in d else d
            
            if not ts:
                continue

            # source override from item if present (e.g. mock)
            item_src = item.get("source", source)

            row = build_row(
                ts_utc=ts,
                entity=entity,
                value=float(val),
                unit=unit,
                source=item_src,
                dataset_id=dataset_id,
                metric_name=metric,
                is_derived=False,
                derived_from=""
            )
            all_rows.append(row)

    if not all_rows:
        return

    # Dedupe using fingerprint logic (relying on pandas)
    df = pd.DataFrame(all_rows)
    
    out = Path(curated_path)
    if out.exists():
        try:
            old_df = pd.read_csv(out)
            df = pd.concat([old_df, df], ignore_index=True)
        except:
            pass
            
    # Dedupe by fingerprint, keep last
    if "fingerprint" in df.columns:
        df = df.drop_duplicates(subset=["fingerprint"], keep="last")
    
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"[OK] Normalized {dataset_id} -> {curated_path}")

# --- Entry Points ---

def normalize_nasdaq(base_dir: Path):
    _generic_normalize("index_nasdaq_ndx_stooq", "data/curated/indices/nasdaq.csv", "NDX", "INDEX", "close", "stooq")

def normalize_dxy(base_dir: Path):
    _generic_normalize("fx_dxy_index_stooq", "data/curated/fx/dxy.csv", "DXY", "INDEX", "close", "stooq")

def normalize_us02y(base_dir: Path):
    _generic_normalize("rates_us02y_yield_ustreasury", "data/curated/rates/us02y.csv", "US02Y", "PCT", "yield", "treasury")

def normalize_wti(base_dir: Path):
    _generic_normalize("comm_wti_crude_oil_stooq", "data/curated/commodities/wti.csv", "WTI", "USD", "close", "stooq")

def normalize_platinum(base_dir: Path):
    _generic_normalize("metal_platinum_xptusd_stooq", "data/curated/metals/platinum.csv", "XPTUSD", "USD", "close", "stooq")

def normalize_eth(base_dir: Path):
    _generic_normalize("crypto_eth_usd_spot_coingecko", "data/curated/crypto/eth_usd.csv", "ETHUSD", "USD", "spot_price", "coingecko")
