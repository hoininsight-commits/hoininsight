import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any

class IssueSignalIndexGenerator:
    """
    (IS-48) Generates latest_index.json as the Single Source of Truth (SSOT).
    """
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.packs_dir = base_dir / "data" / "issuesignal" / "packs"
        self.packs_dir.mkdir(parents=True, exist_ok=True)

    def generate(self, cards: List[Dict[str, Any]], run_date_kst: str = None) -> Path:
        """
        Generates latest_index.json based on today's run results.
        """
        now = datetime.now() + timedelta(hours=9) # KST
        if not run_date_kst:
            run_date_kst = now.strftime("%Y-%m-%d")
        
        run_ts_kst = now.strftime("%Y-%m-%d %H:%M:%S")

        topics_total = len(cards)
        topics_active = len([c for c in cards if c.get("status") == "TRUST_LOCKED"])
        topics_hold = len([c for c in cards if c.get("status") == "HOLD"])
        topics_silent = len([c for c in cards if c.get("status") == "SILENT_DROP"])
        
        # Calculate reason counts
        reason_counts = {}
        for c in cards:
            if c.get("status") != "TRUST_LOCKED":
                reason = c.get("reason_code") or "UNKNOWN"
                reason_counts[reason] = reason_counts.get(reason, 0) + 1
        
        # Sort and get top 5
        top_reasons = sorted(reason_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        top_reason_counts = [{"reason": r, "count": c} for r, c in top_reasons]

        pinned_topic_ids = [c.get("topic_id") for c in cards if c.get("status") == "TRUST_LOCKED"][:3]

        # Define paths (Relative to project root for flexibility)
        index_path = self.packs_dir / "latest_index.json"
        
        # Latest Pointer (Internal use)
        latest_pointer = self.packs_dir / "latest.json"
        
        index_data = {
            "run_date_kst": run_date_kst,
            "run_ts_kst": run_ts_kst,
            "topics_total": topics_total,
            "topics_active": topics_active,
            "topics_hold": topics_hold,
            "topics_silent": topics_silent,
            "top_reason_counts": top_reason_counts,
            "pinned_topic_ids": pinned_topic_ids,
            "paths": {
                "dashboard_json": "data/issuesignal/dashboard.json",
                "packs_root": "data/issuesignal/packs/",
                "hoin_today": f"data/decision/{run_date_kst.replace('-', '/')}/final_decision_card.json"
            }
        }

        with open(index_path, "w", encoding="utf-8") as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)

        # Update latest pointer
        with open(latest_pointer, "w", encoding="utf-8") as f:
            json.dump({"latest_index": str(index_path.relative_to(self.base_dir))}, f)

        print(f"[SSOT] Generated: {index_path}")
        return index_path

if __name__ == "__main__":
    # Test script
    gen = IssueSignalIndexGenerator(Path("."))
    gen.generate([])
