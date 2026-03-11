import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List

class RelationshipStressCollector:
    """
    IS-96-8: Relationship Stress Layer Collector
    Deterministic extraction of partnership stress signals.
    """

    def __init__(self, base_dir: Path = Path(".")):
        self.base_dir = base_dir
        self.output_path = self.base_dir / "data" / "decision" / "relationship_stress.json"
        
        # Input paths
        self.catalyst_path = self.base_dir / "data" / "ops" / "catalyst_events.json"
        self.evidence_path = self.base_dir / "data" / "decision" / "evidence_citations.json"
        self.manual_path = self.base_dir / "data" / "ops" / "manual_relationship_events.yml"
        self.registry_path = self.base_dir / "registry" / "sources" / "source_registry_v1.yml"

    def _load_json(self, path: Path) -> List:
        if not path.exists():
            return []
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except:
            return []

    def _load_yaml(self, path: Path) -> Any:
        if not path.exists():
            return []
        try:
            return yaml.safe_load(path.read_text(encoding="utf-8"))
        except:
            return []

    def collect(self) -> Dict[str, Any]:
        """
        Gathers signals and computes stress scores.
        """
        catalyst_events = self._load_json(self.catalyst_path)
        manual_events = self._load_yaml(self.manual_path)
        source_registry = self._load_yaml(self.registry_path)
        
        # Map source_id to reliability
        registry_map = {}
        if isinstance(source_registry, dict) and "sources" in source_registry:
            for s in source_registry["sources"]:
                registry_map[s.get("id")] = s.get("reliability", 0.5)

        relationships = {} # Keys: (entity_a, entity_b) sorted tuple

        # 1. Process Manual Events
        if isinstance(manual_events, list):
            for me in manual_events:
                key = tuple(sorted([me["entity_a"], me["entity_b"]]))
                if key not in relationships:
                    relationships[key] = self._init_rel(me["entity_a"], me["entity_b"])
                
                rel = relationships[key]
                rel["relationship_type"] = me.get("relationship_type", rel["relationship_type"])
                rel["evidence"].append({
                    "source_id": "manual",
                    "kind": "manual_seed",
                    "title": "Manual Signal",
                    "reliability": me.get("reliability", 1.0),
                    "date": me.get("date", datetime.now().strftime("%Y-%m-%d"))
                })
                
                signals = me.get("signals", {})
                for s_key in rel["signals"]:
                    if signals.get(s_key):
                        rel["signals"][s_key]["present"] = True
                
                rel["why_now"].extend(me.get("why_now", []))

        # 2. Process Catalyst Events
        # Rules: If catalyst contains {company_a, company_b} and keywords like "investment cut", 
        # "talks stalled", "re-evaluation", "switch supplier"
        STRESS_KEYWORDS = ["investment cut", "talks stalled", "re-evaluation", "switch supplier", "conflict", "breakup", "reprice", "talks", "stalled"]
        
        for e in catalyst_events:
            entities = e.get("entities", [])
            if len(entities) >= 2:
                # Simple O(n^2) for small lists of entities
                for i in range(len(entities)):
                    for j in range(i + 1, len(entities)):
                        ent_a = entities[i]
                        ent_b = entities[j]
                        
                        title = e.get("title", "").lower()
                        if any(k in title for k in STRESS_KEYWORDS):
                            key = tuple(sorted([ent_a, ent_b]))
                            if key not in relationships:
                                relationships[key] = self._init_rel(ent_a, ent_b)
                            
                            rel = relationships[key]
                            rel["evidence"].append({
                                "source_id": e.get("source_id", "unknown"),
                                "kind": "catalyst",
                                "title": e.get("title", ""),
                                "reliability": registry_map.get(e.get("source_id"), 0.5),
                                "date": e.get("as_of_date", "")
                            })
                            
                            # Simple heuristic for signals
                            if "reprice" in title or "cost" in title: rel["signals"]["deal_reprice"]["present"] = True
                            if "statement" in title or "diverge" in title or "talks" in title: rel["signals"]["statement_divergence"]["present"] = True
                            if "investment" in title or "capital" in title: rel["signals"]["capital_link"]["present"] = True
                            if "supplier" in title or "supply" in title: rel["signals"]["supply_dependency"]["present"] = True

                            rel["why_now"].append(e.get("title"))

        # 3. Final Scoring and Thresholding
        final_list = []
        for key, rel in relationships.items():
            # Deduplicate why_now
            rel["why_now"] = list(dict.fromkeys(rel["why_now"]))
            
            # stress_score = weighted sum: 
            # deal_reprice(0.35) + statement_divergence(0.25) + capital_link_change(0.20) + supply_dependency(0.20)
            score = 0.0
            if rel["signals"]["deal_reprice"]["present"]: score += 0.35
            if rel["signals"]["statement_divergence"]["present"]: score += 0.25
            if rel["signals"]["capital_link"]["present"]: score += 0.20
            if rel["signals"]["supply_dependency"]["present"]: score += 0.20
            
            rel["stress_score"] = round(score, 2)
            
            # break_risk:
            # HIGH if stress_score >= 0.75 and evidence_count>=2 and avg_reliability>=0.7
            # MED if stress_score >= 0.55
            # else LOW
            ev_count = len(rel["evidence"])
            avg_rel = sum(e["reliability"] for e in rel["evidence"]) / ev_count if ev_count > 0 else 0
            
            if rel["stress_score"] >= 0.75 and ev_count >= 2 and avg_rel >= 0.7:
                rel["break_risk"] = "HIGH"
            elif rel["stress_score"] >= 0.55:
                rel["break_risk"] = "MED"
            else:
                rel["break_risk"] = "LOW"

            final_list.append(rel)

        output = {
            "as_of": datetime.now().strftime("%Y-%m-%d"),
            "relationships": final_list
        }
        
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
            
        print(f"[REL_STRESS] Generated {len(final_list)} relationships in {self.output_path}")
        return output

    def _init_rel(self, a, b) -> Dict:
        return {
            "entity_a": a,
            "entity_b": b,
            "relationship_type": "strategic_partner", # Default
            "evidence": [],
            "signals": {
                "capital_link": {"present": False, "amount_usd": None},
                "supply_dependency": {"present": False, "note": ""},
                "statement_divergence": {"present": False, "note": ""},
                "deal_reprice": {"present": False, "note": ""}
            },
            "stress_score": 0.0,
            "break_risk": "LOW",
            "why_now": [],
            "risk_notes": []
        }

if __name__ == "__main__":
    collector = RelationshipStressCollector()
    collector.collect()
