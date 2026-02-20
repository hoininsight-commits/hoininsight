#!/usr/bin/env python3
"""
Phase 37: Revival Scanner
Scans REJECTED/ARCHIVED narratives and proposes reconsideration if conditions are met.
"""
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any
from src.utils.guards import check_learning_enabled

def load_json(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except:
        return None

def check_ops_conditions(base_dir: Path, ymd_path: str) -> tuple[bool, str]:
    fresh_path = base_dir / "data/ops/freshness" / ymd_path / "freshness_summary.json"
    fresh_data = load_json(fresh_path)
    if not fresh_data:
        return False, "Ops freshness data missing"

    freshness_pct = fresh_data.get("overall_system_freshness_pct", 0)
    if freshness_pct < 85:
        return False, f"System freshness too low ({freshness_pct}%)"

    sla_breaches = fresh_data.get("sla_breach_axes", [])
    
    # Import core datasets list
    import sys
    sys.path.append(str(base_dir))
    try:
        from src.ops.core_dataset import CORE_DATASETS_V2
        core_breaches = [b for b in sla_breaches if b in CORE_DATASETS_V2]
        if core_breaches:
            return False, f"Core dataset SLA breach: {', '.join(core_breaches)}"
    except ImportError:
        pass

    return True, "Ops conditions OK"

def check_regime_conditions(base_dir: Path, ymd_path: str) -> tuple[bool, str]:
    # Check for new Meta Topics today
    meta_path = base_dir / "data/meta_topics" / ymd_path / "meta_topics.json"
    meta_data = load_json(meta_path)
    if meta_data and len(meta_data) > 0:
        return True, f"New Meta Topics detected ({len(meta_data)})"

    # Check for Regime Confidence change
    regime_path = base_dir / "data/regimes/regime_history.json"
    regime_data = load_json(regime_path)
    if regime_data and "history" in regime_data:
        history = regime_data.get("history", [])
        if len(history) >= 2:
            latest = history[-1]
            previous = history[-2]
            
            latest_conf = latest.get("regime_confidence", 0)
            prev_conf = previous.get("regime_confidence", 0)
            
            if latest_conf != prev_conf:
                return True, f"Regime confidence changed: {prev_conf} -> {latest_conf}"

    return False, "No significant regime/meta change"

def scan_revival_candidates(base_dir: Path, ymd_path: str) -> List[Dict[str, Any]]:
    # Source 1: Ledger Summary
    ledger_path = base_dir / "data/narratives/ledger_summary" / ymd_path / "ledger_summary.json"
    ledger_data = load_json(ledger_path)
    
    # Source 2: Archive Summary
    archive_path = base_dir / "data/narratives/archive" / ymd_path / "archive_summary.json"
    archive_data = load_json(archive_path)

    candidates = []
    seen_vids = set()

    if ledger_data:
        for entry in ledger_data.get("recent_entries", []):
            if entry.get("decision") in ["REJECTED", "DUPLICATE"]:
                vid = entry.get("video_id")
                if vid and vid not in seen_vids:
                    candidates.append({
                        "video_id": vid,
                        "original_decision": entry.get("decision"),
                        "reason": entry.get("reason"),
                        "decided_at": entry.get("decided_at")
                    })
                    seen_vids.add(vid)

    if archive_data:
        for entry in archive_data.get("archived_items", []):
            vid = entry.get("video_id")
            if vid and vid not in seen_vids:
                candidates.append({
                    "video_id": vid,
                    "original_decision": entry.get("original_decision"),
                    "reason": entry.get("reason"),
                    "decided_at": entry.get("decided_at")
                })
                seen_vids.add(vid)

    return candidates

def main():
    check_learning_enabled()
    base_dir = Path(__file__).resolve().parent.parent.parent
    now_utc = datetime.now(timezone.utc)
    ymd_path = now_utc.strftime("%Y/%m/%d")
    
    # 1. Check Conditions
    ops_ok, ops_msg = check_ops_conditions(base_dir, ymd_path)
    if not ops_ok:
        print(f"[-] Revival skipped: {ops_msg}")
        return

    regime_ok, regime_msg = check_regime_conditions(base_dir, ymd_path)
    if not regime_ok:
        print(f"[-] Revival skipped: {regime_msg}")
        return

    print(f"[+] Conditions met: {regime_msg} / {ops_msg}")

    # 2. Scan Candidates
    candidates = scan_revival_candidates(base_dir, ymd_path)
    revival_proposals = []

    for c in candidates:
        revival_proposal = {
            "proposal_version": "revival_v1",
            "video_id": c["video_id"],
            "title": f"[REVIVAL] {c['video_id']}",
            "original_decision": c["original_decision"],
            "original_reason": c["reason"],
            "original_decided_at": c["decided_at"],
            "revival_reason": f"New Market Context: {regime_msg}",
            "generated_at": now_utc.isoformat() + "Z",
            "status": "PROPOSED_REVIVAL"
        }
        revival_proposals.append(revival_proposal)

    # 3. Save
    output_dir = base_dir / "data/narratives/revival" / ymd_path
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "revival_proposals.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "generated_at": now_utc.isoformat() + "Z",
            "condition_met": regime_msg,
            "items": revival_proposals
        }, f, indent=2, ensure_ascii=False)

    print(f"✓ Revival scan complete: {output_file}")
    print(f"  - Total candidates proposed: {len(revival_proposals)}")

if __name__ == "__main__":
    main()
