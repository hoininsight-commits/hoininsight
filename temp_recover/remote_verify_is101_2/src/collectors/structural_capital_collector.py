import csv
import json
import os
import requests
from pathlib import Path
from typing import Any, List, Dict
from datetime import datetime, timedelta
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load Env
load_dotenv()
DART_API_KEY = os.getenv("OPENDART_API_KEY")

# Common Utility
def get_target_ymd() -> str:
    return datetime.now().strftime("%Y-%m-%d")

def _ensure_dir(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)

def _save_csv(dataset_name: str, data: List[Dict], filename: str = "data.csv"):
    date_str = get_target_ymd()
    base_dir = Path(f"data/raw/structural_capital/{dataset_name}/{date_str}")
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

def collect_keyword_filings(keyword: str, days: int = 3) -> List[Dict]:
    """
    Search DART for specific keywords (e.g., '보호예수', '블록딜')
    API: list.json
    """
    if not DART_API_KEY:
        print("[WARN] OPENDART_API_KEY not found. Skipping DART collection.")
        return []

    end_dt = datetime.now().strftime("%Y%m%d")
    start_dt = (datetime.now() - timedelta(days=days)).strftime("%Y%m%d")
    
    url = "https://opendart.fss.or.kr/api/list.json"
    params = {
        "crtfc_key": DART_API_KEY,
        "bgn_de": start_dt,
        "end_de": end_dt,
        "page_count": 100,
        "pblntf_detail_ty": "I001" # 수시공시 (주요사항보고서 등)
    }
    
    all_filings = []
    
    try:
        resp = requests.get(url, params=params)
        data = resp.json()
        
        if data.get("status") == "000":
            items = data.get("list", [])
            for item in items:
                report_nm = item.get("report_nm", "")
                # Simple Keyword Filter
                if keyword in report_nm:
                    all_filings.append({
                        "date": get_target_ymd(),
                        "rcept_dt": item.get("rcept_dt"),
                        "corp_name": item.get("corp_name"),
                        "report_nm": report_nm,
                        "corp_code": item.get("corp_code"),
                        "source": "OpenDART_API"
                    })
    except Exception as e:
        print(f"[ERROR] DART API Failed: {e}")

    return all_filings


def collect_lockup_release(base_dir: Path = None):
    print(">>> [Real] Fetching Lock-up/Mezzanine Filings from DART...")
    # Keywords: '전환사채', '신주인수권', '보호예수' (Note: '보호예수' is often inside text, but sometimes in title '특수관계인...')
    # Finding 'Protected' release is hard via title alone.
    # Searching for "주요사항보고서" (Major Reports) related to Capital actions.
    
    # 1. CB/BW Issuance or Conversion (frequent precursor to exit)
    cb_data = collect_keyword_filings("전환사채", days=5)
    _save_csv("cb_bw_filings", cb_data, "cb_bw.csv")
    
    # 2. Block Deal / Disposal (Title often contains '처분')
    disposal_data = collect_keyword_filings("처분", days=5)
    _save_csv("disposal_filings", disposal_data, "disposal.csv")


def collect_block_deals_krx(base_dir: Path = None):
    print(">>> [Real] Fetching Block Deals (Market Data) via PyKRX...")
    try:
        # Use T-1 (Yesterday) as today's data might not be ready in the morning
        target_date = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
        
        # We will collect "Foreigner Net Buy Top 10" as a proxy for Capital Flow.
        try:
            from pykrx import stock
            df = stock.get_market_net_purchases_of_equities_by_ticker(target_date, target_date, "FOREIGNER")
        except ImportError:
            print("[ERROR] 'pykrx' library not found. Skipping KRX block deal collection.")
            return
        
        if df.empty:
            print(f"[WARN] No PyKRX data for {target_date}")
            return

        # Check if column exists (handling potential English/Korean env differences or API changes)
        target_col = "순매수거래대금"
        if target_col not in df.columns:
            print(f"[WARN] Column {target_col} not found in PyKRX data. Cols: {df.columns}")
            return

        # Returns DataFrame. We take top 10 rows.
        top_10 = df.sort_values(by=target_col, ascending=False).head(10)
        
        results = []
        for ticker, row in top_10.iterrows():
            name = stock.get_market_ticker_name(ticker)
            results.append({
                "date": get_target_ymd(),
                "data_date": target_date,
                "ticker": ticker,
                "name": name,
                "net_buy_amount": row[target_col],
                "source": "KRX_Foreigner_Flow"
            })
            
        _save_csv("foreigner_capital_flow", results, "top10_flow.csv")
        
    except Exception as e:
        print(f"[ERROR] PyKRX Failed: {e}")


def collect_pef_exits():
    # PEF data is not easily available via OpenDART List API (requires specialized scraping).
    # Keeping this MOCK for now, or using a simple heuristic on title '펀드'.
    # For stability, we keep this as 'Manual/Mock' logic or simple DART search.
    pass

# --- Entry Point ---

def run_collector():
    print(">>> Starting Structural Capital Collector (Real)...")
    collect_lockup_release()
    collect_block_deals_krx()
    # collect_pef_exits()
    print("<<< Structural Capital Collection Complete.\n")

if __name__ == "__main__":
    run_collector()
