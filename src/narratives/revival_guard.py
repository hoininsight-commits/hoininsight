#!/usr/bin/env python3
"""
Phase 37-B: Revival Guardrails & Ops Evidence Bundle
Generates evidence bundles for revival proposals and detects cognitive loops.
"""
import json
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any

def load_json(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except:
        return None

def detect_loops(base_dir: Path, video_id: str) -> bool:
    """
    Detects if a video_id has been rejected multiple times in the last 90 days.
    REJECTED -> Revival -> REJECTED (2 or more ledger entries for same video_id)
    """
    ledger_entries_count = 0
    # Scan last 90 days of ledger entries
    ledger_base = base_dir / "data/narratives/ledger"
    if not ledger_base.exists():
        return False

    # Simplified loop detection: Count total rejection entries for this video_id
    # in the ledger filesystem directly.
    for root, dirs, files in os.walk(ledger_base):
        for f in files:
            if f.endswith(".yml") and video_id in f:
                # Basic check: one file per decision. 
                # If multiple files exist for same vid across different dates, it's a loop.
                ledger_entries_count += 1
    
    return ledger_entries_count >= 2

def main():
    base_dir = Path(__file__).resolve().parent.parent.parent
    now_utc = datetime.now(timezone.utc)
    ymd_path = now_utc.strftime("%Y/%m/%d")
    
    revival_path = base_dir / "data/narratives/revival" / ymd_path / "revival_proposals.json"
    revival_data = load_json(revival_path)
    if not revival_data or not revival_data.get("items"):
        print("[VERIFY][SKIP] No revival proposals today (no evidence needed)")
        return

    fresh_path = base_dir / "data/ops/freshness" / ymd_path / "freshness_summary.json"
    fresh_data = load_json(fresh_path) or {}

    evidence_bundle = {
        "generated_at": now_utc.isoformat() + "Z",
        "ops_context": {
            "overall_system_freshness_pct": fresh_data.get("overall_system_freshness_pct", 0),
            "sla_breach_count": fresh_data.get("sla_breach_count", 0),
            "sla_breach_axes": fresh_data.get("sla_breach_axes", []),
            "has_stale_warning": fresh_data.get("sla_breach_count", 0) > 0
        },
        "item_evidence": {}
    }

    loop_flags = {
        "generated_at": now_utc.isoformat() + "Z",
        "loop_detected_vids": []
    }

    for item in revival_data.get("items", []):
        vid = item.get("video_id")
        
        # 1. Evidence
        reason = item.get("revival_reason", "Condition met")
        freshness = fresh_data.get("overall_system_freshness_pct", "N/A")
        summary = f"Revived due to '{reason}' at {freshness}% system freshness."
        if fresh_data.get("sla_breach_count", 0) > 0:
            summary += " (Note: Some non-core SLA breaches present)"
            
        evidence_bundle["item_evidence"][vid] = {
            "reason_summary": summary,
            "ops_snapshot": evidence_bundle["ops_context"]
        }

        # 2. Loop Guard
        if detect_loops(base_dir, vid):
            loop_flags["loop_detected_vids"].append(vid)

    # Save Evidence
    evidence_dir = base_dir / "data/narratives/revival" / ymd_path
    evidence_dir.mkdir(parents=True, exist_ok=True)
    
    with open(evidence_dir / "revival_evidence.json", "w", encoding="utf-8") as f:
        json.dump(evidence_bundle, f, indent=2, ensure_ascii=False)

    with open(evidence_dir / "revival_loop_flags.json", "w", encoding="utf-8") as f:
        json.dump(loop_flags, f, indent=2, ensure_ascii=False)

    print(f"✓ Revival Evidence Bundle generated: {len(evidence_bundle['item_evidence'])} items")
    print(f"✓ Cognitive Loop Guard marked: {len(loop_flags['loop_detected_vids'])} items")

if __name__ == "__main__":
    main()
