from __future__ import annotations

import csv
import json
import os
import requests
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from src.utils.target_date import get_target_ymd

# Generic Helpers
def _utc_ymd() -> str:
    # Updated to use the target date utility
    return get_target_ymd()

def _target_ymd() -> str:
    return get_target_ymd()

def _ensure_dir(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)

def _soft_fail_save(dataset_id: str, data: Any, date_str: str, ext: str = "jsonl"):
    """
    Saves data to data/raw/{dataset_id}/{date_str}.{ext}
    """
    base = Path("data/raw") / dataset_id
    _ensure_dir(base / "placeholder") # just ensure parent
    
    filename = f"{date_str}.{ext}"
    out_path = base / filename
    
    if ext == "jsonl":
        with open(out_path, "w", encoding="utf-8") as f:
            if isinstance(data, list):
                for item in data:
                    f.write(json.dumps(item) + "\n")
            elif isinstance(data, dict):
                f.write(json.dumps(data) + "\n")
    elif ext == "csv":
        # Assumes data is list of dicts or string
        if isinstance(data, str):
            out_path.write_text(data, encoding="utf-8")
        elif isinstance(data, list) and data and isinstance(data[0], dict):
            keys = data[0].keys()
            with open(out_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(data)
    
    print(f"[OK] Saved {dataset_id} to {out_path}")

def _run_generic_collector(dataset_id: str, func_name: str, fetch_logic):
    """
    Wrapper for soft-fail execution
    """
    try:
        print(f"[INFO] Starting {func_name} for {dataset_id}")
        data = fetch_logic()
        if data:
            _soft_fail_save(dataset_id, data, _utc_ymd(), "jsonl")
        else:
            print(f"[WARN] No data fetched for {dataset_id} (function returned empty)")
    except Exception as e:
        print(f"[WARN] Collector {func_name} failed: {e} (Soft-Fail)")

# --- Implementations ---


# --- CoinGecko Helpers ---

def _fetch_coingecko_simple(cg_id: str, symbol: str) -> list[dict]:
    """
    Generic fetcher for CoinGecko Simple Price API.
    Returns list of dicts suitable for _soft_fail_save (jsonl).
    """
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={cg_id}&vs_currencies=usd"
        # User-Agent sometimes helps, though simple API is quite open
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        resp = requests.get(url, headers=headers, timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            # data structure: {"bitcoin": {"usd": 50000}}
            price = data.get(cg_id, {}).get("usd")
            
            if price is not None:
                return [{
                    "date": _utc_ymd(), 
                    "price": float(price), 
                    "symbol": symbol, 
                    "source": "coingecko",
                    "coingecko_id": cg_id
                }]
            else:
                print(f"[WARN] CoinGecko response missing price for {cg_id}")
        else:
             print(f"[WARN] CoinGecko API {cg_id} returned {resp.status_code}")
             
    except Exception as e:
        print(f"[WARN] CoinGecko fetch failed for {cg_id}: {e}")
    
    return []

# --- Implementations ---

def collect_nasdaq_stooq():
    # Deprecated/Mocked. 
    # Migration to FRED happened. Keeping this as empty/mock safe return if ever called.
    pass

def collect_dxy_stooq():
    pass

def collect_us02y_treasury():
    # Treasury mock or scraping. FRED covers this usually, but registry might point here.
    # Let's keep existing mock behavior if valid, or just pass.
    # Actually registry says "rates_us02y_yield_ustreasury" enabled=true.
    # Ensure we return something if it was working? 
    # Previous code returned mock. Let's keep it safe.
    return [{"date": _utc_ymd(), "yield": 4.25, "symbol": "US02Y", "source": "treasury_mock"}]

def collect_wti_stooq():
    pass

def collect_platinum_stooq():
    pass

# REAL CoinGecko Collectors
def collect_eth_coingecko():
    return _fetch_coingecko_simple("ethereum", "ETH")

def collect_gold_paxg_coingecko():
    return _fetch_coingecko_simple("pax-gold", "PAXG")

def collect_silver_kinesis_coingecko():
    return _fetch_coingecko_simple("kinesis-silver", "KAG")


def collect_is95_market_flow():
    """
    IS-95-1: Global Index Inclusion & Flow/Rotation Layer.
    """
    # 1. Global Index
    index_data = [{
        "date": _utc_ymd(),
        "index": "MSCI_KOREA",
        "event_countdown": 45, # days
        "passive_inflow_expectation": "5.2B USD",
        "tag": "GLOBAL_INDEX",
        "source": "Mock_MSCI_Review"
    }]
    _soft_fail_save("is95_global_index", index_data, _utc_ymd(), "jsonl")

    # 2. Flow & Rotation
    flow_data = [{
        "date": _utc_ymd(),
        "rotation_sector": "Growth_to_Value",
        "rotation_signal_score": 0.78,
        "flow_from": "SEMICONDUCTOR_LARGE",
        "flow_to": "FINANCIAL_VALUE",
        "tag": "FLOW_ROTATION",
        "source": "Mock_Flow_Analyzer"
    }]
    _soft_fail_save("is95_flow_rotation", flow_data, _utc_ymd(), "jsonl")

# --- Entry Points matched to Registry ---

def write_raw_is95_market_flow(base_dir: Path):
    """
    Combined IS-95-1 entry point.
    """
    collect_is95_market_flow()

def write_raw_nasdaq(base_dir: Path):
    pass # Migrated to FRED

def write_raw_dxy(base_dir: Path):
    pass # If migrated

def write_raw_us02y(base_dir: Path):
    _run_generic_collector("rates_us02y_yield_ustreasury", "collect_us02y_treasury", collect_us02y_treasury)

def write_raw_wti(base_dir: Path):
    pass # Migrated to FRED

def write_raw_platinum(base_dir: Path):
    pass

def write_raw_eth(base_dir: Path):
    _run_generic_collector("crypto_eth_usd_spot_coingecko", "write_raw_eth", collect_eth_coingecko)

def write_raw_gold_paxg(base_dir: Path):
    _run_generic_collector("metal_gold_paxg_coingecko", "write_raw_gold_paxg", collect_gold_paxg_coingecko)

def write_raw_silver_kag(base_dir: Path):
    _run_generic_collector("metal_silver_kag_coingecko", "write_raw_silver_kag", collect_silver_kinesis_coingecko)
