from __future__ import annotations
import csv
import json
import random
from pathlib import Path
from typing import Any, List, Dict
from datetime import datetime, timedelta

# Common Utility
def get_target_ymd() -> str:
    return datetime.now().strftime("%Y-%m-%d")

def _ensure_dir(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)

def _save_csv(dataset_name: str, data: List[Dict], filename: str = "data.csv"):
    date_str = get_target_ymd()
    base_dir = Path(f"data/raw/policy/{dataset_name}/{date_str}")
    _ensure_dir(base_dir / filename)
    
    out_path = base_dir / filename
    
    if not data:
        return

    keys = data[0].keys()
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)
    
    print(f"[OK] Saved {dataset_name} to {out_path}")

# --- Mock Generators ---

def collect_fomc_calendar():
    """
    Mock: FOMC Meeting Schedule
    """
    # Assuming standard 8 meetings a year
    data = [{
        "date": get_target_ymd(),
        "event": "FOMC Meeting",
        "scheduled_date": "2026-01-28", # Hypothetical
        "importance": "High",
        "expected_action": "Rate Hold",
        "source": "Mock_Fed_Calendar"
    }, {
        "date": get_target_ymd(),
        "event": "FOMC Meeting",
        "scheduled_date": "2026-03-18",
        "importance": "High",
        "expected_action": "Rate Cut 25bp",
        "source": "Mock_Fed_Calendar"
    }]
    _save_csv("fomc_calendar", data, "schedule.csv")

def collect_key_economic_events():
    """
    Mock: CPI/PCE/NFP Release Schedule
    """
    today = datetime.now()
    data = [{
        "date": get_target_ymd(),
        "event": "US CPI Release",
        "scheduled_date": (today + timedelta(days=5)).strftime("%Y-%m-%d"),
        "consensus": "3.1%",
        "previous": "3.2%",
        "source": "Mock_Investing_com"
    }, {
         "date": get_target_ymd(),
        "event": "Non-Farm Payrolls",
        "scheduled_date": (today + timedelta(days=12)).strftime("%Y-%m-%d"),
        "consensus": "150K",
        "previous": "180K",
        "source": "Mock_Investing_com"
    }]
    _save_csv("economic_calendar", data, "events.csv")

def collect_is95_policy_flow():
    """
    IS-95-1: Strategic Policy Flow (KR/US)
    Capture Govt Roadmap vs Execution data.
    """
    today = datetime.now()
    data = [{
        "date": get_target_ymd(),
        "policy_id": "KR_VALUE_UP_2026",
        "title": "Corporate Value-up Program Phase 2",
        "status": "ANNOUNCED",
        "target_sector": "ALL_MARKET",
        "tag": "KR_POLICY",
        "metrics": {
            "policy_commitment_score": 0.85,
            "policy_execution_gap": 0.20
        },
        "source": "Gov_Press_Release"
    }, {
        "date": get_target_ymd(),
        "policy_id": "US_CHIPS_ACT_EXT",
        "title": "CHIPS Act Ecosystem Expansion Fund",
        "status": "EXECUTION",
        "target_sector": "SEMICONDUCTOR",
        "tag": "US_POLICY",
        "metrics": {
            "policy_commitment_score": 0.95,
            "policy_execution_gap": 0.05
        },
        "source": "US_Commerce_Dept"
    }]
    _save_csv("is95_policy_flow", data, "observation_layer.csv")

# --- Entry Point ---

def run_collector():
    print(">>> Starting Policy/Event Collector (Mock)...")
    collect_fomc_calendar()
    collect_key_economic_events()
    collect_is95_policy_flow()
    print("<<< Policy Collection Complete.\n")

if __name__ == "__main__":
    run_collector()
