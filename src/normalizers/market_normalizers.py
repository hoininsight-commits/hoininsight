from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Dict, List

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

def _write_csv(p: Path, data: List[Dict[str, Any]], fields: List[str]):
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data)

def _generic_normalize(raw_id: str, curated_path: str, entity: str, unit: str, metric: str, source: str):
    """
    Reads raw jsonl (date, value/price/close/yield) and writes timestamps_v1 csv
    """
    # Find latest raw file
    base_raw = Path("data/raw") / raw_id
    if not base_raw.exists():
        print(f"[WARN] No raw data for {raw_id}")
        return

    # Just pick the last file for simplicity or iterate?
    # For daily pipeline, we usually process 'today' or 'latest'.
    # We'll iter all generic jsonl files and combine? 
    # Or just grab the latest.
    files = sorted(base_raw.glob("*.jsonl"))
    if not files:
        print(f"[WARN] No .jsonl files in {base_raw}")
        return

    all_rows = []
    for f in files:
        items = _read_jsonl(f)
        for item in items:
            # Map item to schema
            # Schema: entity, timestamp, metric, value, unit, source
            val = item.get("close") or item.get("price") or item.get("yield") or 0.0
            
            # Timestamp: "YYYY-MM-DD" -> "YYYY-MM-DDT00:00:00Z" ? 
            # Existing schema usually expects ISO. 
            d = item.get("date", "")
            ts = f"{d}T00:00:00Z" if len(d) == 10 else d
            
            row = {
                "entity": entity,
                "timestamp": ts,
                "metric": metric,
                "value": val,
                "unit": unit,
                "source": source
            }
            all_rows.append(row)

    # Dedupe?
    # Simple dedupe by timestamp + entity
    unique_map = {}
    for r in all_rows:
        unique_map[r["timestamp"]] = r
    
    final_rows = sorted(unique_map.values(), key=lambda x: x["timestamp"])
    
    # Write
    out = Path(curated_path)
    fields = ["entity", "timestamp", "metric", "value", "unit", "source"]
    _write_csv(out, final_rows, fields)
    print(f"[OK] Normalized {raw_id} -> {curated_path}")

# --- Entry Points ---

def normalize_nasdaq():
    _generic_normalize("index_nasdaq_ndx_stooq", "data/curated/indices/nasdaq.csv", "NDX", "INDEX", "close", "stooq")

def normalize_dxy():
    _generic_normalize("fx_dxy_index_stooq", "data/curated/fx/dxy.csv", "DXY", "INDEX", "close", "stooq")

def normalize_us02y():
    _generic_normalize("rates_us02y_yield_ustreasury", "data/curated/rates/us02y.csv", "US02Y", "PCT", "yield", "treasury")

def normalize_wti():
    _generic_normalize("comm_wti_crude_oil_stooq", "data/curated/commodities/wti.csv", "WTI", "USD", "close", "stooq")

def normalize_platinum():
    _generic_normalize("metal_platinum_xptusd_stooq", "data/curated/metals/platinum.csv", "XPTUSD", "USD", "close", "stooq")

def normalize_eth():
    _generic_normalize("crypto_eth_usd_spot_coingecko", "data/curated/crypto/eth_usd.csv", "ETHUSD", "USD", "spot_price", "coingecko")
