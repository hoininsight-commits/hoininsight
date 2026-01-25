#!/usr/bin/env python3
"""
Phase 36: Auto-Archive (Non-destructive)

판단을 정리하는 Phase. 엔진의 기억은 보존하되, 운영자의 인지 부하만 줄임.
자동 삭제 금지, 기존 파일 수정 금지, Non-destructive Archive만 허용.
"""
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from src.utils.guards import check_learning_enabled


def should_archive_ledger_entry(entry: Dict[str, Any], today: datetime) -> tuple[bool, str]:
    """Determine if a ledger entry should be archived."""
    decision = entry.get("decision")
    
    # REJECTED and DUPLICATE are always archivable
    if decision in ["REJECTED", "DUPLICATE"]:
        return True, f"Auto-archive: {decision} decision"
    
    # DEFERRED with expired expires_at
    if decision == "DEFERRED":
        expires_at = entry.get("expires_at", "")
        if expires_at:
            try:
                expires_date = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
                if expires_date.date() < today.date():
                    return True, f"Auto-archive: DEFERRED expired on {expires_at[:10]}"
            except:
                pass
    
    return False, ""


def build_archive_summary(base_dir: Path) -> Dict[str, Any]:
    """Build archive summary from ledger entries."""
    # Load ledger summary
    ymd = datetime.utcnow().strftime("%Y/%m/%d")
    ledger_path = base_dir / "data" / "narratives" / "ledger_summary" / ymd / "ledger_summary.json"
    
    if not ledger_path.exists():
        return {
            "archive_version": "phase36_v1",
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "total_archived": 0,
            "archived_items": []
        }
    
    ledger_data = json.loads(ledger_path.read_text(encoding="utf-8"))
    recent_entries = ledger_data.get("recent_entries", [])
    
    # Determine which entries should be archived
    today = datetime.utcnow()
    archived_items = []
    
    for entry in recent_entries:
        should_archive, reason = should_archive_ledger_entry(entry, today)
        
        if should_archive:
            archived_item = {
                "video_id": entry.get("video_id"),
                "original_decision": entry.get("decision"),
                "decided_at": entry.get("decided_at"),
                "decided_by": entry.get("decided_by", ""),
                "reason": entry.get("reason", ""),
                "related_video_id": entry.get("related_video_id", ""),
                "archive_reason": reason,
                "archived_at": datetime.utcnow().isoformat() + "Z",
                "original_ledger_file": entry.get("_ledger_file", ""),
                "non_destructive": True  # Original file preserved
            }
            archived_items.append(archived_item)
    
    return {
        "archive_version": "phase36_v1",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "total_archived": len(archived_items),
        "archived_items": archived_items
    }


def verify_non_destructive(base_dir: Path, archived_items: List[Dict[str, Any]]) -> bool:
    """Verify that original files still exist (non-destructive check)."""
    all_preserved = True
    
    for item in archived_items:
        original_file = item.get("original_ledger_file", "")
        if original_file:
            file_path = base_dir / original_file
            if not file_path.exists():
                print(f"[WARN] Original file missing: {original_file}")
                all_preserved = False
    
    return all_preserved


def main():
    """Main entry point for auto-archive."""
    check_learning_enabled()
    base_dir = Path(__file__).parent.parent.parent
    
    # Build archive summary
    archive_summary = build_archive_summary(base_dir)
    
    # Verify non-destructive
    if archive_summary["total_archived"] > 0:
        is_preserved = verify_non_destructive(base_dir, archive_summary["archived_items"])
        archive_summary["non_destructive_verified"] = is_preserved
    
    # Save archive summary
    ymd = datetime.utcnow().strftime("%Y/%m/%d")
    output_dir = base_dir / "data" / "narratives" / "archive" / ymd
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = output_dir / "archive_summary.json"
    output_path.write_text(json.dumps(archive_summary, indent=2, ensure_ascii=False), encoding="utf-8")
    
    print(f"✓ Auto-archive complete: {output_path}")
    print(f"  - Total archived: {archive_summary['total_archived']}")
    if archive_summary["total_archived"] > 0:
        print(f"  - Non-destructive verified: {archive_summary.get('non_destructive_verified', False)}")


if __name__ == "__main__":
    main()
