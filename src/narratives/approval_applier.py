"""
Phase 31-C: Approval Applier
Reads the Proposal Queue and applies approved additive changes to documentation.
Strictly Additive Only.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Constants
TARGET_FILES = {
    "data_collection_master": "docs/DATA_COLLECTION_MASTER.md",
    "anomaly_detection_logic": "docs/ANOMALY_DETECTION_LOGIC.md",
    "baseline_signals": "docs/BASELINE_SIGNALS.md"
}

def load_queue(base_dir: Path) -> List[Dict]:
    ymd = datetime.utcnow().strftime("%Y/%m/%d")
    queue_path = base_dir / "data/narratives/queue" / ymd / "proposal_queue.json"
    if not queue_path.exists():
        print(f"[Applier] No queue file found for today ({ymd})")
        return []
    return json.loads(queue_path.read_text(encoding='utf-8'))

def extract_proposal_content(proposal_path: Path) -> str:
    """Extracts the 'Engine Extension Suggestions' section from proposal md."""
    if not proposal_path.exists():
        return ""
    
    content = proposal_path.read_text(encoding='utf-8')
    
    # Regex to find the suggestions block
    # Start: ## Engine Extension Suggestions
    # End: ## Safety Notice OR End of File
    
    pattern = r"(## Engine Extension Suggestions.*?)(?=## Safety Notice|$)"
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        return match.group(1).strip()
    return ""

def apply_approval(base_dir: Path, item: Dict, log: Dict):
    video_id = item['video_id']
    apply_cfg = item.get('apply_config', {})
    
    if not apply_cfg:
        log['skipped_count'] += 1
        return

    # Load approval metadata for logging
    appr_meta = {}
    try:
        # We need to reload approval file to get details like approved_by
        # Item has 'approval_file' path
        af_path = Path(item['approval_file'])
        if af_path.exists():
            # Simple parse again to avoid dependency check issues if yaml missing
            txt = af_path.read_text(encoding='utf-8')
            for line in txt.splitlines():
                if "approved_by:" in line:
                    appr_meta['by'] = line.split(":", 1)[1].strip()
                if "approved_at:" in line:
                    appr_meta['at'] = line.split(":", 1)[1].strip()
                if "source_url:" in line: # Optional
                    appr_meta['src'] = line.split(":", 1)[1].strip()
    except:
        pass

    # Proposal content to append
    prop_path = Path(item['proposal_path'])
    prop_text = extract_proposal_content(prop_path)
    if not prop_text:
        log['reasons'].append(f"{video_id}: No content extracted from proposal")
        return

    # Construct Append Block
    header = f"\n\n## [APPROVED][NARRATIVE][{video_id}]\n"
    meta_block = f"- approved_at: {appr_meta.get('at', 'Unknown')}\n"
    meta_block += f"- approved_by: {appr_meta.get('by', 'Unknown')}\n"
    meta_block += "### Proposed Additions\n"
    
    full_block = header + meta_block + prop_text + "\n"
    
    applied_any = False
    
    for key, target_rel_path in TARGET_FILES.items():
        # Check if this doc type is approved
        if str(apply_cfg.get(key, 'false')).lower() != 'true':
            continue
            
        target_path = base_dir / target_rel_path
        
        # [Rule] Only modify if file exists
        if not target_path.exists():
            log['reasons'].append(f"{video_id}: Target {key} not found ({target_rel_path})")
            continue
            
        # [Rule] Check Duplication (Fingerprint)
        current_content = target_path.read_text(encoding='utf-8')
        fingerprint = f"[APPROVED][NARRATIVE][{video_id}]"
        
        if fingerprint in current_content:
            log['reasons'].append(f"{video_id}: Already applied to {key}")
            continue
            
        # [Action] Append
        try:
            with open(target_path, "a", encoding="utf-8") as f:
                f.write(full_block)
            
            applied_any = True
            log['affected_files'].append(str(target_rel_path))
            print(f"[Applier] Applied {video_id} to {target_rel_path}")
            
        except Exception as e:
            log['reasons'].append(f"{video_id}: Write error {e}")
            
    if applied_any:
        log['applied_count'] += 1
    else:
        # If we entered here, it means we had 'apply_cfg' but maybe files didn't exist or were dupes
        # Just increment skipped?
        pass

def main():
    base_dir = Path(__file__).parent.parent.parent
    
    print("[Applier] Starting Approval Application...")
    queue = load_queue(base_dir)
    
    log = {
        "applied_count": 0, 
        "skipped_count": 0, 
        "reasons": [], 
        "affected_files": []
    }
    
    for item in queue:
        if item.get('status') == 'APPROVED':
            apply_approval(base_dir, item, log)
        else:
            log['skipped_count'] += 1
            
    # Save Log
    ymd = datetime.utcnow().strftime("%Y/%m/%d")
    log_dir = base_dir / "data/narratives/applied" / ymd
    log_dir.mkdir(parents=True, exist_ok=True)
    
    (log_dir / "applied_log.json").write_text(json.dumps(log, indent=2), encoding='utf-8')
    print(f"[Applier] Complete. Applied: {log['applied_count']}, Skipped: {log['skipped_count']}")
    
if __name__ == "__main__":
    main()
