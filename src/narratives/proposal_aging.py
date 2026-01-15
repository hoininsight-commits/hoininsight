"""
Phase 33: Proposal Aging & Decay Engine
Applies time-based decay to proposal scores to naturally deprioritize older proposals.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

HALF_LIFE_DAYS = 7

def _get_utc_ymd() -> str:
    return datetime.utcnow().strftime("%Y/%m/%d")

def calculate_age_days(proposal_date_str: str) -> int:
    """Calculate age in days from proposal date (YYYY/MM/DD format)."""
    try:
        proposal_date = datetime.strptime(proposal_date_str, "%Y/%m/%d")
        now = datetime.utcnow()
        delta = now - proposal_date
        return max(0, delta.days)
    except:
        return 0

def calculate_decay_factor(age_days: int) -> float:
    """Calculate decay factor using half-life formula."""
    return 0.5 ** (age_days / HALF_LIFE_DAYS)

def determine_status(base_dir: Path, video_id: str, ymd: str) -> str:
    """Determine proposal status by checking for approval/applied files."""
    # Check APPLIED
    applied_path = base_dir / "data/narratives/applied" / ymd / "applied_summary.json"
    if applied_path.exists():
        try:
            applied_data = json.loads(applied_path.read_text(encoding="utf-8"))
            applied_vids = [item.get("video_id") for item in applied_data.get("items", [])]
            if video_id in applied_vids:
                return "APPLIED"
        except:
            pass
    
    # Check APPROVED (search in approvals directory)
    approval_base = base_dir / "data/narratives/approvals"
    if approval_base.exists():
        approve_files = list(approval_base.rglob(f"approve_{video_id}.yml"))
        if approve_files:
            return "APPROVED"
    
    # Check PROPOSED (proposal file exists)
    # We assume if it's in the scoring list, it's at least PROPOSED
    return "PROPOSED"

def apply_aging(base_dir: Path):
    ymd = _get_utc_ymd()
    
    # Input: Phase 32 output
    input_path = base_dir / "data/narratives/prioritized" / ymd / "proposal_scores.json"
    
    # Output
    output_dir = base_dir / "data/narratives/prioritized" / ymd
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "proposal_scores_with_aging.json"
    
    print(f"[Aging] Starting Phase 33 Aging for {ymd}")
    
    if not input_path.exists():
        print(f"[Aging] No prioritized proposals found at {input_path}. Skipping.")
        # Write empty structure
        empty_output = {
            "aging_version": "phase33_v1",
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "half_life_days": HALF_LIFE_DAYS,
            "items": []
        }
        output_path.write_text(json.dumps(empty_output, indent=2, ensure_ascii=False), encoding="utf-8")
        return
    
    # Load Phase 32 data
    p32_data = json.loads(input_path.read_text(encoding="utf-8"))
    
    # Handle both old array format and new dict wrapper
    if isinstance(p32_data, dict) and "items" in p32_data:
        items = p32_data["items"]
    else:
        items = p32_data if isinstance(p32_data, list) else []
    
    aged_items = []
    
    for item in items:
        video_id = item.get("video_id")
        alignment_score = item.get("alignment_score", 0)
        proposal_date = item.get("proposal_date", ymd)  # Fallback to today if missing
        
        # Calculate aging metrics
        age_days = calculate_age_days(proposal_date)
        decay_factor = calculate_decay_factor(age_days)
        final_priority_score = alignment_score * decay_factor
        
        # Determine status
        status = determine_status(base_dir, video_id, ymd)
        
        aged_item = {
            "video_id": video_id,
            "alignment_score": alignment_score,
            "age_days": age_days,
            "decay_factor": round(decay_factor, 3),
            "final_priority_score": round(final_priority_score, 2),
            "status": status,
            "proposal_date": proposal_date,
            "score_breakdown": item.get("score_breakdown", ""),
            "priority_rank": item.get("priority_rank", 0)
        }
        
        aged_items.append(aged_item)
    
    # Sort by final_priority_score (descending)
    aged_items.sort(key=lambda x: x["final_priority_score"], reverse=True)
    
    # Re-assign priority ranks based on final score
    for idx, item in enumerate(aged_items, 1):
        item["final_priority_rank"] = idx
    
    # Build output
    output_data = {
        "aging_version": "phase33_v1",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "half_life_days": HALF_LIFE_DAYS,
        "items": aged_items
    }
    
    output_path.write_text(json.dumps(output_data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[Aging] Saved {len(aged_items)} aged proposals to {output_path}")

def main():
    base_dir = Path(os.getcwd())
    apply_aging(base_dir)

if __name__ == "__main__":
    main()
