#!/usr/bin/env python3
"""
Phase 38: Final Decision Card Generator
Aggregates Regime, Revival, and Ops context into a single structured card for human decision making.
"""
import json
import sys
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

def main():
    base_dir = Path(__file__).resolve().parent.parent.parent
    now_utc = datetime.now(timezone.utc)
    ymd_path = now_utc.strftime("%Y/%m/%d")
    ymd_dash = now_utc.strftime("%Y-%m-%d")
    
    # 1. Load Data Sources
    # Regime
    regime_path = base_dir / f"data/regimes/regime_{ymd_dash}.json"
    regime_data = load_json(regime_path) or {}
    
    meta_path = base_dir / "data/meta_topics" / ymd_path / "meta_topics.json"
    meta_topics = load_json(meta_path) or []
    
    # Revival
    rev_base = base_dir / "data/narratives/revival" / ymd_path
    revival_proposals = load_json(rev_base / "revival_proposals.json") or {}
    revival_evidence = load_json(rev_base / "revival_evidence.json") or {}
    revival_loops = load_json(rev_base / "revival_loop_flags.json") or {}
    
    # Ops
    fresh_path = base_dir / "data/ops/freshness" / ymd_path / "freshness_summary.json"
    fresh_data = load_json(fresh_path) or {}
    
    score_path = base_dir / "data/ops/scoreboard" / ymd_path / "ops_scoreboard.json"
    ops_scoreboard = load_json(score_path) or {}

    # Candidates (Phase 39 Output)
    cand_path = base_dir / "data/topics/candidates" / ymd_path / "topic_candidates.json"
    candidates_data = load_json(cand_path)
    candidates = candidates_data.get("candidates", []) if candidates_data else []

    # 2. Build Blocks
    
    # Regime Block
    regime_block = {
        "current_regime": regime_data.get("regime", "Unknown"),
        "confidence": regime_data.get("confidence", 0.0),
        "has_meta_topics": len(meta_topics) > 0,
        "meta_topic_count": len(meta_topics),
        "basis_type": regime_data.get("basis_type", "NONE")
    }

    # Revival Block
    rev_items = revival_proposals.get("items", [])
    revival_block = {
        "proposal_count": len(rev_items),
        "has_revival": len(rev_items) > 0,
        "loop_warning_count": len(revival_loops.get("loop_detected_vids", [])),
        "primary_revival_reason": revival_proposals.get("condition_met", "N/A") if rev_items else "N/A"
    }

    # Ops Block
    ops_block = {
        "system_freshness": fresh_data.get("overall_system_freshness_pct", 0),
        "sla_breach_count": fresh_data.get("sla_breach_count", 0),
        "has_stale_warning": fresh_data.get("sla_breach_count", 0) > 0,
        "7d_success_rate": f"{ops_scoreboard.get('success_count', 0)}/7" if ops_scoreboard else "N/A"
    }

    # 3. Topic Selection Logic (Daily Top 5)
    selected_topic_title = None
    selected_rationale = None
    key_data = {}
    top_topics = []

    if candidates:
        scored_candidates = []
        
        for cand in candidates:
            ds_id = cand["dataset_id"]
            topic_file = base_dir / "data/topics" / ymd_path / f"{ds_id}.json"
            t_data_raw = load_json(topic_file)
            
            if t_data_raw:
                # Handle List structure
                t_obj = t_data_raw[0] if isinstance(t_data_raw, list) and len(t_data_raw) > 0 else t_data_raw
                if not isinstance(t_obj, dict): continue

                # Determine level value
                lvl = t_obj.get("anomaly_level")
                if not lvl and "evidence" in t_obj:
                    lvl = t_obj["evidence"].get("level")
                lvl = lvl or "L1"
                
                lvl_val = 1
                if lvl == "L4": lvl_val = 4
                elif lvl == "L3": lvl_val = 3
                elif lvl == "L2": lvl_val = 2
                
                # Tie-breaker: Structural > Real Estate > Others directly in score
                if "struct" in ds_id or "real_estate" in ds_id:
                    lvl_val += 0.5
                
                # Extract Title/Rationale for display
                t_title = t_obj.get("key_conception") or t_obj.get("topic") or t_obj.get("title") or "Topic Detected"
                t_rationale = t_obj.get("why_now") or t_obj.get("rationale") or "No rationale."
                
                scored_candidates.append({
                    "dataset_id": ds_id,
                    "level": lvl,
                    "score": lvl_val,
                    "title": t_title,
                    "rationale": t_rationale,
                    "raw_data": t_obj
                })
        
        # Sort by Score Descending
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        
        # Select Top 5
        top_topics = scored_candidates[:5]
        
        # Set Main Topic
        if top_topics:
            best = top_topics[0]
            selected_topic_title = best["title"]
            selected_rationale = best["rationale"]
            key_data[best["dataset_id"]] = "Primary"
            
            # Add secondary badges
            for other in top_topics[1:]:
                key_data[other["dataset_id"]] = "Secondary"

    # Fallback if no candidates but maybe Revival exists? 
    # (Existing logic didn't handle this, but adding minimal fallback)
    if not selected_topic_title and revival_block["has_revival"]:
        selected_topic_title = "Narrative Revival"
        selected_rationale = "Past narratives have resurfaced based on recent signals."

    # 4. Construct Final Card
    card = {
        "card_version": "phase38_v1",
        "generated_at": now_utc.isoformat() + "Z",
        "date": ymd_dash,
        "blocks": {
            "regime": regime_block,
            "revival": revival_block,
            "ops": ops_block
        },
        "topic": selected_topic_title,               # Main Topic
        "decision_rationale": selected_rationale,    # Main Rationale
        "key_data": key_data,
        "top_topics": top_topics,                    # Full Top 5 List
        "human_prompt": "현재 Regime 및 데이터 상태를 고려할 때, 이 주제를 오늘 다룰 가치가 있다고 판단하십니까?"
    }

    # 4. Save
    output_dir = base_dir / "data/decision" / ymd_path
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "final_decision_card.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(card, f, indent=2, ensure_ascii=False)

    print(f"✓ Final Decision Card generated: {output_file}")
    print(f"  - Topic: {selected_topic_title}")
    print(f"  - Rationale: {selected_rationale}")
    print(f"  - Regime: {regime_block['current_regime']} (Conf: {regime_block['confidence']})")
    print(f"  - Revival: {revival_block['proposal_count']} props")
    print(f"  - Ops: {ops_block['system_freshness']}% freshness")

if __name__ == "__main__":
    main()
