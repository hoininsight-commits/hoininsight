#!/usr/bin/env python3
import json
import sys
from pathlib import Path

def verify():
    path = Path("docs/data/decision/today.json")
    if not path.exists():
        print(f"❌ ERROR: {path} not found")
        sys.exit(1)
        
    try:
        data = json.load(path.open(encoding="utf-8"))
    except Exception as e:
        print(f"❌ ERROR: Failed to parse JSON: {e}")
        sys.exit(1)
        
    if "picks" not in data:
        print("❌ ERROR: 'picks' key missing in today.json")
        sys.exit(1)
        
    for i, pick in enumerate(data["picks"]):
        if "intensity" not in pick:
            print(f"❌ ERROR: Pick #{i} missing 'intensity' field")
            sys.exit(1)
            
    print("✅ data cards intensity check passed (today.json)")

if __name__ == "__main__":
    verify()
