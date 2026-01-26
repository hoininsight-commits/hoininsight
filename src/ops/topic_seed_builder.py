from __future__ import annotations
import json
import uuid
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Set

class TopicSeedBuilder:
    """
    Clusters framed FACTs into TOPIC SEEDS based on shared structural logic.
    Deterministic clustering (frame + entities + window).
    """

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.output_path = base_dir / "data" / "ops" / "topic_seeds.json"
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

    def build_seeds(self, enriched_facts: List[Dict[str, Any]], lookback_days: int = 14) -> List[Dict[str, Any]]:
        """
        Clusters facts into seeds. 
        In production, this would also load previous seeds to find incremental matches.
        For this step, we cluster the provided batch.
        """
        if not enriched_facts:
            return []

        # 1. Group facts by structural frames
        # We use a greedy clustering approach:
        # A cluster is defined by (Frame Set, Entity Set, Date Range)
        
        seeds: List[Dict[str, Any]] = []
        fact_pool = list(enriched_facts)
        
        while fact_pool:
            base_fact = fact_pool.pop(0)
            base_frames = {f["frame"] for f in base_fact.get("structural_frames", [])}
            base_entities = set(base_fact.get("entities", []))
            base_date_raw = base_fact.get("published_at") or datetime.now().strftime("%Y-%m-%d")
            try:
                base_date = datetime.strptime(base_date_raw, "%Y-%m-%d")
            except:
                base_date = datetime.now()
            
            cluster_members = [base_fact]
            remaining_pool = []
            
            for f in fact_pool:
                f_frames = {fr["frame"] for fr in f.get("structural_frames", [])}
                f_entities = set(f.get("entities", []))
                f_date_raw = f.get("published_at") or datetime.now().strftime("%Y-%m-%d")
                try:
                    f_date = datetime.strptime(f_date_raw, "%Y-%m-%d")
                except:
                    f_date = datetime.now()
                
                # Clustering Rules:
                # 1. Share at least one frame
                # 2. Entity overlap OR same domain (simplification: entity overlap)
                # 3. Within time window
                
                shared_frames = base_frames.intersection(f_frames)
                shared_entities = base_entities.intersection(f_entities)
                days_diff = abs((base_date - f_date).days)
                
                if shared_frames and (shared_entities or not base_entities or not f_entities) and days_diff <= lookback_days:
                    cluster_members.append(f)
                else:
                    remaining_pool.append(f)
            
            # Form a seed if we have members
            seed = self._create_seed(cluster_members)
            seeds.append(seed)
            fact_pool = remaining_pool
            
        self._save_seeds(seeds)
        return seeds

    def _create_seed(self, members: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Creates a single Topic Seed from a cluster of members.
        """
        # Aggregate frames
        all_frames = set()
        for m in members:
            for f in m.get("structural_frames", []):
                all_frames.add(f["frame"])
        
        # Aggregate fact IDs
        fact_ids = [m["fact_id"] for m in members]
        
        # Determine first_seen
        parsed_dates = []
        for m in members:
            d_raw = m.get("published_at")
            if d_raw:
                try:
                    parsed_dates.append(datetime.strptime(d_raw, "%Y-%m-%d"))
                except: pass
        
        if not parsed_dates:
            first_seen = datetime.now().strftime("%Y-%m-%d")
        else:
            first_seen = min(parsed_dates).strftime("%Y-%m-%d")
        
        # Generate Seed Summary (Neutral)
        # One-sentence neutral structural description
        entities = set()
        for m in members:
            for e in m.get("entities", []):
                entities.add(e)
        
        frames_str = " & ".join(sorted(list(all_frames)))
        entities_str = ", ".join(sorted(list(entities)))
        
        summary = f"Clustered facts regarding {entities_str} indicate {frames_str} structural alignment."
        if not entities:
            summary = f"Identified {frames_str} alignment across multiple factual anchors."

        return {
            "seed_id": f"seed_{uuid.uuid4().hex[:8]}",
            "structural_frames": sorted(list(all_frames)),
            "supporting_facts": fact_ids,
            "seed_summary": summary,
            "first_seen": first_seen,
            "status": "SHADOW_ONLY"
        }

    def _save_seeds(self, seeds: List[Dict[str, Any]]):
        # In a real system, we'd merge with src/data/ops/topic_seeds.json
        # For simplicity, we write or overwrite today's output
        self.output_path.write_text(json.dumps(seeds, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"[SeedBuilder] Generated {len(seeds)} Topic Seeds to {self.output_path}")

if __name__ == "__main__":
    # Smoke test
    builder = TopicSeedBuilder(Path("."))
    facts = [
        {
            "fact_id": "f1",
            "fact_type": "TECH",
            "fact_text": "Nvidia confirms AI delivery",
            "entities": ["Nvidia", "AI"],
            "published_at": "2026-01-26",
            "structural_frames": [{"frame": "TECH_INFLECTION", "reason": "..."}]
        },
        {
            "fact_id": "f2",
            "fact_type": "BUDGET",
            "fact_text": "US chip funding increased",
            "entities": ["AI", "Semiconductors"],
            "published_at": "2026-01-26",
            "structural_frames": [{"frame": "TECH_INFLECTION", "reason": "..."}]
        }
    ]
    builder.build_seeds(facts)
