import json
import os
from datetime import datetime
from pathlib import Path
from src.narratives.proposal_scorer import ProposalScorer
from src.utils.guards import check_learning_enabled

def _get_utc_ymd() -> str:
    return datetime.now().strftime("%Y/%m/%d")

def main():
    check_learning_enabled()
    base_dir = Path(os.getcwd())
    ymd = _get_utc_ymd()
    
    # Paths
    queue_path = base_dir / "data/narratives/queue" / ymd / "proposal_queue.json"
    output_dir = base_dir / "data/narratives/prioritized" / ymd
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "proposal_scores.json"
    
    print(f"[Priority] Starting Phase 32 Prioritization for {ymd}")
    
    # 1. Load Queue
    if not queue_path.exists():
        print(f"[Priority] No queue found at {queue_path}. Skipping.")
        # Write empty structure to satisfy verification and metadata reqs
        final_output = {
            "scoring_version": "phase32_v1",
            "generated_at": datetime.now().isoformat() + "Z",
            "inputs_hash": "empty_queue",
            "items": []
        }
        output_path.write_text(json.dumps(final_output, indent=2), encoding="utf-8")
        return
        
    queue_items = json.loads(queue_path.read_text(encoding="utf-8"))
    
    # 2. Get Regime Context
    regime_info = {"regime": "Unknown", "confidence": "LOW"}
    
    # Load Regime History
    rh_path = base_dir / "data/regimes" / "regime_history.json"
    if rh_path.exists():
        try:
            rh = json.loads(rh_path.read_text(encoding="utf-8"))
            if rh.get("history"):
                regime_info["regime"] = rh["history"][-1].get("regime", "Unknown")
        except: pass
        
    # Load Confidence
    # Simplified logic: check collection_status
    cs_path = base_dir / "data/dashboard" / "collection_status.json"
    if cs_path.exists():
        try:
            # Re-using the logic from regime_confidence roughly/simplified
            # Or just assume MEDIUM if we can't fully calc. 
            # Actually, let's try to import if possible, otherwise separate logic.
            # importing src.ops requires path handling.
            try:
                from src.ops.regime_confidence import calculate_regime_confidence
                res = calculate_regime_confidence(cs_path)
                regime_info["confidence"] = res.get("regime_confidence", "LOW")
            except ImportError:
                pass
        except: pass
        
    print(f"[Priority] Context: {regime_info}")
    
    # 3. Score Items
    scorer = ProposalScorer()
    scored_items = []
    
    for item in queue_items:
        vid = item.get("video_id")
        p_path_str = item.get("proposal_path")
        
        # Default text if file missing
        text = ""
        if p_path_str and os.path.exists(p_path_str):
            try:
                with open(p_path_str, "r", encoding="utf-8") as f:
                    text = f.read()
            except: pass
            
        score_res = scorer.calculate_score(text, regime_info)
        
        # Merge info
        scored_item = item.copy()
        scored_item.update(score_res)
        scored_items.append(scored_item)
        
    # 4. Sort and Rank
    # Sort by alignment_score desc
    scored_items.sort(key=lambda x: x["alignment_score"], reverse=True)
    
    # Assign Rank
    for idx, item in enumerate(scored_items, 1):
        item["priority_rank"] = idx
        
    # Calculate Input Hash
    import hashlib
    vid_list = sorted([item.get("video_id", "") for item in queue_items])
    input_str = f"{regime_info['regime']}|{regime_info['confidence']}|{','.join(vid_list)}"
    input_hash = hashlib.sha256(input_str.encode("utf-8")).hexdigest()

    final_output = {
        "scoring_version": "phase32_v1",
        "generated_at": datetime.now().isoformat() + "Z",
        "inputs_hash": input_hash,
        "items": scored_items
    }

    # 5. Save
    output_path.write_text(json.dumps(final_output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[Priority] Saved {len(scored_items)} scored proposals to {output_path}")

if __name__ == "__main__":
    main()
