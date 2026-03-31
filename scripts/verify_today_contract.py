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
    
    topics = []
    if isinstance(data, list):
        topics = data
    elif isinstance(data, dict):
        if "picks" in data:
            topics = data["picks"]
        elif "top_topics" in data:
            topics = data["top_topics"]
        elif "title" in data:
            topics = [data]
            
    if not topics:
        print("❌ ERROR: No topics found in today.json (checked 'picks', 'top_topics', and root list)")
        sys.exit(1)
        
    for i, t in enumerate(topics):
        if "intensity" not in t:
            print(f"❌ ERROR: Topic #{i} ({t.get('title', 'No Title')}) missing 'intensity' field")
            sys.exit(1)
            
    print(f"✅ data cards intensity check passed ({len(topics)} topics found in today.json)")

if __name__ == "__main__":
    verify()
