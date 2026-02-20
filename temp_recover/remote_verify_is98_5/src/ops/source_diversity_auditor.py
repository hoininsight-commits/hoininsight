import json
from pathlib import Path
from typing import List, Dict, Any
from src.ops.diversity_enforcer import DiversityEnforcer

class SourceDiversityAuditor:
    """
    IS-32: SOURCE_DIVERSITY_AUDITOR
    Orchestrates the diversity checks and multi-source audit logging.
    """

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.enforcer = DiversityEnforcer()

    def audit_topics(self, topics: List[Dict[str, Any]], events_index: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Input: List of topic dicts.
        Output: Enriched topics with diversity metrics and demotion applied.
        """
        audit_log = []

        for topic in topics:
            # Gather all evidence sources for this topic
            sources = self._gather_sources(topic, events_index)
            
            # Enforce diversity
            res = self.enforcer.enforce(sources)
            
            # Enrich topic
            topic["source_clusters_count"] = res["clusters_count"]
            topic["source_families_list"] = res["families_list"]
            topic["diversity_verdict"] = res["verdict"]
            topic["diversity_reason_code"] = res["reason_code"]
            
            # Apply demotion logic
            if res["verdict"] != "PASS":
                topic["is_diversity_demoted"] = True
                if topic.get("status") == "READY":
                    topic["status"] = "HOLD"
                    topic["demotion_reason"] = f"LACK_SOURCE_DIVERSITY ({res['reason_code']})"

            # Add to audit log
            audit_log.append({
                "topic_id": topic.get("topic_id"),
                "verdict": res["verdict"],
                "reason": res["reason_code"],
                "clusters": res["clusters_count"],
                "families": res["families_list"],
                "evidence_count": len(sources)
            })

        # Save Audit Log
        self._save_audit_log(audit_log)
        
        return topics

    def _gather_sources(self, topic: Dict[str, Any], events_index: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Collects raw sources from the events index based on candidate IDs."""
        sources = []
        source_ids = topic.get("source_candidates", []) or [topic.get("candidate_id")]
        for sid in source_ids:
            if sid in events_index:
                evt = events_index[sid]
                # If event has its own source list, use it. Otherwise use the event itself.
                if "sources" in evt and isinstance(evt["sources"], list):
                    sources.extend(evt["sources"])
                else:
                    sources.append(evt)
        return sources

    def _save_audit_log(self, audit_log: List[Dict[str, Any]]):
        audit_dir = self.base_dir / "data" / "ops" / "issuesignal"
        audit_dir.mkdir(parents=True, exist_ok=True)
        audit_file = audit_dir / "source_audit.json"
        
        # Standardize for daily run (append or overwrite today's)
        # For now, overwrite latest
        audit_file.write_text(json.dumps(audit_log, indent=2, ensure_ascii=False), encoding="utf-8")
