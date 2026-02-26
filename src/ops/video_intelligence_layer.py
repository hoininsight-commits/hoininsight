#!/usr/bin/env python3
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

class VideoIntelligenceLayer:
    """
    [PHASE-18] Video Intelligence Layer (Independent)
    Selects high-value topics for video production without modifying core logic.
    """

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.logger = logging.getLogger("VideoIntelligenceLayer")
        self.ymd = datetime.now().strftime("%Y-%m-%d")
        
    def _load_json(self, path: Path) -> Any:
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding='utf-8'))
        except Exception as e:
            self.logger.error(f"Failed to load {path}: {e}")
            return {}

    def run(self):
        self.logger.info(f"Running Video Intelligence Layer for {self.ymd}...")

        # 1. Load Inputs
        narrative_path = self.base_dir / "data/ops/narrative_intelligence_v2.json"
        narrative_data = self._load_json(narrative_path)
        topics = narrative_data.get("topics", [])

        # Load why_now_type from interpretation_units or similar if available
        units_path = self.base_dir / "data/decision/interpretation_units.json"
        units = self._load_json(units_path)
        if not isinstance(units, list): units = []
        
        # Build mapping for why_now_type
        # We need to bridge STRUCT_ID -> Source ID -> Interpretation Unit
        seeds_path = self.base_dir / "data/ops/structural_topic_seeds_today.json"
        seeds_data = self._load_json(seeds_path)
        seeds = seeds_data.get("seeds", [])
        
        id_to_why_now = {}
        # Bridge: topic_seed_id -> source_refs[0].id
        seed_to_source = {s.get("topic_seed_id"): s.get("source_refs", [{}])[0].get("id") for s in seeds}
        
        # interpretation_id -> why_now_type
        unit_why_now = {u.get("interpretation_id"): u.get("why_now_type") for u in units}
        
        # Also check Anchor Result (Priority for Top-1 candidate)
        anchor_path = self.base_dir / f"data/topics/anchor/{self.ymd.replace('-', '/')}/anchor_result.json"
        anchor_data = self._load_json(anchor_path)
        anchor_why = anchor_data.get("why_now_type") if anchor_data else None
        anchor_axis = anchor_data.get("data_axis", []) if anchor_data else []

        # Composite mapping
        for topic_id, source_id in seed_to_source.items():
            # If it's the anchor axis, use anchor why_now_type
            is_anchor = any(axis in topic_id for axis in anchor_axis)
            if is_anchor and anchor_why:
                id_to_why_now[topic_id] = anchor_why
            elif source_id in unit_why_now:
                id_to_why_now[topic_id] = unit_why_now[source_id]
            else:
                # [PHASE-18] Inference Fallback:
                # If it's in the seeds, it has a why_now string, so it's not NONE.
                if "signal_f" in topic_id or "cand_" in topic_id:
                    id_to_why_now[topic_id] = "State-driven"
                else:
                    id_to_why_now[topic_id] = "Mechanism-driven"

        # 2. Filter Candidates
        candidates = []
        for t in topics:
            ns = float(t.get("narrative_score", 0))
            sas = float(t.get("structural_actor_score", 0))
            cam = float(t.get("cross_axis_multiplier", 1.0))
            dataset_id = t.get("dataset_id")
            topic_id = t.get("topic_id")
            
            # Use linked why_now_type or fallback
            why_now_type = id_to_why_now.get(topic_id)
            
            # Additional check: If this dataset is in anchor axes, use anchor_why
            if not why_now_type and dataset_id in anchor_axis:
                why_now_type = anchor_why
            
            # Final fallback: if intensity is high, it's likely state-driven
            if not why_now_type:
                intensity = float(t.get("intensity", 50.0))
                if intensity >= 80:
                    why_now_type = "Event-driven"
                else:
                    why_now_type = "NONE"

            # Condition:
            # - narrative_score >= 70
            # - structural_actor_score > 0
            # - cross_axis_multiplier > 1.0
            # - why_now_type != NONE
            
            if ns >= 70 and sas > 0 and cam > 1.0 and why_now_type != "NONE":
                # 3. Calculate Video Score (Emotional Impact)
                # video_score = (ns * 0.5) + (intensity * 0.3) + (20 if conflict else 0)
                intensity = float(t.get("intensity", 50.0))
                conflict = t.get("conflict_flag", False)
                
                v_score = (ns * 0.5) + (intensity * 0.3) + (20.0 if conflict else 0.0)
                
                candidates.append({
                    "title": t.get("title"),
                    "dataset_id": t.get("dataset_id"),
                    "intensity": intensity,
                    "narrative_score": ns,
                    "video_score": round(v_score, 2),
                    "why_now_type": why_now_type,
                    "structural_axes": t.get("_diag_axis_matches", [])
                })

        # 4. Sort and Save
        candidates.sort(key=lambda x: x["video_score"], reverse=True)
        top_3 = candidates[:3]

        output_path = self.base_dir / "data_outputs/ops/video_candidate_pool.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        output_data = {
            "run_date": self.ymd,
            "pool_size": len(candidates),
            "top_candidates": top_3,
            "schema_version": "v1.0"
        }
        
        output_path.write_text(json.dumps(output_data, indent=2, ensure_ascii=False), encoding='utf-8')
        self.logger.info(f"Generated video candidate pool with {len(candidates)} items. Top candidate score: {top_3[0]['video_score'] if top_3 else 0}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    VideoIntelligenceLayer(Path(".")).run()
