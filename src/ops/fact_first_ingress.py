from __future__ import annotations
import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

class FactFirstIngress:
    """
    Dedicated FACT-FIRST topic ingress layer.
    Early topic capture based on factual anchors (policy, flows, news).
    Status is always SHADOW.
    """
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.output_root = base_dir / "data" / "topics" / "shadow_pool"
        
    def _utc_ymd_path(self, target_date: Optional[str] = None) -> str:
        if target_date:
            return target_date.replace("-", "/")
        return datetime.now().strftime("%Y/%m/%d")

    def run_ingress(self, target_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Main execution loop for fact-first ingestion.
        """
        ymd_path = self._utc_ymd_path(target_date)
        raw_dir = self.base_dir / "data" / "raw"
        
        candidates = []
        
        # 1. Load from Policy
        policy_dir = raw_dir / "policy" / ymd_path
        if policy_dir.exists():
            for f in policy_dir.glob("*.json"):
                try:
                    data = json.loads(f.read_text(encoding="utf-8"))
                    items = data if isinstance(data, list) else [data]
                    for item in items:
                        cand = self._process_policy_item(item)
                        if cand: candidates.append(cand)
                except Exception: continue

        # [Step 60] Load from Operator Input (Fact-First Seed)
        op_input_file = self.base_dir / "data" / "ops" / "fact_first_input_today.json"
        if op_input_file.exists():
            try:
                op_data = json.loads(op_input_file.read_text(encoding="utf-8"))
                for fact in op_data.get("facts", []):
                    cand = self._process_operator_fact(fact)
                    if cand: candidates.append(cand)
                print(f"[FactIngress] Loaded {len(op_data.get('facts', []))} operator facts.")
            except Exception as e:
                print(f"[FactIngress] Operator input load error: {e}")

        # 2. Load from Flows (Institutional)
        flow_dir = raw_dir / "structural_capital" / ymd_path
        if flow_dir.exists():
            for f in flow_dir.glob("*.json"):
                try:
                    data = json.loads(f.read_text(encoding="utf-8"))
                    items = data if isinstance(data, list) else [data]
                    for item in items:
                        cand = self._process_flow_item(item)
                        if cand: candidates.append(cand)
                except Exception: continue

        # 3. Load from News/RSS (via Youtube or news collectors if available)
        # Note: placeholder for specialized news collectors if they exist in raw
        
        # [Step 48] 4. Load from Harvested Fact Anchors
        fact_file = self.base_dir / "data" / "facts" / f"fact_anchors_{ymd_path.replace('/', '')}.json"
        if fact_file.exists():
            try:
                facts_data = json.loads(fact_file.read_text(encoding="utf-8"))
                for fact in facts_data:
                    cand = self._process_harvested_fact(fact)
                    if cand: candidates.append(cand)
            except Exception: pass
        
        # [Step 49] Enrich with Structural Narrative Frames
        try:
            from src.ops.structural_narrative_mapper import StructuralNarrativeMapper
            mapper = StructuralNarrativeMapper(self.base_dir)
            candidates = mapper.enrich_facts(candidates)
        except Exception as e:
            print(f"[FactFirst] Mapper error: {e}")

        # filter to unique topics if needed (not strictly required by mission but good practice)
        final_topics = self._finalize_shadows(candidates)
        
        if final_topics:
            self._save_output(final_topics, ymd_path)
            
        return final_topics

    def _process_policy_item(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Rule: At least one factual anchor + structural implication.
        """
        anchor = item.get("title") or item.get("key_sentence") or item.get("summary")
        if not anchor: return None
        
        # Simple extraction for mission demonstration
        # In production, this might use LLM with the "Strict Rule" prompt
        structural_reason = f"If this policy persists, {item.get('impact_area', 'the target structure')} changes."
        
        # Constraint: Shadow only, no scoring
        return {
            "topic_type": "FACT_FIRST",
            "status": "SHADOW",
            "fact_anchor": anchor,
            "structural_reason": structural_reason,
            "why_now_hint": f"New official document: {item.get('source_id', 'policy')}",
            "confidence": "MEDIUM" if item.get("trust_score", 0) > 0.7 else "LOW",
            "source_refs": [f"policy:{item.get('id', 'unknown')}"]
        }

    def _process_flow_item(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        metric = item.get("dataset_id")
        val = item.get("value")
        if not metric or val is None: return None
        
        # Rule check: number/flow statement anchor exists
        structural_reason = f"If this flow level {val} persists, liquidity structure for {metric} shifts."
        
        return {
            "topic_type": "FACT_FIRST",
            "status": "SHADOW",
            "fact_anchor": f"Historical flow reading: {val} for {metric}",
            "structural_reason": structural_reason,
            "why_now_hint": f"Raw data ingestion trigger for {metric}",
            "confidence": "LOW",
            "source_refs": [f"raw:{metric}"]
        }

    def _process_harvested_fact(self, fact: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        metric = fact.get("fact_id")
        text = fact.get("fact_text")
        if not text: return None
        
        # Rule check: At least one factual anchor exists
        # One-sentence structural implication (Mocking for mission)
        st_reason = f"Structural implication: '{text}' suggests a shift in {fact.get('fact_type')} dynamics."
        
        return {
            "topic_type": "FACT_FIRST",
            "status": "SHADOW",
            "fact_anchor": text,
            "structural_reason": st_reason,
            "why_now_hint": f"Harvested fact from {fact.get('source')}",
            "confidence": "LOW", # Harvested facts start as LOW
            "source_refs": [f"fact:{fact.get('fact_id')}"]
        }

    def _process_operator_fact(self, fact: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Convert operator fact to candidate seed.
        Schema: fact, subject, object, type, source, confidence
        """
        anchor = fact.get("fact")
        if not anchor: return None
        
        # Structure logic: TYPE + Subject -> Object
        st_reason = f"[{fact.get('type')}] {fact.get('subject')} -> {fact.get('object')} shift detected."
        
        return {
            "topic_type": "FACT_FIRST",
            "status": "SHADOW",
            "fact_anchor": anchor,
            "structural_reason": st_reason,
            "why_now_hint": f"Operator Seed: {fact.get('source')}",
            "confidence": fact.get("confidence", "MEDIUM"), 
            "source_refs": [f"op:{fact.get('fact_id')}"],
            # Pass through extra metadata if needed
            "metadata": fact
        }

    def _finalize_shadows(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # For MISSION: remove duplicates and ensure strict SHADOW status
        seen = set()
        final = []
        for c in candidates:
            if c["fact_anchor"] not in seen:
                final.append(c)
                seen.add(c["fact_anchor"])
        return final

    def _save_output(self, topics: List[Dict[str, Any]], ymd_path: str):
        # [Step 50] Build Topic Seeds before saving
        try:
            from src.ops.topic_seed_builder import TopicSeedBuilder
            builder = TopicSeedBuilder(self.base_dir)
            seeds = builder.build_seeds(topics)
            
            # [Step 51] Build Narrative Hypotheses
            from src.ops.narrative_hypothesis_builder import NarrativeHypothesisBuilder
            hyp_builder = NarrativeHypothesisBuilder(self.base_dir)
            hypotheses = hyp_builder.build_hypotheses(seeds)
        except Exception as e:
            print(f"[FactFirst] Seed/Hypo error: {e}")
            seeds = []
            hypotheses = []

        out_dir = self.output_root / ymd_path
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / "fact_first.json"
        
        payload = {
            "run_ts": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "topics": topics,
            "topic_seeds": seeds,
            "narrative_hypotheses": hypotheses
        }
        
        out_file.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"[FactFirst] Saved {len(topics)} shadow topics and {len(seeds)} seeds to {out_file}")

if __name__ == "__main__":
    # Test run
    ing = FactFirstIngress(Path("."))
    ing.run_ingress()
