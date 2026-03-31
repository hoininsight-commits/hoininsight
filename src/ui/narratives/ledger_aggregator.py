#!/usr/bin/env python3
"""
Phase 35: Rejection Ledger Aggregator

기록(ledger) + 표시(UI) + 중복경고만 수행.
자동 삭제/수정/승인 금지.
"""
import json
import yaml
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from src.utils.guards import check_learning_enabled


def load_ledger_entries(base_dir: Path, lookback_days: int = 90) -> List[Dict[str, Any]]:
    """Load all ledger entries from the last N days."""
    entries = []
    today = datetime.now().date()
    
    for i in range(lookback_days):
        check_date = today - timedelta(days=i)
        ymd_path = check_date.strftime("%Y/%m/%d")
        
        ledger_dir = base_dir / "data" / "narratives" / "ledger" / ymd_path
        if not ledger_dir.exists():
            continue
        
        # Load all ledger_*.yml files
        for ledger_file in ledger_dir.glob("ledger_*.yml"):
            try:
                data = yaml.safe_load(ledger_file.read_text(encoding="utf-8"))
                if not data:
                    continue
                
                # Validate required fields
                if "video_id" not in data or "decision" not in data:
                    continue
                
                # Add metadata
                data["_ledger_file"] = str(ledger_file.relative_to(base_dir))
                data["_discovered_date"] = check_date.strftime("%Y-%m-%d")
                
                entries.append(data)
            except Exception as e:
                print(f"[WARN] Failed to load ledger {ledger_file}: {e}")
                continue
    
    return entries


def build_duplicate_map(entries: List[Dict[str, Any]]) -> Dict[str, str]:
    """Build a map of video_id -> related_video_id for DUPLICATE decisions."""
    duplicate_map = {}
    
    for entry in entries:
        if entry.get("decision") == "DUPLICATE":
            video_id = entry.get("video_id")
            related = entry.get("related_video_id", "")
            if video_id and related:
                duplicate_map[video_id] = related
    
    return duplicate_map


def count_by_decision(entries: List[Dict[str, Any]]) -> Dict[str, int]:
    """Count entries by decision type."""
    counts = {
        "REJECTED": 0,
        "DEFERRED": 0,
        "DUPLICATE": 0,
        "OTHER": 0
    }
    
    for entry in entries:
        decision = entry.get("decision", "OTHER")
        if decision in counts:
            counts[decision] += 1
        else:
            counts["OTHER"] += 1
    
    return counts


def aggregate_ledger(base_dir: Path, lookback_days: int = 90) -> Dict[str, Any]:
    """Aggregate ledger entries and generate summary."""
    entries = load_ledger_entries(base_dir, lookback_days)
    
    # Sort by decided_at (most recent first)
    entries.sort(key=lambda x: x.get("decided_at", ""), reverse=True)
    
    # Build summary
    summary = {
        "ledger_summary_version": "phase35_v1",
        "generated_at": datetime.now().isoformat() + "Z",
        "lookback_days": lookback_days,
        "total_entries": len(entries),
        "counts_by_decision": count_by_decision(entries),
        "duplicate_map": build_duplicate_map(entries),
        "recent_entries": entries[:20]  # Top 20 most recent
    }
    
    return summary


def main():
    """Main entry point for ledger aggregation."""
    check_learning_enabled()
    base_dir = Path(__file__).parent.parent.parent
    
    # Configuration
    lookback_days = 90
    
    # Aggregate ledger
    summary = aggregate_ledger(base_dir, lookback_days)
    
    # Save output
    ymd = datetime.now().strftime("%Y/%m/%d")
    output_dir = base_dir / "data" / "narratives" / "ledger_summary" / ymd
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = output_dir / "ledger_summary.json"
    output_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    
    print(f"✓ Ledger aggregation complete: {output_path}")
    print(f"  - Total entries: {summary['total_entries']}")
    print(f"  - Counts: {summary['counts_by_decision']}")


if __name__ == "__main__":
    main()
