from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
from datetime import datetime

# Adjust paths
import sys
sys.path.append(os.getcwd())

from src.events.collectors import earnings, policy, flow, contract, capital
from src.events.validate import validate_evidence
from src.events.normalize import normalize_event

def main():
    parser = argparse.ArgumentParser(description="Step 9: Modular Event Build Orchestrator")
    parser.add_argument("--as-of-date", default=datetime.now().strftime("%Y-%m-%d"), help="YYYY-MM-DD")
    args = parser.parse_args()
    
    as_of_date = args.as_of_date
    print(f"[*] Starting Event Build for {as_of_date}...")
    
    # 1. Collection (S1~S5)
    collector_map = {
        "earnings": earnings.collect,
        "policy": policy.collect,
        "flow": flow.collect,
        "contract": contract.collect,
        "capital": capital.collect
    }
    
    raw_events = []
    for e_type, collect_fn in collector_map.items():
        print(f"  [>] Collecting {e_type}...")
        try:
            batch = collect_fn()
            for item in batch:
                item["_type_hint"] = e_type # Pass to normalizer
                raw_events.append(item)
        except Exception as e:
            print(f"  [!] Failed to collect {e_type}: {e}")
            
    # 2. Validation (HARD FILTER)
    valid_events = []
    for raw in raw_events:
        if validate_evidence(raw):
            valid_events.append(raw)
        else:
            print(f"  [DROP] No evidence for: {raw.get('title')}")
            
    # 3. Normalization
    normalized_events = []
    for valid in valid_events:
        try:
            norm = normalize_event(valid, as_of_date)
            normalized_events.append(norm)
        except Exception as e:
            print(f"  [!] Normalization failed for {valid.get('title')}: {e}")
            
    # 4. Save (events.json)
    # Output path based on as-of-date convention: data/events/YYYY/MM/DD/events.json
    out_dir = Path("data") / "events" / as_of_date.replace("-", "/")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    payload = {
        "schema_version": "gate_events_v1",
        "as_of_date": as_of_date,
        "events": normalized_events[:5] # Limit to 0~5 events as per mandate
    }
    
    out_path = out_dir / "events.json"
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    
    print(f"[OK] Saved {len(normalized_events[:5])} events to {out_path}")

if __name__ == "__main__":
    main()
