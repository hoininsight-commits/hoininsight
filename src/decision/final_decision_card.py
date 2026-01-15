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

    # 3. Construct Final Card
    card = {
        "card_version": "phase38_v1",
        "generated_at": now_utc.isoformat() + "Z",
        "date": ymd_dash,
        "blocks": {
            "regime": regime_block,
            "revival": revival_block,
            "ops": ops_block
        },
        "human_prompt": "현재 Regime 및 데이터 상태를 고려할 때, 이 주제를 오늘 다룰 가치가 있다고 판단하십니까?"
    }

    # 4. Save
    output_dir = base_dir / "data/decision" / ymd_path
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "final_decision_card.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(card, f, indent=2, ensure_ascii=False)

    print(f"✓ Final Decision Card generated: {output_file}")
    print(f"  - Regime: {regime_block['current_regime']} (Conf: {regime_block['confidence']})")
    print(f"  - Revival: {revival_block['proposal_count']} props")
    print(f"  - Ops: {ops_block['system_freshness']}% freshness")

if __name__ == "__main__":
    main()
