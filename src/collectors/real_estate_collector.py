from __future__ import annotations
import csv
import json
import os
import requests
import xmltodict
from pathlib import Path
from typing import Any, List, Dict
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load Env
load_dotenv()
DATA_GO_KR_API_KEY = os.getenv("DATA_GO_KR_API_KEY")

# Common Utility
def get_target_ymd() -> str:
    return datetime.now().strftime("%Y-%m-%d")

def _ensure_dir(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)

def _save_csv(dataset_name: str, data: List[Dict], filename: str = "data.csv"):
    date_str = get_target_ymd()
    base_dir = Path(f"data/raw/real_estate/{dataset_name}/{date_str}")
    _ensure_dir(base_dir / filename)
    
    out_path = base_dir / filename
    
    if not data:
        print(f"[INFO] No data found for {dataset_name}")
        return

    keys = data[0].keys()
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)
    
    print(f"[OK] Saved {dataset_name} to {out_path} ({len(data)} rows)")

# --- Real Collectors ---

def collect_apt_transaction_price(lawd_cd: str = "11680", deal_ym: str = None):
    """
    Collect Apartment Transaction Data from MOLIT (Public Data Portal)
    API: RTMSDataSvcAptTradeDev
    lawd_cd: Region Code (11680 = Gangnam-gu, 11110 = Jongno-gu)
    deal_ym: YYYYMM (Default: Current Month)
    """
    if not DATA_GO_KR_API_KEY:
        print("[WARN] DATA_GO_KR_API_KEY not found. Skipping Real Estate collection.")
        return

    if not deal_ym:
        deal_ym = datetime.now().strftime("%Y%m")

    # URL for "Apartment Transaction Details" (Updated to Data.go.kr Standard Gateway)
    # Old: http://openapi.molit.go.kr/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptTradeDev
    # New: https://apis.data.go.kr/1613000/RTMSDataSvcAptTradeDev/getRTMSDataSvcAptTradeDev
    url = "https://apis.data.go.kr/1613000/RTMSDataSvcAptTradeDev/getRTMSDataSvcAptTradeDev"
    
    params = {
        "serviceKey": DATA_GO_KR_API_KEY, # Decoding Key provided
        "LAWD_CD": lawd_cd,
        "DEAL_YMD": deal_ym,
        "numOfRows": 1000,
        "pageNo": 1
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    print(f">>> [Real] Fetching Apartment Transactions for Region {lawd_cd}, {deal_ym}...")
    
    try:
        # Note: requests sometimes double-encodes the key if passed in params dict.
        # It's safer to pass the unencoded key if using 'serviceKey' in requests params?
        # Actually user said "Decoding Key", which is the raw string before URL encoding. 
        # Requests 'params' automatically URL-encodes values. So using Decoding key is correct.
        
        resp = requests.get(url, params=params, headers=headers)
        
        # Public Portal usually returns XML
        data_dict = xmltodict.parse(resp.content)
        
        # Valid response check
        header = data_dict.get("response", {}).get("header", {})
        if header.get("resultCode") != "00":
             print(f"[ERROR] API Error: {header.get('resultMsg')}")
             return

        body = data_dict.get("response", {}).get("body", {})
        items_wrapper = body.get("items")
        
        if not items_wrapper:
            print("[INFO] No transactions found.")
            return

        items = items_wrapper.get("item")
        if isinstance(items, dict):
            items = [items] # Normalize single item to list
            
        cleaned_data = []
        for item in items:
            cleaned_data.append({
                "date": get_target_ymd(),
                "deal_date": f"{item.get('년')}-{item.get('월')}-{item.get('일')}",
                "region_code": lawd_cd,
                "apt_name": item.get("아파트"),
                "area_exclusive": item.get("전용면적"),
                "floor": item.get("층"),
                "price_str": item.get("거래금액"),
                "price_raw": int(item.get("거래금액", "0").replace(",", "").strip()),
                "construction_year": item.get("건축년도"),
                "source": "MOLIT_API"
            })
            
        _save_csv(f"transaction_{lawd_cd}", cleaned_data, f"apt_trade_{deal_ym}.csv")

    except Exception as e:
        print(f"[ERROR] Real Estate API Failed: {e}")
        try:
            print(f"[DEBUG] Raw Response: {resp.text[:500]}")
        except:
            pass
        
        # Fallback to Mock
        print(">>> [System] Falling back to MOCK Data Generation...")
        collect_housing_price_index()
        collect_transaction_volume()
        collect_unsold_inventory()


# --- Mock Generators (Restored for Fallback) ---

def collect_housing_price_index():
    print("   [Mock] Generating Price Index...")
    data = [{
        "date": get_target_ymd(),
        "region": "Nationwide",
        "apt_price_index": 90.5,
        "source": "Mock_Fallback"
    }]
    _save_csv("housing_price_index", data, "price_index.csv")

def collect_transaction_volume():
    print("   [Mock] Generating Volume Data...")
    data = [{
        "date": get_target_ymd(),
        "region": "Nationwide",
        "transaction_count": 2500,
        "source": "Mock_Fallback"
    }]
    _save_csv("transaction_volume", data, "volume.csv")

def collect_unsold_inventory():
    print("   [Mock] Generating Unsold Inventory...")
    data = [{
        "date": get_target_ymd(),
        "region": "Nationwide",
        "unsold_units": 62000,
        "source": "Mock_Fallback"
    }]
    _save_csv("unsold_inventory", data, "unsold.csv")

# --- Entry Point ---

def run_collector():
    print(">>> Starting Real Estate Collector (Hybrid)...")
    # Try Real, Fallback to Mock if fail
    collect_apt_transaction_price("11680") # Gangnam
    print("<<< Real Estate Collection Complete.\n")

if __name__ == "__main__":
    run_collector()
