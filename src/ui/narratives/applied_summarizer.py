"""
Phase 31-E: Applied Change Summarizer
Consolidates applied_log.json and approval metadata into a user-friendly summary.
Used for Dashboard and Daily Reports.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
from src.utils.guards import check_learning_enabled

# Configurations
APPLIED_BASE = Path("data/narratives/applied")
APPROVAL_BASE = Path("data/narratives/approvals")
PROPOSAL_BASE = Path("data/narratives/proposals")

def load_applied_log(ymd: str) -> Dict:
    log_path = APPLIED_BASE / ymd / "applied_log.json"
    if not log_path.exists():
        return None
    return json.loads(log_path.read_text(encoding='utf-8'))

def get_approval_details(video_id: str, ymd: str) -> Dict:
    # Finding approve file can be tricky if date doesn't match exactly.
    # For now, we assume standard layout or search via search_approvals helper.
    # Let's search broadly in standard location
    # NOTE: approval might be from previous days, but applied today.
    # Let's search using rglob as fallback or standard path.
    
    # Standard: approvals/YYYY/MM/DD/approve_<video_id>.yml
    # Let's just rglob from APPROVAL_BASE
    
    candidates = list(APPROVAL_BASE.rglob(f"approve_{video_id}.yml"))
    if not candidates:
        return {}
        
    # Prefer latest
    target = sorted(candidates)[-1]
    
    meta = {}
    try:
        txt = target.read_text(encoding='utf-8')
        import yaml
        data = yaml.safe_load(txt)
        meta = data
    except ImportError:
        # Fallback manual parse
        txt = target.read_text(encoding='utf-8')
        for line in txt.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                k = k.strip()
                v = v.strip().strip('"')
                meta[k] = v
                
                # Manual fix for 'apply' block if needed? 
                # Simple parsing is fragile for nested 'apply'. 
                # But approval_applier logic already handled application.
                # Here we just need display info.
    return meta

def get_proposal_title(video_id: str) -> str:
    # Try to find proposal file to get title or just use Video ID
    candidates = list(PROPOSAL_BASE.rglob(f"proposal_{video_id}.md"))
    if not candidates:
        return f"Video {video_id}"
        
    # Read title from first line? Usually # Title
    # Or just return filename or ID. 
    # Let's try to extract title from content if possible.
    try:
        content = candidates[0].read_text(encoding='utf-8')
        first_line = content.splitlines()[0]
        return first_line.replace("#", "").strip()
    except:
        return f"Video {video_id}"

def generate_summary():
    check_learning_enabled()
    base_dir = Path(__file__).resolve().parent.parent.parent
    global APPLIED_BASE, APPROVAL_BASE, PROPOSAL_BASE
    
    # Re-root
    APPLIED_BASE = base_dir / APPLIED_BASE
    APPROVAL_BASE = base_dir / APPROVAL_BASE
    PROPOSAL_BASE = base_dir / PROPOSAL_BASE
    
    # Today
    today_ymd = datetime.now().strftime("%Y/%m/%d")
    ymd_slug = datetime.now().strftime("%Y-%m-%d")
    
    log = load_applied_log(today_ymd)
    
    summary = {
        "date": ymd_slug,
        "applied_count": 0,
        "items": []
    }
    
    if log and log.get('applied_count', 0) > 0:
        summary["applied_count"] = log['applied_count']
        
        # 'affected_files' in log is a flat list of all files? 
        # Or does applied_log structure allow per-video tracking?
        # Looking at approval_applier.py:
        # It logs "affected_files": [] globally. 
        # And "reasons" or console logs per video.
        
        # To reconstruct per-video mapping effectively, we might need 
        # to check which approvals were processed.
        # However, applied_log usually aggregates.
        # Let's infer from Queue or re-scan applied_log logic?
        # Actually `approval_applier.py` prints: [Applier] Applied {video_id} to {target_rel_path}
        # But here we only have json.
        
        # LIMITATION: current applied_log.json structure is simple aggregates.
        # For Phase 31-E, let's assume if applied_count > 0, we check the Queue of today
        # to see which items were marked "APPROVED" and successfully applied.
        
        # Load Queue
        q_path = base_dir / "data/narratives/queue" / today_ymd / "proposal_queue.json"
        if q_path.exists():
            q_data = json.loads(q_path.read_text(encoding='utf-8'))
            for item in q_data:
                if item.get('status') == 'APPROVED':
                    vid = item.get('video_id')
                    
                    # Check details
                    appr_meta = get_approval_details(vid, today_ymd)
                    
                    # Applied Scopes
                    scopes = []
                    apply_cfg = item.get('apply_config', {})
                    if not apply_cfg and appr_meta:
                        apply_cfg = appr_meta.get('apply', {})
                        
                    for k, v in apply_cfg.items():
                        if str(v).lower() == 'true':
                            scopes.append(k.upper())
                            
                    # For affected files, we can just list generic affected based on scopes
                    # or list what applied_log says globally.
                    
                    summary_item = {
                        "video_id": vid,
                        "title": get_proposal_title(vid),
                        "approved_by": appr_meta.get('approved_by', 'Unknown'),
                        "approved_at": appr_meta.get('approved_at', 'Unknown'),
                        "applied_scopes": scopes,
                        "affected_files": log.get('affected_files', []) # Shared list
                    }
                    summary["items"].append(summary_item)
    
    # Output
    out_dir = APPLIED_BASE / today_ymd
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "applied_summary.json"
    
    out_file.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"[Summarizer] Generated summary at {out_file}")

if __name__ == "__main__":
    generate_summary()
