"""
Phase 31-C: Proposal Review Queue Indexer
Scans recent proposals and checks for approval files.
Generates a queue manifest for review and merger tools.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

# Configurations
PROPOSAL_BASE = Path("data/narratives/proposals")
APPROVAL_BASE = Path("data/narratives/approvals")
QUEUE_BASE = Path("data/narratives/queue")
LOOKBACK_DAYS = 7

def _get_utc_ymd(delta_days: int = 0) -> str:
    d = datetime.now() - timedelta(days=delta_days)
    return d.strftime("%Y/%m/%d")

def scan_proposals(base_dir: Path) -> List[Dict[str, Any]]:
    queue_items = []
    
    # Scan last N days (including today)
    for i in range(LOOKBACK_DAYS + 1):
        ymd = _get_utc_ymd(i)
        p_dir = PROPOSAL_BASE / ymd
        
        if not p_dir.exists():
            continue
            
        for p_file in p_dir.glob("proposal_*.md"):
            try:
                # Parse Video ID from filename: proposal_<video_id>.md
                # Assuming video_id doesn't contain underscores ideally, but split strategy needs care.
                # Filename format: proposal_VIDEOID.md
                filename = p_file.stem
                if not filename.startswith("proposal_"):
                    continue
                
                video_id = filename[9:] # strip 'proposal_'
                
                # Check for Approval File
                # Layout: approvals/YYYY/MM/DD/approve_<video_id>.yml
                # But approval might happen on a DIFFERENT day than proposal.
                # The prompt says: data/narratives/approvals/YYYY/MM/DD/approve_<video_id>.yml
                # We must search for the approval file. Since we don't know the approval date,
                # we might need to scan all approval dirs or just check if "any" approval exists?
                # However, the user prompt implies a specific path structure.
                # Let's assume we scan the approval directory recursively or check "anywhere".
                # For efficiency, let's just search the whole APPROVAL_BASE for the filename.
                
                approval_status = "PENDING"
                approval_file = None
                approval_data = None
                
                expected_approve_name = f"approve_{video_id}.yml"
                found_approvals = list(APPROVAL_BASE.rglob(expected_approve_name))
                
                if found_approvals:
                    # Pick the latest one if multiple (unlikely)
                    approval_file = found_approvals[0]
                    approval_status = "APPROVED"
                    
                    # Read minimal info
                    try:
                        import yaml
                        with open(approval_file, 'r', encoding='utf-8') as f:
                            approval_data = yaml.safe_load(f)
                    except ImportError:
                        # Fallback simple parse
                        content = approval_file.read_text(encoding='utf-8')
                        approval_data = {}
                        for line in content.splitlines():
                            if ":" in line:
                                k, v = line.split(":", 1)
                                approval_data[k.strip()] = v.strip().strip('"')
                                
                item = {
                    "video_id": video_id,
                    "proposal_date": ymd,
                    "proposal_path": str(p_file),
                    "status": approval_status,
                    "approval_file": str(approval_file) if approval_file else None,
                    "apply_config": approval_data.get("apply", {}) if approval_data else None
                }
                queue_items.append(item)
                
            except Exception as e:
                print(f"[Queue] Error processing {p_file}: {e}")
                continue

    return queue_items

def generate_queue_output(items: List[Dict[str, Any]], output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. JSON
    json_path = output_dir / "proposal_queue.json"
    json_path.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding='utf-8')
    
    # 2. Markdown (Human Readable)
    md_lines = ["# Proposal Review Queue", f"Generated at: {datetime.now().isoformat()}", ""]
    
    if not items:
        md_lines.append("No proposals found in the last 7 days.")
    else:
        md_lines.append("| Date | Video ID | Status | Actions |")
        md_lines.append("|---|---|---|---|")
        for it in items:
            actions = []
            if it['apply_config']:
                for k, v in it['apply_config'].items():
                    if str(v).lower() == 'true':
                        actions.append(k)
            action_str = ", ".join(actions) if actions else "-"
            
            md_lines.append(f"| {it['proposal_date']} | {it['video_id']} | **{it['status']}** | {action_str} |")
            
    md_path = output_dir / "proposal_queue.md"
    md_path.write_text("\n".join(md_lines), encoding='utf-8')

def main():
    base_dir = Path(__file__).parent.parent.parent
    global PROPOSAL_BASE, APPROVAL_BASE, QUEUE_BASE
    
    # Re-root paths
    PROPOSAL_BASE = base_dir / PROPOSAL_BASE
    APPROVAL_BASE = base_dir / APPROVAL_BASE
    QUEUE_BASE = base_dir / QUEUE_BASE
    
    print(f"[Queue] Scanning proposals in {PROPOSAL_BASE}...")
    items = scan_proposals(base_dir)
    
    # Output to today's queue folder
    today_ymd = _get_utc_ymd(0)
    output_dir = QUEUE_BASE / today_ymd
    
    generate_queue_output(items, output_dir)
    print(f"[Queue] Generated queue with {len(items)} items at {output_dir}")

if __name__ == "__main__":
    main()
