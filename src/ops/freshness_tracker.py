#!/usr/bin/env python3
"""
Phase 36-B: Freshness Tracker & SLA Breach Guard
Calculates data latency per axis and identifies SLA breaches.
"""
import json
import yaml
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any

def get_last_modified(path: Path) -> datetime:
    """Get last modified time of a file in UTC."""
    if not path.exists():
        return datetime.min.replace(tzinfo=timezone.utc)
    mtime = os.path.getmtime(path)
    return datetime.fromtimestamp(mtime, tz=timezone.utc)

def calculate_freshness(base_dir: Path) -> Dict[str, Any]:
    dataset_path = base_dir / "registry" / "datasets.yml"
    if not dataset_path.exists():
        return {"error": "registry/datasets.yml missing"}

    with open(dataset_path, "r", encoding="utf-8") as f:
        registry = yaml.safe_load(f)
        datasets = registry.get("datasets", [])

    now = datetime.now(timezone.utc)
    freshness_items = []
    sla_breaches = []
    
    total_axes = 0
    fresh_axes = 0
    
    for ds in datasets:
        ds_id = ds.get("dataset_id")
        curated_path_str = ds.get("curated_path")
        if not curated_path_str:
            continue
            
        total_axes += 1
        curated_path = base_dir / curated_path_str
        last_collected = get_last_modified(curated_path)
        
        diff = now - last_collected
        freshness_minutes = int(diff.total_seconds() / 60)
        
        # In case of missing files (min date)
        if last_collected == datetime.min.replace(tzinfo=timezone.utc):
            freshness_minutes = 999999
            
        is_breach = freshness_minutes > (6 * 60) # 6 hours SLA
        
        item = {
            "dataset_id": ds_id,
            "last_collected_at": last_collected.isoformat() if last_collected != datetime.min.replace(tzinfo=timezone.utc) else "N/A",
            "freshness_minutes": freshness_minutes,
            "is_sla_breach": is_breach
        }
        
        freshness_items.append(item)
        if is_breach:
            sla_breaches.append(ds_id)
        else:
            fresh_axes += 1

    overall_freshness = (fresh_axes / total_axes * 100) if total_axes > 0 else 0
    
    # Get latest updated axis
    sorted_items = sorted(freshness_items, key=lambda x: x["freshness_minutes"])
    latest_axis = sorted_items[0]["dataset_id"] if sorted_items else "N/A"

    return {
        "tracker_version": "phase36b_v1",
        "generated_at": now.isoformat(),
        "overall_system_freshness_pct": round(overall_freshness, 1),
        "latest_updated_axis": latest_axis,
        "sla_breach_count": len(sla_breaches),
        "sla_breach_axes": sla_breaches,
        "axes": freshness_items
    }

def main():
    base_dir = Path(__file__).parent.parent.parent
    summary = calculate_freshness(base_dir)
    
    ymd = datetime.now(timezone.utc).strftime("%Y/%m/%d")
    out_dir = base_dir / "data" / "ops" / "freshness" / ymd
    out_dir.mkdir(parents=True, exist_ok=True)
    
    out_path = out_dir / "freshness_summary.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
        
    print(f"✓ Freshness summary generated: {out_path}")
    print(f"  - Overall Freshness: {summary.get('overall_system_freshness_pct')}%")
    print(f"  - SLA Breaches: {summary.get('sla_breach_count')}")

if __name__ == "__main__":
    main()
